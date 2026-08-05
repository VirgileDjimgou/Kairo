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
    app_name: str = "Kairo"
    app_env: str = "development"
    app_debug: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator(
        "llm_provider_kind", "embedding_provider_kind", "ai_runtime_mode", mode="before"
    )
    @classmethod
    def normalize_provider_kind(cls, v: str) -> str:
        return v.strip().lower() if isinstance(v, str) else v

    @field_validator("jwt_secret_key", mode="after")
    @classmethod
    def validate_jwt_secret_key(cls, v: str, info) -> str:
        placeholder = "change-me-in-production-use-a-long-random-string"
        env = info.data.get("app_env", "development")
        if v == placeholder and env == "production":
            raise ValueError(
                "JWT_SECRET_KEY must be changed from the default placeholder "
                "in production. Generate a strong random key and set it "
                "in your .env file."
            )
        return v

    # Security — MUST be changed in production
    jwt_secret_key: str = "change-me-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Database (psycopg3 async DSN)
    database_url: str = "postgresql+psycopg://orgmind:orgmind_dev_password@postgres:5432/orgmind"

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
    llm_provider_kind: Literal["ollama", "openai_compatible", "remote_ai_runtime"] = "ollama"
    embedding_provider_kind: Literal["ollama", "openai_compatible", "remote_ai_runtime"] = "ollama"
    openai_compatible_base_url: str = "http://127.0.0.1:1234/v1"
    openai_compatible_api_key: str = "lm-studio"
    openai_compatible_llm_model: str = "zai-org/glm-4.7-flash"
    openai_compatible_embedding_model: str = "text-embedding-nomic-embed-text-v1.5"

    # AI runtime topology. The core API remains the policy enforcement point;
    # the optional remote runtime only executes inference and vector operations.
    ai_runtime_mode: Literal["disabled", "embedded", "remote"] = "embedded"
    ai_gateway_base_url: str | None = None
    ai_gateway_shared_secret: str | None = None
    # Optional Cloudflare Access service-token headers. The HMAC signature is
    # still required by the local gateway after Cloudflare authorizes the call.
    ai_gateway_access_client_id: str | None = None
    ai_gateway_access_client_secret: str | None = None
    ai_gateway_request_ttl_seconds: int = 60
    ai_gateway_health_timeout_seconds: int = 5
    ai_embedding_profile: str | None = None

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
    notification_reconciliation_callback_token: str | None = None

    # Web Push is opt-in and uses generic lock-screen text. VAPID material is
    # supplied only through deployment secrets, never the browser bundle.
    web_push_enabled: bool = True
    web_push_vapid_public_key: str | None = None
    web_push_vapid_private_key: str | None = None
    web_push_vapid_subject: str = "mailto:notifications@localhost"

    # Recovery. Archives are encrypted before leaving the container and are
    # never served directly to browser sessions. Keep both keys in a secret
    # manager or in the protected production .env file.
    backup_enabled: bool = True
    backup_auto_enabled: bool = True
    backup_storage_dir: str = "/var/backups"
    backup_retention_days: int = 30
    backup_encryption_key: str | None = None
    backup_manifest_signing_key: str | None = None
    backup_external_s3_endpoint: str | None = None
    backup_external_s3_bucket: str | None = None
    backup_external_s3_access_key: str | None = None
    backup_external_s3_secret_key: str | None = None
    backup_pitr_enabled: bool = True

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
    rag_keyword_match_boost: float = 0.2
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

    @property
    def ai_runtime_enabled(self) -> bool:
        return self.ai_runtime_mode != "disabled"


settings = Settings()
