"""
Configuration settings for the RAG chatbot system.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from openai import AsyncOpenAI
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App Configuration
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # API Rate Limiting
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW: int = 60  # in seconds
    SELECTION_MAX_LENGTH: int = 5000  # in characters

    # Database Configuration
    NEON_DATABASE_URL: str = "postgresql+asyncpg://username:password@ep-xxxx.us-east-1.aws.neon.tech/dbname"

    # Qdrant Configuration
    QDRANT_URL: str = "your_qdrant_cluster_url"
    QDRANT_API_KEY: str = "your_qdrant_api_key"
    QDRANT_COLLECTION_NAME: str = "book_content_chunks"

    # OpenAI Configuration
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    OPENAI_MODEL: str = "gpt-4o"  # Updated model name
    BASE_URL: Optional[str] = "https://openrouter.ai/api/v1"  # Optional custom base URL for OpenAI-compatible APIs

    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:8080",
        "http://localhost:8000",
        "https://your-docusaurus-site.com",
        "https://your-docusaurus-site.github.io"  # For GitHub Pages
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Initialize OpenAI client with optional custom base URL
openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.BASE_URL if settings.BASE_URL else None
)

# Setup logging
def setup_logging():
    """Setup logging configuration."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),  # Log to stdout
        ]
    )

    # Set specific loggers to appropriate levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    return logger


# Initialize logging
setup_logging()

# Export the main logger
logger = get_logger(__name__)