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
    app_name: str = "OrgMind AI"
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

    # Security — MUST be changed in production
    jwt_secret_key: str = "change-me-in-production"
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
    ollama_llm_model: str = "qwen2.5:7b-instruct"
    ollama_embedding_model: str = "nomic-embed-text"

    # Upload
    max_upload_mb: int = 50
    allowed_upload_extensions: str = "pdf,docx,txt,md,csv,png,jpg,jpeg,webp"

    # Ingestion
    ingestion_chunk_size: int = 800
    ingestion_chunk_overlap: int = 100
    ingestion_auto_enqueue: bool = True

    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_upload_extensions.split(",")]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
