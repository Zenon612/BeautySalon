from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive = False,
        extra="ignore",
    )
    app_name: str = "Beauty Salon API"
    debug: bool = Field(default=False, validation_alias="DEBUG")

    database_url: str = Field(..., validation_alias="DATABASE_URL")
    secret_key: str = Field(..., validation_alias="SECRET_KEY")

    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    cors_origins_raw: str = Field(default="", validation_alias="CORS_ORIGINS")

    @property
    def parse_origins(self) -> List[str]:
        if not self.cors_origins_raw:
            return []
        cleaned = self.cors_origins_raw.strip().strip('"').strip("'")
        return [origin.strip() for origin in cleaned.split(",")]

    @property
    def is_production(self) -> bool:
        return not self.debug

settings = Settings()