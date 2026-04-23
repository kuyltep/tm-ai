from functools import lru_cache
import json
from typing import Any
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

  port: int = 8000
  host: str = "0.0.0.0"

  db_host: str
  db_port: int
  db_user: SecretStr
  db_password: SecretStr
  db_name: str

  gemini_api_key: SecretStr = SecretStr("")

  api_key: SecretStr

  converter_api_key: SecretStr
  converter_url: AnyHttpUrl

  cors_origins: list[str] = Field(default_factory=lambda: ["*"])
  log_level: str = "INFO"

  @field_validator("cors_origins", mode="before")
  @classmethod
  def parse_cors_origins(cls, value: Any) -> list[str]:
    if value is None or value == "":
      return ["*"]
    if isinstance(value, str):
      stripped = value.strip()
      if stripped.startswith("["):
        return json.loads(stripped)
      return [origin.strip() for origin in stripped.split(",") if origin.strip()]
    return value

  @field_validator("log_level")
  @classmethod
  def normalize_log_level(cls, value: str) -> str:
    normalized = value.upper()
    if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
      return "INFO"
    return normalized

  @property
  def database_url(self) -> str:
    user = quote_plus(self.db_user.get_secret_value())
    password = quote_plus(self.db_password.get_secret_value())
    return f"postgresql+asyncpg://{user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache
def get_settings() -> Settings:
  return Settings()
