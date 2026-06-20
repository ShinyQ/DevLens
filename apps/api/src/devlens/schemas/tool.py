from pydantic import BaseModel


class ToolStat(BaseModel):
    tool_name: str
    execution_count: int
    is_error_count: int
    error_rate: float
    session_count: int
