"""
Application configuration settings
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # App settings
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 7 days

    # OpenAI settings
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    DEFAULT_MODEL: str = Field(default="gpt-4o-mini", env="DEFAULT_MODEL")
    MAX_TOKENS: int = Field(default=4096, env="MAX_TOKENS")

    PERPLEXITY_API_KEY: str = Field(..., env="PERPLEXITY_API_KEY")
    PERPLEXITY_BASE_URL: str = Field(default="https://api.perplexity.ai", env="PERPLEXITY_BASE_URL")

    # Security settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="ALLOWED_ORIGINS"
    )

    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour in seconds

    # Database settings (for user management)
    DATABASE_URL: str = Field(default="sqlite:///./app.db", env="DATABASE_URL")

    # Redis settings (for rate limiting and caching)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="app.log", env="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
