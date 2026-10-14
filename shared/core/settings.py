from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "agent-saas-platform"
    app_env: str = "development"
    app_port: int = 3000
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+asyncpg://studio:studio@localhost:5432/ai_movie_studio"
    redis_url: str = "redis://redis:6379/0"

    openai_api_key: str = "place-your-open-api-key"
    openai_model: str = "place-your-llm-model-name"
    openai_base_url: str = "if-any-place"

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # comfyui & media rendering
    comfyui_base_url: str = "http://127.0.0.1:8188"
    comfyui_timeout_seconds: int = 600
    media_output_dir: str = "output"
    ffmpeg_bin: str = "ffmpeg"

    # 24/7 autonomous studio engine
    autonomous_studio_enabled: bool = True
    autonomous_loop_interval_seconds: int = 15

    # for langsmith 
    langchain_api_key: str = ""
    langchain_tracing_v2: bool = False
    langchain_project: str = "ai_movie_studio"
    langchain_endpoint: str = "https://api.smith.langchain.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
