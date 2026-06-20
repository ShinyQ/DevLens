from collections import Counter
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session as DBSession

from devlens.db.models.analytics import Message, Session, ToolUsage, TrackedFile
from devlens.db.models.project import Project
from devlens.ingestion.aggregator import rebuild_daily_aggregates
from devlens.ingestion.parser import ParsedSession, ParsedMessage, parse_jsonl_file
from devlens.providers.base import BaseProvider
from devlens.providers.claude import ClaudeProvider
from devlens.providers.copilot import CopilotProvider

PROVIDERS: list[BaseProvider] = [ClaudeProvider(), CopilotProvider()]


class SyncEngine:
    def __init__(self, db: DBSession):
        self.db = db

    def run(self) -> dict[str, Any]:
        stats: dict[str, Any] = {
            "files_checked": 0,
            "files_processed": 0,
            "sessions_upserted": 0,
            "providers": [],
        }

        for provider in PROVIDERS:
            if not provider.is_available():
                continue

            provider_stats = {"name": provider.provider_name, "processed": 0}

            for raw in provider.discover_sessions():
                stats["files_checked"] += 1

                try:
                    checksum = provider.file_checksum(raw.file_path)
                except OSError:
                    continue

                tracked = (
                    self.db.query(TrackedFile)
                    .filter_by(path=str(raw.file_path))
                    .first()
                )

                if tracked and tracked.checksum == checksum:
                    continue

                parsed = parse_jsonl_file(
                    raw.file_path,
                    raw.session_id,
                    raw.project_slug,
                    raw.project_path,
                    provider.provider_name,
                )

                self._upsert_session(parsed)

                if not tracked:
                    tracked = TrackedFile(path=str(raw.file_path))
                    self.db.add(tracked)

                try:
                    stat = raw.file_path.stat()
                    tracked.last_modified = stat.st_mtime
                except OSError:
                    pass

                tracked.checksum = checksum
                tracked.last_processed = datetime.now(timezone.utc).replace(tzinfo=None)

                stats["files_processed"] += 1
                stats["sessions_upserted"] += 1
                provider_stats["processed"] += 1

            stats["providers"].append(provider_stats)

        self.db.commit()
        rebuild_daily_aggregates(self.db)
        self.db.commit()
        return stats

    def _upsert_session(self, parsed: ParsedSession) -> None:
        project = self.db.query(Project).filter_by(slug=parsed.project_slug).first()
        if not project:
            project = Project(
                name=parsed.project_slug,
                slug=parsed.project_slug,
                path=parsed.project_path,
            )
            self.db.add(project)
            self.db.flush()
        elif parsed.project_path and not project.path:
            project.path = parsed.project_path

        session = self.db.query(Session).filter_by(session_id=parsed.session_id).first()
        if not session:
            session = Session(
                session_id=parsed.session_id,
                provider=parsed.provider,
                project_id=project.id,
            )
            self.db.add(session)
            self.db.flush()

        # Full reprocess: delete existing message and tool data
        self.db.query(Message).filter_by(session_id=session.id).delete()
        self.db.query(ToolUsage).filter_by(session_id=session.id).delete()

        tool_counts: dict[str, dict[str, int]] = {}
        timestamps = []
        total_input = total_output = 0
        models: list[str] = []

        # Track tool_use_id → tool_name for error attribution
        tool_id_to_name: dict[str, str] = {}

        for parsed_msg in parsed.messages:
            if parsed_msg.timestamp:
                timestamps.append(parsed_msg.timestamp)

            db_msg = Message(
                session_id=session.id,
                role=parsed_msg.role,
                content_summary=parsed_msg.content_summary or None,
                input_tokens=parsed_msg.input_tokens,
                output_tokens=parsed_msg.output_tokens,
                cache_creation_tokens=parsed_msg.cache_creation_tokens,
                cache_read_tokens=parsed_msg.cache_read_tokens,
                model=parsed_msg.model,
                timestamp=parsed_msg.timestamp,
            )
            self.db.add(db_msg)

            total_input += parsed_msg.input_tokens
            total_output += parsed_msg.output_tokens

            if parsed_msg.model:
                models.append(parsed_msg.model)

            for tool_name in parsed_msg.tool_calls:
                if tool_name not in tool_counts:
                    tool_counts[tool_name] = {"exec": 0, "err": 0}
                tool_counts[tool_name]["exec"] += 1

            # Attribute errors back to originating tools
            for tool_use_id in parsed_msg.tool_error_ids:
                err_tool = tool_id_to_name.get(tool_use_id)
                if err_tool and err_tool in tool_counts:
                    tool_counts[err_tool]["err"] += 1

        for tool_name, counts in tool_counts.items():
            self.db.add(
                ToolUsage(
                    session_id=session.id,
                    tool_name=tool_name,
                    execution_count=counts["exec"],
                    is_error_count=counts["err"],
                )
            )

        # Update session summary
        session.message_count = len(parsed.messages)
        session.tool_call_count = sum(v["exec"] for v in tool_counts.values())
        session.total_input_tokens = total_input
        session.total_output_tokens = total_output
        session.has_compaction = parsed.has_compaction

        if models:
            counter = Counter(models)
            session.model = counter.most_common(1)[0][0]

        if timestamps:
            session.started_at = min(timestamps)
            session.ended_at = max(timestamps)
