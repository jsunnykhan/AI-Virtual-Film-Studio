from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "agent-saas-platform"
    app_env: str = "development"
    app_port: int = 3000
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/ai_movie_studio"
    redis_url: str = "redis://redis:6379/0"

    openai_api_key: str = "place-your-open-api-key"
    openai_model: str = "place-your-llm-model-name"
    openai_base_url: str = "if-any-place"

    # langchain_api_key: str = ""
    # langchain_tracing_v2: str = "false"
    # langchain_project: str = "ai_movie_studio"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
