import os
from pydantic import BaseModel, model_validator


class Settings(BaseModel):
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce_research.db")

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "ecommerce_research")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"

    # LLM Configuration
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DB_PASSWORD:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_postgresql(self) -> bool:
        return self.database_url.startswith("postgresql")

    def get_sqlalchemy_engine_args(self) -> dict:
        if self.is_sqlite:
            return {"connect_args": {"check_same_thread": False}, "echo": self.is_development}
        else:
            return {"pool_pre_ping": True, "pool_recycle": 300, "echo": self.is_development}

    @property
    def database_info(self) -> dict:
        return {
            "database_url": self.database_url.split("://")[0] + "://***",
            "database_type": "SQLite" if self.is_sqlite else "PostgreSQL",
            "environment": self.ENVIRONMENT,
            "is_development": self.is_development,
        }

    @model_validator(mode="after")
    def check_db_settings(self):
        if self.is_sqlite:
            return self
        if self.is_postgresql:
            if not self.DB_HOST:
                raise ValueError("DB_HOST is required for PostgreSQL")
            if not self.DB_PORT:
                raise ValueError("DB_PORT is required for PostgreSQL")
            if not self.DB_NAME:
                raise ValueError("DB_NAME is required for PostgreSQL")
            if not self.DB_USER:
                raise ValueError("DB_USER is required for PostgreSQL")
            if not self.DB_PASSWORD:
                raise ValueError("DB_PASSWORD is required for PostgreSQL")
            return self
        raise ValueError("Invalid database type")


settings = Settings()
