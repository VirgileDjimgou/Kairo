"""Sprint 3 acceptance tests: document upload and tenant-scoped listing."""

import uuid as _uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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
