from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Combis Sport Verein"
    app_env: str = "development"
    app_debug: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("llm_provider_kind", "embedding_provider_kind", mode="before")
    @classmethod
    def normalize_provider_kind(cls, v: str) -> str:
        return v.strip().lower() if isinstance(v, str) else v

    # Security — MUST be changed in production
    jwt_secret_key: str = "change-me-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Database (psycopg3 async DSN)
    database_url: str = (
        "postgresql+psycopg://orgmind:orgmind_dev_password@postgres:5432/orgmind"
    )

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_public_endpoint: str = "http://localhost:9000"
    minio_root_user: str = "orgmind"
    minio_root_password: str = "orgmind_dev_password"
    minio_bucket_documents: str = "documents"

    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "orgmind_document_chunks"

    # Ollama
    ollama_base_url: str = "http://ollama:11434"
    ollama_llm_model: str = "qwen2.5:14b"
    ollama_embedding_model: str = "bge-m3"

    # OpenAI-compatible local providers (LM Studio, OpenRouter-compatible mocks, etc.)
    llm_provider_kind: Literal["ollama", "openai_compatible"] = "ollama"
    embedding_provider_kind: Literal["ollama", "openai_compatible"] = "ollama"
    openai_compatible_base_url: str = "http://127.0.0.1:1234/v1"
    openai_compatible_api_key: str = "lm-studio"
    openai_compatible_llm_model: str = "zai-org/glm-4.7-flash"
    openai_compatible_embedding_model: str = "text-embedding-nomic-embed-text-v1.5"

    # Optional notification channel placeholders
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    telegram_bot_token: str | None = None
    telegram_default_chat_id: str | None = None
    whatsapp_api_base_url: str | None = None
    whatsapp_api_token: str | None = None

    # Upload
    max_upload_mb: int = 50
    allowed_upload_extensions: str = "pdf,docx,txt,md,csv,xlsx,png,jpg,jpeg,webp"

    # Ingestion
    ingestion_chunk_size: int = 800
    ingestion_chunk_overlap: int = 100
    ingestion_auto_enqueue: bool = True

    # Embeddings / Qdrant
    embedding_dimensions: int = 1024
    embedding_request_timeout_seconds: int = 120
    indexing_auto_enabled: bool = True

    # LLM tuning
    llm_request_timeout_seconds: int = 120
    llm_temperature: float = 0.3
    llm_top_p: float = 0.9
    llm_max_tokens: int = 1024

    # RAG tuning
    rag_top_k: int = 6
    rag_score_threshold: float = 0.65
    rag_candidate_multiplier: int = 5
    rag_language_boost: float = 0.15
    rag_rerank_enabled: bool = True
    rag_rerank_top_k: int = 10
    rag_hybrid_search: bool = True

    # Conversation
    conversation_max_history: int = 20
    conversation_retention_days: int = 30

    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_upload_extensions.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
