from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Vinhomes AI Real Estate"
    app_version: str = "0.8.0"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_port: int = Field(default=8000, ge=1, le=65535)
    app_host: str = "0.0.0.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    cors_origins: str = "http://localhost:3000"
    sqlalchemy_echo: bool = False

    # LLM Configuration
    llm_provider: Literal["openrouter", "openai", "custom"] = "openrouter"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_api_key: str = ""
    openai_embedding_base_url: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = Field(default=1536, ge=1, le=4096)
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "deepseek/deepseek-chat"
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    openrouter_site_url: str = "https://vinhomes-ai.local"
    openrouter_app_name: str = "Vinhomes AI Real Estate Advisor"
    rag_embedding_provider: Literal["openai", "openrouter", "local_hash"] = "openrouter"
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # Database
    database_url: str = "sqlite:///./app.db"
    auto_create_tables: bool = True
    auto_seed_catalog: bool = True

    # Chat gating (BAN_THIET_KE_V2 Mục 5.1)
    free_message_limit: int = Field(default=3, ge=1, le=20)
    chat_rate_limit_per_minute: int = Field(default=5, ge=1, le=60)
    chat_ip_rate_limit_per_minute: int = Field(default=30, ge=1, le=300)
    customer_score_rate_limit_per_minute: int = Field(default=10, ge=1, le=120)
    login_ip_rate_limit_per_minute: int = Field(default=10, ge=1, le=120)
    login_account_rate_limit_per_minute: int = Field(default=5, ge=1, le=60)

    # Dashboard authentication
    jwt_secret_key: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60, ge=5, le=480)
    admin_email: str = "admin@oceanpark.vn"
    admin_password: str = "ChangeMe123!"
    admin_full_name: str = "Quản trị Ocean Park"
    admin_api_key: str = "change-me-in-production"

    # Project data
    chroma_persist_dir: str = "./data/chroma"
    vinhomes_seed_path: str = "./data/vinhomes_real.json"

    # RAG retrieval
    rag_provider: Literal["legacy", "pgvector"] = "legacy"
    rag_top_k: int = Field(default=5, ge=1, le=20)
    rag_vector_top_k: int = Field(default=12, ge=1, le=50)
    rag_lexical_top_k: int = Field(default=12, ge=1, le=50)
    rag_min_score: float = Field(default=0.05, ge=0.0, le=1.0)
    rag_context_token_budget: int = Field(default=1200, ge=200, le=6000)
    rag_rrf_k: int = Field(default=60, ge=1, le=200)
    rag_vector_weight: float = Field(default=0.6, ge=0.0, le=5.0)
    rag_lexical_weight: float = Field(default=0.4, ge=0.0, le=5.0)
    rag_domain_boost: float = Field(default=0.08, ge=0.0, le=1.0)
    rag_metadata_boost: float = Field(default=0.12, ge=0.0, le=1.0)
    rag_freshness_boost: float = Field(default=0.04, ge=0.0, le=1.0)
    rag_stale_months: int = Field(default=6, ge=1, le=60)

    @property
    def cors_origin_list(self) -> list[str]:
        """Return normalized origins for Starlette's CORS middleware."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def effective_llm_api_key(self) -> str:
        """Return the API key for the selected LLM provider.

        Backward compatibility:
        - `LLM_API_KEY` works for any provider.
        - `OPENAI_API_KEY` still works for OpenAI-compatible gateways.
        - `OPENROUTER_API_KEY` is preferred when `LLM_PROVIDER=openrouter`.
        """
        if self.llm_api_key.strip():
            return self.llm_api_key.strip()
        if self.llm_provider == "openrouter":
            return (self.openrouter_api_key or self.openai_api_key).strip()
        if self.llm_provider == "openai":
            return self.openai_api_key.strip()
        return self.openai_api_key.strip()

    @property
    def effective_llm_base_url(self) -> str:
        """Return the OpenAI-compatible base URL for the selected provider."""
        if self.llm_base_url.strip():
            return self.llm_base_url.strip()
        if self.llm_provider == "openrouter":
            return self.openrouter_base_url
        if self.llm_provider == "openai":
            return self.openai_base_url
        return self.openai_base_url

    @property
    def effective_llm_model(self) -> str:
        """Return the model id for the selected provider."""
        if self.llm_model.strip():
            return self.llm_model.strip()
        if self.llm_provider == "openrouter":
            return self.openrouter_model
        if self.llm_provider == "openai":
            return self.openai_model
        return self.openai_model

    @model_validator(mode="after")
    def validate_deployment_security(self) -> "Settings":
        """Fail fast when staging/production is started with unsafe defaults."""
        if self.app_env not in {"staging", "production"}:
            return self

        errors: list[str] = []
        weak_jwt_secrets = {
            "development-only-change-me",
            "local-docker-secret-change-before-deploy",
            "replace-with-a-long-random-secret",
        }
        jwt_secret_lower = self.jwt_secret_key.lower()
        if (
            len(self.jwt_secret_key) < 32
            or self.jwt_secret_key in weak_jwt_secrets
            or "replace" in jwt_secret_lower
            or "change-me" in jwt_secret_lower
        ):
            errors.append("JWT_SECRET_KEY must be a unique secret of at least 32 characters")

        admin_password_lower = self.admin_password.lower()
        if self.admin_password in {"ChangeMe123!", "change-me", "password"} or any(
            marker in admin_password_lower for marker in ("replace", "change-me")
        ):
            errors.append("ADMIN_PASSWORD must not use a documented default")
        if self.admin_password and len(self.admin_password) < 12:
            errors.append("ADMIN_PASSWORD must contain at least 12 characters")

        if "admin_api_key" in self.model_fields_set and self.admin_api_key == "change-me-in-production":
            errors.append("ADMIN_API_KEY must be changed before staging/production")

        if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            errors.append("DATABASE_URL must use PostgreSQL")
        if self.auto_create_tables:
            errors.append("AUTO_CREATE_TABLES must be false; use Alembic migrations")
        if self.app_env == "production" and any(
            origin == "*" or "localhost" in origin or "127.0.0.1" in origin
            for origin in self.cors_origin_list
        ):
            errors.append("CORS_ORIGINS must contain only production HTTPS domains")

        if errors:
            raise ValueError("Unsafe deployment configuration: " + "; ".join(errors))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
