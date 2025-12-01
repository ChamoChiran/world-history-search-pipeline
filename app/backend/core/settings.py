import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "HistoryAgent"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS configuration
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # RAG configuration
    CHROMA_DB_DIR: str = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "vector_db")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()