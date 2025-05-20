from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ROOT = Path(__file__).parents[2]


class Settings(BaseSettings):
    worker_count: int = 2
    client_type: Literal["ollama", "openai"]
    llm_model: str
    log_level: Literal["INFO", "WARNING", "ERROR"] = "INFO"

    model_config = SettingsConfigDict(env_file=ROOT / ".env")
