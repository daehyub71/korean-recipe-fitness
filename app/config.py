"""Application configuration using pydantic-settings."""

import os
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


def _load_streamlit_secrets():
    """Streamlit secrets를 환경변수로 로드"""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            for key, value in st.secrets.items():
                if key not in os.environ:
                    os.environ[key] = str(value)
            return True
    except Exception:
        pass
    return False


# Streamlit Cloud 환경이면 secrets 로드
_load_streamlit_secrets()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI API
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # 공공데이터포털 API
    recipe_api_key: str = Field(default="", alias="RECIPE_API_KEY")
    nutrition_api_key: str = Field(default="", alias="NUTRITION_API_KEY")

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
