from pydantic import BaseModel


class ModelStat(BaseModel):
    model: str
    session_count: int
    message_count: int
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    estimated_cost: float
