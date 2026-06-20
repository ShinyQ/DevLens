from datetime import date
from typing import Optional

from pydantic import BaseModel


class DailyTokenPoint(BaseModel):
    date: date
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    total_tokens: int


class DailyCostPoint(BaseModel):
    date: date
    estimated_cost: float
    input_cost: float
    output_cost: float
    cache_cost: float


class OverviewResponse(BaseModel):
    total_sessions: int
    total_projects: int
    total_input_tokens: int
    total_output_tokens: int
    total_cache_tokens: int
    total_tokens: int
    cost_all_time: float
    cost_30d: float
    cost_7d: float
    active_projects_30d: int
    token_trend: list[DailyTokenPoint]
    cost_trend: list[DailyCostPoint]
    most_active_project: Optional[str]
    most_used_model: Optional[str]
