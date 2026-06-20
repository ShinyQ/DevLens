from typing import Optional

from pydantic import BaseModel


class InsightsResponse(BaseModel):
    peak_day_of_week: Optional[str]
    most_active_hour: Optional[int]
    avg_session_duration_minutes: float
    longest_session_id: Optional[str]
    longest_session_duration_minutes: float
    most_used_tool: Optional[str]
    most_used_tool_count: int
    busiest_project: Optional[str]
    cache_hit_rate: float
    avg_messages_per_session: float
    total_tool_calls: int
    total_sessions: int
    total_messages: int
