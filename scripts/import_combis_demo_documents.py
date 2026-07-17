from __future__ import annotations

# ruff: noqa: E402
import asyncio
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "services" / "api"
sys.path.insert(0, str(API_ROOT))

from app.core.config import settings
from app.core.dependencies import (
    get_embedding_provider,
    get_object_storage_provider,
    get_vector_store_provider,
)
from app.db.session import async_session_factory
from app.modules.documents.metadata import (
    classify_archive_access,
    infer_document_language,
)
from app.modules.documents.models import (
    Document,
    DocumentStatus,
    DocumentVersion,
    IngestionJob,
)
from app.modules.documents.repository import DocumentRepository
from app.modules.identity.models import User
from app.modules.ingestion.service import IngestionService
from app.modules.tenancy.models import Role, Tenant
from sqlalchemy import select

ARCHIVE_DIR = Path(
    os.getenv("COMBIS_ARCHIVE_DIR", str(ROOT / "Combis Sport Verein"))
)
TARGET_TENANT_SLUG = os.getenv("COMBIS_TARGET_TENANT", "demo")


async def main() -> None:
    if not ARCHIVE_DIR.exists():
        raise RuntimeError(f"Archive folder not found: {ARCHIVE_DIR}")

    storage_provider = get_object_storage_provider()
    embedding_provider = get_embedding_provider()
    vector_store_provider = get_vector_store_provider()
    storage_provider.ensure_bucket(settings.minio_bucket_documents)

    async with async_session_factory() as db:
        repo = DocumentRepository(db)
        ingestion = IngestionService(
            db,
            storage_provider=storage_provider,
            embedding_provider=embedding_provider,
            vector_store_provider=vector_store_provider,
        )

        tenant = await db.scalar(
            select(Tenant).where(Tenant.slug == TARGET_TENANT_SLUG)
        )
        if tenant is None:
            raise RuntimeError("Demo tenant not found. Run the seed first.")

        owner = await db.scalar(select(User).where(User.email == "principal@demo.org"))
        if owner is None:
            owner = await db.scalar(select(User).where(User.email == "admin@demo.org"))
        if owner is None:
            raise RuntimeError("No owner user found for document import.")

        roles = {
            role.code: str(role.id)
            for role in (
                await db.execute(select(Role).where(Role.tenant_id == tenant.id))
            )
            .scalars()
            .all()
        }

        imported = 0
        skipped = 0
        for path in sorted(ARCHIVE_DIR.iterdir()):
            if not path.is_file():
                continue
            extension = path.suffix.lower().lstrip(".")
            if extension not in {
                "pdf",
                "docx",
                "txt",
                "md",
                "csv",
                "xlsx",
                "png",
                "jpg",
                "jpeg",
                "webp",
            }:
                skipped += 1
                continue

            file_bytes = path.read_bytes()
            checksum = hashlib.sha256(file_bytes).hexdigest()
            duplicate = await repo.get_duplicate_document_by_checksum(
                tenant.id,
                checksum,
                path.name,
            )
            if duplicate is not None:
                skipped += 1
                continue

            access_scope, allowed_role_ids = classify_archive_access(path.name, roles)
            language = infer_document_language(file_name=path.name, title=path.stem)

            document_id = uuid.uuid4()
            version_id = uuid.uuid4()
            job_id = uuid.uuid4()
            storage_key = f"{tenant.slug}/{document_id}/{version_id}/{path.name}"
            storage_provider.upload_bytes(
                bucket=settings.minio_bucket_documents,
                object_key=storage_key,
                data=file_bytes,
                content_type=guess_content_type(extension),
            )

            document = Document(
                id=document_id,
                tenant_id=tenant.id,
                title=path.stem,
                description=f"Imported Combis archive document: {path.name}",
                source_type="association_archive",
                language=language,
                access_scope=access_scope,
                allowed_role_ids_json=(
                    json.dumps(allowed_role_ids) if allowed_role_ids else None
                ),
                owner_user_id=owner.id,
                status=DocumentStatus.uploaded.value,
                current_version_id=None,
                created_by=owner.id,
            )
            version = DocumentVersion(
                id=version_id,
                tenant_id=tenant.id,
                document_id=document_id,
                version_number=1,
                file_name=path.name,
                mime_type=guess_content_type(extension),
                file_size_bytes=len(file_bytes),
                storage_bucket=settings.minio_bucket_documents,
                storage_key=storage_key,
                checksum=checksum,
                created_by=owner.id,
            )
            job = IngestionJob(
                id=job_id,
                tenant_id=tenant.id,
                document_id=document_id,
                document_version_id=version_id,
                status="pending",
            )

            await repo.create_document(document)
            await repo.create_version(version)
            document.current_version_id = version_id
            await repo.create_ingestion_job(job)
            await db.commit()
            await ingestion.process_job(job_id)
            imported += 1
            print(f"Imported: {path.name} -> {access_scope} [{language}]")

        print(f"Done. Imported={imported} Skipped={skipped}")


def guess_content_type(extension: str) -> str:
    mapping = {
        "pdf": "application/pdf",
        "docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        "txt": "text/plain",
        "md": "text/markdown",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }
    return mapping.get(extension, "application/octet-stream")


if __name__ == "__main__":
    asyncio.run(main())
