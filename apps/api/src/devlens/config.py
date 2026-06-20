from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:////app/data/devlens.db"
    claude_data_path: Path = Path("/home/claude_data")

    github_token: Optional[str] = None
    github_org: Optional[str] = None

    pricing: dict = {
        "claude-opus-4-5": {"input": 3.0, "output": 15.0},
        "claude-opus-4": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
        "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
        "claude-sonnet-4": {"input": 3.0, "output": 15.0},
        "claude-haiku-4-5": {"input": 0.8, "output": 4.0},
        "claude-haiku-4": {"input": 0.8, "output": 4.0},
        "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-5-haiku": {"input": 0.8, "output": 4.0},
        "claude-3-opus": {"input": 15.0, "output": 75.0},
    }
    cache_creation_multiplier: float = 1.25
    cache_read_multiplier: float = 0.10

    @field_validator("claude_data_path", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser()


settings = Settings()
