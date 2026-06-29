"""Sprint 3 and Sprint 20 acceptance tests: document upload and tenant-scoped listing."""

from io import BytesIO
import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document, IngestionJob
from app.modules.ingestion.service import IngestionService
from app.providers.parsers import parse_document_bytes
from helpers import create_tenant_with_user, login

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_document_upload_and_list_scoped_to_tenant(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("policy.txt", b"tenant document body", "text/plain")},
        data={
            "title": "Tenant Policy",
            "description": "Internal policy document",
            "access_scope": "tenant_public",
        },
    )
    assert upload.status_code == 200, upload.text
    body = upload.json()
    assert body["title"] == "Tenant Policy"
    assert body["status"] == "uploaded"
    assert body["current_version"]["file_name"] == "policy.txt"
    assert body["ingestion_job_id"]

    listing = await client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200, listing.text
    documents = listing.json()
    assert len(documents) == 1
    assert documents[0]["title"] == "Tenant Policy"
    assert documents[0]["current_version"]["checksum"]


@pytest.mark.asyncio
async def test_document_upload_rejects_unsupported_extension(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("malware.exe", b"MZ", "application/octet-stream")},
        data={"title": "Blocked", "access_scope": "tenant_public"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_document_list_is_tenant_isolated(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    alpha = await create_tenant_with_user(db_session, f"alpha-{_uuid.uuid4().hex[:6]}")
    beta = await create_tenant_with_user(db_session, f"beta-{_uuid.uuid4().hex[:6]}")

    token_alpha = await login(
        client, alpha["user"].email, alpha["password"], tenant_slug=alpha["tenant"].slug
    )

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_alpha}"},
        files={"file": ("alpha-only.txt", b"alpha tenant secret", "text/plain")},
        data={"title": "Alpha Confidential", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text

    alpha_list = await client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {token_alpha}"},
    )
    assert alpha_list.status_code == 200
    assert len(alpha_list.json()) == 1
    assert alpha_list.json()[0]["title"] == "Alpha Confidential"

    token_beta = await login(
        client, beta["user"].email, beta["password"], tenant_slug=beta["tenant"].slug
    )
    beta_list = await client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {token_beta}"},
    )
    assert beta_list.status_code == 200
    assert beta_list.json() == []


@pytest.mark.asyncio
async def test_upload_stores_object_with_tenant_scoped_key(
    client: AsyncClient,
    seeded_tenant_and_admin: dict,
    fake_storage,
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    response = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("notes.txt", b"scoped storage key", "text/plain")},
        data={"title": "Scoped Notes", "access_scope": "tenant_public"},
    )
    assert response.status_code == 200, response.text

    assert len(fake_storage.uploads) == 1
    stored = fake_storage.uploads[0]
    assert str(data["tenant"].id) in stored["object_key"]
    assert stored["data"] == b"scoped storage key"


