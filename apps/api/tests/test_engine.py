import json
import shutil
from pathlib import Path

import pytest

from devlens.db.models.analytics import Message, Session, ToolUsage, TrackedFile
from devlens.db.models.project import Project
from devlens.ingestion.engine import SyncEngine
from devlens.providers.base import BaseProvider, RawSession


class FakeProvider(BaseProvider):
    """Minimal provider that serves a single temp JSONL file for testing."""

    provider_name = "test"

    def __init__(self, files: list[Path]):
        self._files = files

    def is_available(self) -> bool:
        return True

    def discover_sessions(self):
        for f in self._files:
            yield RawSession(
                file_path=f,
                session_id=f.stem,
                project_slug="test-project",
                project_path="/home/user/test-project",
            )


FIXTURE = Path(__file__).parent / "fixtures" / "sample_session.jsonl"


def _make_engine(db_session, files: list[Path]) -> SyncEngine:
    engine = SyncEngine(db_session)
    engine._providers = [FakeProvider(files)]
    # Monkey-patch PROVIDERS at module level for this engine instance
    engine.__class__._get_providers = lambda self: [FakeProvider(files)]
    return engine


def _run_with_provider(db_session, provider: FakeProvider) -> dict:
    from devlens.ingestion import engine as engine_module

    original = engine_module.PROVIDERS
    engine_module.PROVIDERS = [provider]
    try:
        eng = SyncEngine(db_session)
        return eng.run()
    finally:
        engine_module.PROVIDERS = original


def test_sync_creates_session_and_messages(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    stats = _run_with_provider(db_session, FakeProvider([f]))

    assert stats["files_processed"] == 1
    assert stats["sessions_upserted"] == 1

    session = db_session.query(Session).filter_by(session_id="abc123def456").first()
    assert session is not None
    assert session.message_count == 10
    assert session.model is not None

    messages = db_session.query(Message).filter_by(session_id=session.id).all()
    assert len(messages) == 10


def test_sync_creates_tool_usages(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    _run_with_provider(db_session, FakeProvider([f]))

    session = db_session.query(Session).filter_by(session_id="abc123def456").first()
    tool_usages = db_session.query(ToolUsage).filter_by(session_id=session.id).all()
    tool_names = {t.tool_name for t in tool_usages}

    assert "Read" in tool_names
    assert "Write" in tool_names
    assert "Bash" in tool_names
    assert "Edit" in tool_names


def test_sync_records_tool_errors(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    _run_with_provider(db_session, FakeProvider([f]))

    session = db_session.query(Session).filter_by(session_id="abc123def456").first()
    tool_usages = db_session.query(ToolUsage).filter_by(session_id=session.id).all()
    bash = next((t for t in tool_usages if t.tool_name == "Bash"), None)

    assert bash is not None
    assert bash.is_error_count == 1


def test_sync_checksum_cache_skips_unchanged(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    stats1 = _run_with_provider(db_session, FakeProvider([f]))
    assert stats1["files_processed"] == 1

    # Second run — same file, same checksum → skip
    stats2 = _run_with_provider(db_session, FakeProvider([f]))
    assert stats2["files_checked"] == 1
    assert stats2["files_processed"] == 0


def test_sync_reprocesses_on_file_change(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    _run_with_provider(db_session, FakeProvider([f]))

    # Append a new line to change the checksum
    new_entry = {
        "type": "user",
        "message": {"role": "user", "content": "new message"},
        "timestamp": "2026-06-20T09:01:00.000Z",
        "uuid": "msg-new",
        "sessionId": "abc123def456",
    }
    with open(f, "a") as fh:
        fh.write(json.dumps(new_entry) + "\n")

    stats2 = _run_with_provider(db_session, FakeProvider([f]))
    assert stats2["files_processed"] == 1

    session = db_session.query(Session).filter_by(session_id="abc123def456").first()
    assert session.message_count == 11  # 10 original + 1 new


def test_sync_full_reprocess_replaces_messages(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    _run_with_provider(db_session, FakeProvider([f]))

    session = db_session.query(Session).filter_by(session_id="abc123def456").first()
    initial_count = db_session.query(Message).filter_by(session_id=session.id).count()
    assert initial_count == 10

    # Change file → reprocess should delete old messages and reinsert
    new_entry = {
        "type": "user",
        "message": {"role": "user", "content": "another message"},
        "timestamp": "2026-06-20T09:02:00.000Z",
        "uuid": "msg-extra",
        "sessionId": "abc123def456",
    }
    with open(f, "a") as fh:
        fh.write(json.dumps(new_entry) + "\n")

    _run_with_provider(db_session, FakeProvider([f]))

    final_count = db_session.query(Message).filter_by(session_id=session.id).count()
    assert final_count == 11  # no duplicates


def test_sync_creates_project(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    _run_with_provider(db_session, FakeProvider([f]))

    project = db_session.query(Project).filter_by(slug="test-project").first()
    assert project is not None
    assert project.name == "test-project"


def test_sync_multiple_files(db_session, tmp_path):
    f1 = tmp_path / "session-aaa.jsonl"
    f2 = tmp_path / "session-bbb.jsonl"
    shutil.copy(FIXTURE, f1)
    shutil.copy(FIXTURE, f2)

    stats = _run_with_provider(db_session, FakeProvider([f1, f2]))
    assert stats["files_processed"] == 2
    assert db_session.query(Session).count() == 2


def test_sync_tracked_file_updated(db_session, tmp_path):
    f = tmp_path / "abc123def456.jsonl"
    shutil.copy(FIXTURE, f)

    _run_with_provider(db_session, FakeProvider([f]))

    tracked = db_session.query(TrackedFile).filter_by(path=str(f)).first()
    assert tracked is not None
    assert tracked.checksum is not None
    assert tracked.last_processed is not None
