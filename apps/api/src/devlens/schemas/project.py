from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProjectSummary(BaseModel):
    id: int
    name: str
    slug: str
    path: str
    total_sessions: int
    sessions_30d: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    estimated_cost: float
    last_active: Optional[datetime]
    most_used_model: Optional[str]


class ProjectDetail(ProjectSummary):
    total_messages: int
    total_tool_calls: int
    avg_session_duration_minutes: Optional[float]
