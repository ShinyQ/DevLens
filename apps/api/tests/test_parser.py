from pathlib import Path

from devlens.ingestion.parser import parse_jsonl_file

FIXTURE = Path(__file__).parent / "fixtures" / "sample_session.jsonl"


def test_message_count():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    # fixture has 5 user + 5 assistant = 10 messages
    assert len(result.messages) == 10


def test_assistant_messages_have_model():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    assistant_msgs = [m for m in result.messages if m.role == "assistant"]
    assert len(assistant_msgs) == 5
    for msg in assistant_msgs:
        assert msg.model == "claude-sonnet-4-6-20250625"


def test_token_totals():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    total_input = sum(m.input_tokens for m in result.messages)
    total_output = sum(m.output_tokens for m in result.messages)
    # From fixture: 1200+1500+1800+2100+2400=9000 input, 85+120+60+95+40=400 output
    assert total_input == 9000
    assert total_output == 400


def test_cache_tokens():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    total_cache_create = sum(m.cache_creation_tokens for m in result.messages)
    total_cache_read = sum(m.cache_read_tokens for m in result.messages)
    # cache_creation: 800+0+0+0+0=800, cache_read: 0+800+1200+1500+1800=5300
    assert total_cache_create == 800
    assert total_cache_read == 5300


def test_tool_names_extracted():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    all_tool_calls = [t for m in result.messages for t in m.tool_calls]
    assert "Read" in all_tool_calls
    assert "Write" in all_tool_calls
    assert "Bash" in all_tool_calls
    assert "Edit" in all_tool_calls


def test_tool_error_attributed():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    # tool_003 (Bash) had is_error=true in fixture; parser resolves ID → tool name
    user_msgs_with_errors = [m for m in result.messages if m.tool_error_ids]
    assert len(user_msgs_with_errors) == 1
    assert "Bash" in user_msgs_with_errors[0].tool_error_ids


def test_no_compaction_flag():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    assert result.has_compaction is False


def test_compaction_flag_set(tmp_path):
    jsonl = tmp_path / "session.jsonl"
    jsonl.write_text(
        '{"type":"summary","summary":"Earlier conversation was about X","timestamp":"2026-06-20T10:00:00Z"}\n'
        '{"type":"user","message":{"role":"user","content":"continue"},"timestamp":"2026-06-20T10:01:00Z","uuid":"u1","sessionId":"s1"}\n'
    )
    result = parse_jsonl_file(jsonl, "s1", "project", "/proj", "claude")
    assert result.has_compaction is True


def test_content_summary_truncated(tmp_path):
    long_text = "A" * 500
    jsonl = tmp_path / "session.jsonl"
    jsonl.write_text(
        f'{{"type":"user","message":{{"role":"user","content":"{long_text}"}},"timestamp":"2026-06-20T10:00:00Z","uuid":"u1","sessionId":"s1"}}\n'
    )
    result = parse_jsonl_file(jsonl, "s1", "project", "/proj", "claude")
    assert len(result.messages[0].content_summary) <= 200


def test_skips_unknown_types(tmp_path):
    jsonl = tmp_path / "session.jsonl"
    jsonl.write_text(
        '{"type":"attachment","data":"some binary"}\n'
        '{"type":"queue-operation","op":"push"}\n'
        '{"type":"user","message":{"role":"user","content":"hello"},"timestamp":"2026-06-20T10:00:00Z","uuid":"u1","sessionId":"s1"}\n'
    )
    result = parse_jsonl_file(jsonl, "s1", "project", "/proj", "claude")
    assert len(result.messages) == 1


def test_empty_file(tmp_path):
    jsonl = tmp_path / "empty.jsonl"
    jsonl.write_text("")
    result = parse_jsonl_file(jsonl, "s1", "project", "/proj", "claude")
    assert len(result.messages) == 0
    assert result.has_compaction is False


def test_malformed_lines_skipped(tmp_path):
    jsonl = tmp_path / "session.jsonl"
    jsonl.write_text(
        "not valid json\n"
        '{"type":"user","message":{"role":"user","content":"ok"},"timestamp":"2026-06-20T10:00:00Z","uuid":"u1","sessionId":"s1"}\n'
    )
    result = parse_jsonl_file(jsonl, "s1", "project", "/proj", "claude")
    assert len(result.messages) == 1


def test_session_metadata():
    result = parse_jsonl_file(FIXTURE, "abc123def456", "my-project", "/home/user/my-project", "claude")
    assert result.session_id == "abc123def456"
    assert result.project_slug == "my-project"
    assert result.provider == "claude"
