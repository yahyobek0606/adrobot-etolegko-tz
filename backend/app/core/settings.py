from functools import lru_cache
from typing import Annotated

from pydantic import Field, HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Keitaro Campaign Manager"
    log_level: str = "INFO"
    log_json: bool = True

    database_url: str

    keitaro_base_url: HttpUrl
    keitaro_api_key: SecretStr
    keitaro_default_domain_id: int
    keitaro_default_group_id: int
    keitaro_default_traffic_source_id: int
    keitaro_timeout_seconds: float = 10.0
    keitaro_offers_ttl_seconds: float = 60.0

    fallback_redirect_url: HttpUrl = HttpUrl("https://google.com")

    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
