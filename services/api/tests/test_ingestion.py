"""Sprint 4 tests: text ingestion, chunking, and job lifecycle."""

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import DocumentChunk, IngestionJob
from app.modules.ingestion.service import IngestionService
from helpers import create_tenant_with_user, login

pytestmark = pytest.mark.integration


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

    service = IngestionService(db_session, fake_storage)
    await service.process_job(job_id)
    await db_session.commit()

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    assert job.status == "completed"
    assert job.error_message is None
    assert job.started_at is not None
    assert job.finished_at is not None

    chunk_count = await db_session.scalar(
        select(func.count())
        .select_from(DocumentChunk)
        .where(
            DocumentChunk.tenant_id == data["tenant"].id,
            DocumentChunk.document_id == job.document_id,
        )
    )
    assert chunk_count and chunk_count >= 1

    chunk_rows = (
        await db_session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_version_id == job.document_version_id)
            .order_by(DocumentChunk.chunk_index)
        )
    ).all()
    texts = [chunk.text for chunk in chunk_rows]
    assert any("tenant policy" in text for text in texts)
    assert all(chunk.tenant_id == data["tenant"].id for chunk in chunk_rows)


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

    service = IngestionService(db_session, fake_storage)
    await service.process_job(job_id)
    await db_session.commit()

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    assert job.status == "completed"

    chunks = await db_session.scalars(
        select(DocumentChunk).where(DocumentChunk.document_version_id == job.document_version_id)
    )
    assert len(chunks.all()) >= 1


@pytest.mark.asyncio
async def test_unsupported_format_marks_job_failed(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_storage,
) -> None:
    data = await create_tenant_with_user(db_session, f"pdf-{_uuid.uuid4().hex[:6]}")
    token = await login(
        client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug
    )

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("report.pdf", b"%PDF-1.4 fake", "application/pdf")},
        data={"title": "Report", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200
    job_id = _uuid.UUID(upload.json()["ingestion_job_id"])

    service = IngestionService(db_session, fake_storage)
    await service.process_job(job_id)
    await db_session.commit()

    job = await db_session.get(IngestionJob, job_id)
    assert job is not None
    assert job.status == "failed"
    assert job.error_message
    assert "not supported yet" in job.error_message.lower()
