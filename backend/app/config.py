from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///./loan_box.db"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
