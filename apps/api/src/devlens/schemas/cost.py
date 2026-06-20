from datetime import date
from typing import Optional

from pydantic import BaseModel


class CostDataPoint(BaseModel):
    period: str
    input_cost: float
    output_cost: float
    cache_cost: float
    total_cost: float
    input_tokens: int
    output_tokens: int


class ModelCostBreakdown(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    percentage: float


class CostResponse(BaseModel):
    granularity: str
    total_cost: float
    total_input_cost: float
    total_output_cost: float
    total_cache_cost: float
    data_points: list[CostDataPoint]
    model_breakdown: list[ModelCostBreakdown]
