"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI API
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    # 공공데이터포털 API
    recipe_api_key: str = Field(..., alias="RECIPE_API_KEY")
    nutrition_api_key: str = Field(..., alias="NUTRITION_API_KEY")

    # App Config
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # FAISS Config
    similarity_threshold: float = Field(default=0.7, alias="SIMILARITY_THRESHOLD")
    top_k_results: int = Field(default=3, alias="TOP_K_RESULTS")

    # Default User Profile
    default_weight_kg: float = Field(default=70, alias="DEFAULT_WEIGHT_KG")
    default_height_cm: float = Field(default=170, alias="DEFAULT_HEIGHT_CM")
    default_age: int = Field(default=30, alias="DEFAULT_AGE")
    default_gender: str = Field(default="male", alias="DEFAULT_GENDER")

    # API URLs
    recipe_api_base_url: str = "http://openapi.foodsafetykorea.go.kr/api"
    nutrition_api_base_url: str = "http://openapi.foodsafetykorea.go.kr/api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
