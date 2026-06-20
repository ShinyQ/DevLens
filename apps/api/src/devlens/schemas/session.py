from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SessionSummary(BaseModel):
    id: int
    session_id: str
    provider: str
    project_id: int
    project_name: str
    model: Optional[str]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_minutes: Optional[float]
    message_count: int
    tool_call_count: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    estimated_cost: float
    has_compaction: bool


class MessageDetail(BaseModel):
    id: int
    role: str
    content_summary: Optional[str]
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    model: Optional[str]
    timestamp: Optional[datetime]


class ToolUsageDetail(BaseModel):
    tool_name: str
    execution_count: int
    is_error_count: int


class SessionDetail(SessionSummary):
    messages: list[MessageDetail]
    tool_usages: list[ToolUsageDetail]


class PaginatedSessionList(BaseModel):
    items: list[SessionSummary]
    total: int
    page: int
    page_size: int
    pages: int