@pytest.mark.asyncio
async def test_ingestion_job_status_is_tenant_scoped(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    alpha = await create_tenant_with_user(db_session, f"job-a-{_uuid.uuid4().hex[:6]}")
    beta = await create_tenant_with_user(db_session, f"job-b-{_uuid.uuid4().hex[:6]}")

    token_alpha = await login(
        client, alpha["user"].email, alpha["password"], tenant_slug=alpha["tenant"].slug
    )
    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_alpha}"},
        files={"file": ("job.txt", b"job status probe", "text/plain")},
        data={"title": "Job Probe", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200
    job_id = upload.json()["ingestion_job_id"]

    token_beta = await login(
        client, beta["user"].email, beta["password"], tenant_slug=beta["tenant"].slug
    )
    forbidden = await client.get(
        f"/api/v1/documents/ingestion-jobs/{job_id}",
        headers={"Authorization": f"Bearer {token_beta}"},
    )
    assert forbidden.status_code == 404

    allowed = await client.get(
        f"/api/v1/documents/ingestion-jobs/{job_id}",
        headers={"Authorization": f"Bearer {token_alpha}"},
    )
    assert allowed.status_code == 200
    body = allowed.json()
    assert body["id"] == job_id
    assert body["status"] == "pending"


@pytest.mark.asyncio
async def test_admin_can_update_document_access_and_roles(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("policy.txt", b"admin scoped body", "text/plain")},
        data={"title": "Admin Policy", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text
    document_id = upload.json()["id"]

    response = await client.patch(
        f"/api/v1/documents/{document_id}/access",
        headers={"Authorization": f"Bearer {token}"},
        json={"access_scope": "role_restricted", "allowed_role_ids": ["admin", "member"]},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_scope"] == "role_restricted"
    assert sorted(body["allowed_role_ids"]) == ["admin", "member"]

    listing = await client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200
    documents = listing.json()
    assert documents[0]["allowed_role_ids"] == ["admin", "member"]


@pytest.mark.asyncio
async def test_non_admin_cannot_update_document_access(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    tenant = await create_tenant_with_user(
        db_session,
        f"member-{_uuid.uuid4().hex[:6]}",
        role_code="member",
        profile_type="member",
    )
    token = await login(client, tenant["user"].email, tenant["password"], tenant_slug=tenant["tenant"].slug)

    response = await client.patch(
        "/api/v1/documents/00000000-0000-0000-0000-000000000001/access",
        headers={"Authorization": f"Bearer {token}"},
        json={"access_scope": "tenant_public"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_queue_document_reindex(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("reindex.txt", b"reindex body", "text/plain")},
        data={"title": "Reindex Target", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text
    document_id = upload.json()["id"]

    response = await client.post(
        f"/api/v1/documents/{document_id}/reindex",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["document_id"] == document_id
    assert body["status"] == "pending"
    assert body["chunk_count"] == 0


@pytest.mark.asyncio
async def test_duplicate_upload_reports_existing_document(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    first = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("duplicate.txt", b"same body", "text/plain")},
        data={"title": "Duplicate Source", "access_scope": "tenant_public"},
    )
    assert first.status_code == 200, first.text

    second = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("duplicate.txt", b"same body", "text/plain")},
        data={"title": "Duplicate Source Copy", "access_scope": "tenant_public"},
    )
    assert second.status_code == 200, second.text
    assert second.json()["duplicate_of_document_id"] == first.json()["id"]


@pytest.mark.asyncio
async def test_image_document_uses_ocr_and_becomes_searchable(
    client: AsyncClient,
    db_session: AsyncSession,
    fake_storage,
    fake_vector_store,
    fake_llm,
) -> None:
    from PIL import Image, ImageDraw, ImageFont

    data = await create_tenant_with_user(db_session, f"ocr-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    image = Image.new("RGB", (900, 240), "white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 64)
    except OSError:
        font = ImageFont.load_default()
    draw.text((40, 70), "HELLO OCR", fill="black", font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    parsed = parse_document_bytes(image_bytes, "hello.png")
    assert "HELLO" in parsed.upper()

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("hello.png", image_bytes, "image/png")},
        data={"title": "OCR target", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text
    job_id = upload.json()["ingestion_job_id"]

    service = IngestionService(
        db_session,
        fake_storage,
        embedding_provider=type("E", (), {"embed_texts": lambda self, texts: [[0.1] * 8 for _ in texts]})(),
        vector_store_provider=fake_vector_store,
    )
    await service.process_job(_uuid.UUID(job_id))

    docs = await client.get(
        "/api/v1/documents/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert docs.status_code == 200, docs.text
    body = docs.json()[0]
    assert body["status"] == "ready"


@pytest.mark.asyncio
async def test_bulk_upload_returns_partial_success(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    token = await login(client, data["user"].email, data["password"])

    response = await client.post(
        "/api/v1/documents/bulk-upload",
        headers={"Authorization": f"Bearer {token}"},
        files=[
            ("files", ("a.txt", b"alpha bulk body", "text/plain")),
            ("files", ("bad.exe", b"MZ", "application/octet-stream")),
        ],
        data={"title_prefix": "Bulk "},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success_count"] == 1
    assert body["failure_count"] == 1
    assert body["items"][0]["status"] == "uploaded"
    assert body["items"][1]["status"] == "failed"


@pytest.mark.asyncio
async def test_archive_restore_and_retry_failed_job(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    data = await create_tenant_with_user(db_session, f"arch-{_uuid.uuid4().hex[:6]}")
    token = await login(client, data["user"].email, data["password"], tenant_slug=data["tenant"].slug)

    upload = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("archive.txt", b"archive body", "text/plain")},
        data={"title": "Archive Target", "access_scope": "tenant_public"},
    )
    assert upload.status_code == 200, upload.text
    document_id = upload.json()["id"]
    job_id = upload.json()["ingestion_job_id"]

    archive_resp = await client.patch(
        f"/api/v1/documents/{document_id}/archive",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert archive_resp.status_code == 200, archive_resp.text
    assert archive_resp.json()["status"] == "archived"

    restore_resp = await client.patch(
        f"/api/v1/documents/{document_id}/unarchive",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert restore_resp.status_code == 200, restore_resp.text
    assert restore_resp.json()["status"] in {"ready", "uploaded"}

    job = await db_session.get(IngestionJob, _uuid.UUID(job_id))
    assert job is not None
    job.status = "failed"
    job.error_message = "parser error"
    await db_session.commit()

    retry_resp = await client.post(
        f"/api/v1/documents/ingestion-jobs/{job_id}/retry",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert retry_resp.status_code == 200, retry_resp.text
    assert retry_resp.json()["job"]["status"] == "pending"
