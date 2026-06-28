"""Sprint 4/5 tests: ingestion, chunking, and vector indexing."""

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.documents.models import DocumentChunk, IngestionJob
from app.modules.ingestion.service import IngestionService
from helpers import create_tenant_with_user, login
from fakes import FakeEmbeddingProvider, FakeVectorStoreProvider

pytestmark = pytest.mark.integration


def _build_ingestion_service(db_session: AsyncSession, fake_storage) -> tuple[IngestionService, FakeVectorStoreProvider]:
    vector_store = FakeVectorStoreProvider()
    service = IngestionService(
        db_session,
        fake_storage,
        embedding_provider=FakeEmbeddingProvider(),
        vector_store_provider=vector_store,
    )
    return service, vector_store


@pytest.mark.asyncio
async def test_txt_upload_produces_chunks(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_storage,
) -> None:
    data = await create_tenant_with_user(db_session, f"ingest-{_uuid.uuid4().hex[:6]}")
    token = await login(
        client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug
    )

    body_text = ("Paragraph one about tenant policy.\n\n" * 5).strip()
    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("policy.txt", body_text.encode(), "text/plain")},
        data={"title": "Policy", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text
    job_id = _uuid.UUID(upload.json()["ingestion_job_id"])

    previous = settings.indexing_auto_enabled
    settings.indexing_auto_enabled = True
    try:
        service, vector_store = _build_ingestion_service(db_session, fake_storage)
        await service.process_job(job_id)
    finally:
        settings.indexing_auto_enabled = previous
    await db_session.commit()

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    assert job.status == "completed"

    chunk_count = await db_session.scalar(
        select(func.count())
        .select_from(DocumentChunk)
        .where(
            DocumentChunk.tenant_id == data["tenant"].id,
            DocumentChunk.document_version_id == job.document_version_id,
        )
    )
    assert chunk_count and chunk_count >= 1
    assert len(vector_store.points) >= 1
    _, payload = next(iter(vector_store.points.values()))
    assert payload["tenant_id"] == str(data["tenant"].id)
    assert payload["access_scope"] == "tenant_public"


@pytest.mark.asyncio
async def test_markdown_upload_produces_chunks(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_storage,
) -> None:
    data = await create_tenant_with_user(db_session, f"md-{_uuid.uuid4().hex[:6]}")
    token = await login(
        client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug
    )

    md_content = b"# Guide\n\nSome markdown content for ingestion."
    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("guide.md", md_content, "text/markdown")},
        data={"title": "Guide", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200
    job_id = _uuid.UUID(upload.json()["ingestion_job_id"])

    service, _ = _build_ingestion_service(db_session, fake_storage)
    await service.process_job(job_id)
    await db_session.commit()

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    assert job.status == "completed"


@pytest.mark.asyncio
async def test_pdf_upload_produces_chunks(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_storage,
) -> None:
    import fitz

    data = await create_tenant_with_user(db_session, f"pdf-{_uuid.uuid4().hex[:6]}")
    token = await login(
        client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug
    )

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "tenant policy inside pdf")
    pdf_bytes = doc.tobytes()
    doc.close()

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("report.pdf", pdf_bytes, "application/pdf")},
        data={"title": "Report", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200
    job_id = _uuid.UUID(upload.json()["ingestion_job_id"])

    service, vector_store = _build_ingestion_service(db_session, fake_storage)
    previous = settings.indexing_auto_enabled
    settings.indexing_auto_enabled = True
    try:
        await service.process_job(job_id)
    finally:
        settings.indexing_auto_enabled = previous
    await db_session.commit()

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    assert job.status == "completed"
    assert len(vector_store.points) >= 1


@pytest.mark.asyncio
async def test_image_without_ocr_marks_job_failed(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_storage,
) -> None:
    data = await create_tenant_with_user(db_session, f"img-{_uuid.uuid4().hex[:6]}")
    token = await login(
        client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug
    )

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("scan.png", b"\x89PNG", "image/png")},
        data={"title": "Scan", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200
    job_id = _uuid.UUID(upload.json()["ingestion_job_id"])

    service, _ = _build_ingestion_service(db_session, fake_storage)
    await service.process_job(job_id)
    await db_session.commit()

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    assert job.status == "failed"
    assert job.error_message
    assert "ocr is not configured" in job.error_message.lower()
