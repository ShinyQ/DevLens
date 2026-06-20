import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class ParsedMessage:
    role: str
    timestamp: Optional[datetime]
    model: Optional[str]
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    content_summary: str = ""
    tool_calls: list[str] = field(default_factory=list)
    tool_error_ids: list[str] = field(default_factory=list)


@dataclass
class ParsedSession:
    session_id: str
    project_slug: str
    project_path: str
    provider: str
    messages: list[ParsedMessage] = field(default_factory=list)
    has_compaction: bool = False


def parse_jsonl_file(
    path: Path,
    session_id: str,
    project_slug: str,
    project_path: str,
    provider: str,
) -> ParsedSession:
    result = ParsedSession(
        session_id=session_id,
        project_slug=project_slug,
        project_path=project_path,
        provider=provider,
    )

    # Maps tool_use_id → tool_name for error attribution
    tool_id_map: dict[str, str] = {}

    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = entry.get("type")

                if entry_type == "assistant":
                    msg = _parse_assistant(entry, tool_id_map)
                    if msg:
                        result.messages.append(msg)

                elif entry_type == "user":
                    msg = _parse_user(entry, tool_id_map)
                    if msg:
                        result.messages.append(msg)

                elif entry_type == "summary":
                    result.has_compaction = True

                # skip: attachment, queue-operation, and unknown types

    except OSError:
        pass

    return result


def _parse_assistant(entry: dict, tool_id_map: dict[str, str]) -> Optional[ParsedMessage]:
    msg_data = entry.get("message", {})
    if not isinstance(msg_data, dict):
        return None

    usage = msg_data.get("usage", {}) or {}
    content_blocks = msg_data.get("content", []) or []
    model = msg_data.get("model")

    tool_calls: list[str] = []
    text_parts: list[str] = []

    for block in content_blocks:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "tool_use":
            tool_name = block.get("name", "unknown")
            tool_id = block.get("id", "")
            tool_calls.append(tool_name)
            if tool_id:
                tool_id_map[tool_id] = tool_name
        elif block_type == "text":
            text = block.get("text", "")
            if text:
                text_parts.append(text)
        # skip "thinking" blocks — internal reasoning, counted in input_tokens already

    summary = " ".join(text_parts)[:200]

    return ParsedMessage(
        role="assistant",
        timestamp=_parse_ts(entry.get("timestamp")),
        model=model,
        input_tokens=int(usage.get("input_tokens", 0) or 0),
        output_tokens=int(usage.get("output_tokens", 0) or 0),
        cache_creation_tokens=int(usage.get("cache_creation_input_tokens", 0) or 0),
        cache_read_tokens=int(usage.get("cache_read_input_tokens", 0) or 0),
        content_summary=summary,
        tool_calls=tool_calls,
    )


def _parse_user(entry: dict, tool_id_map: dict[str, str]) -> Optional[ParsedMessage]:
    msg_data = entry.get("message", {})
    if not isinstance(msg_data, dict):
        return None

    content = msg_data.get("content", [])
    tool_error_ids: list[str] = []
    text_parts: list[str] = []

    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "tool_result":
                if block.get("is_error"):
                    tool_use_id = block.get("tool_use_id", "")
                    if tool_use_id:
                        # Resolve to tool name so engine can attribute errors by name
                        tool_error_ids.append(tool_id_map.get(tool_use_id, tool_use_id))
            elif block_type == "text":
                text = block.get("text", "")
                if text:
                    text_parts.append(text)
    elif isinstance(content, str):
        text_parts.append(content)

    summary = " ".join(text_parts)[:200]

    return ParsedMessage(
        role="user",
        timestamp=_parse_ts(entry.get("timestamp")),
        model=None,
        content_summary=summary,
        tool_error_ids=tool_error_ids,
    )


def _parse_ts(ts_value) -> Optional[datetime]:
    if not ts_value:
        return None
    try:
        ts_str = str(ts_value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, TypeError):
        return None
