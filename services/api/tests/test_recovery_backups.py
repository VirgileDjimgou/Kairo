import json
import uuid
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.backup.archive import (
    encrypt_payload,
    sha256_bytes,
    sign_manifest,
    verify_archive_files,
)


@pytest.mark.asyncio
async def test_backup_center_permissions_and_tenant_isolation(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    owner = await create_tenant_with_user(db_session, f"recovery-{uuid.uuid4().hex[:6]}")
    president = await create_user_for_tenant(
        db_session,
        tenant_id=owner["tenant"].id,
        email="president.recovery@test.org",
        password="PresidentPass123!",
        display_name="President Recovery",
        role_code="president",
        profile_type="staff",
    )
    secretary = await create_user_for_tenant(
        db_session,
        tenant_id=owner["tenant"].id,
        email="secretary.recovery@test.org",
        password="SecretaryPass123!",
        display_name="Secretary Recovery",
        role_code="secretary_general",
        profile_type="staff",
    )
    treasurer = await create_user_for_tenant(
        db_session,
        tenant_id=owner["tenant"].id,
        email="treasurer.recovery@test.org",
        password="TreasurerPass123!",
        display_name="Treasurer Recovery",
        role_code="treasurer",
        profile_type="staff",
    )
    other = await create_tenant_with_user(db_session, f"recovery-other-{uuid.uuid4().hex[:6]}")
    await db_session.commit()

    from app.worker.tasks.backups import run_backup
    monkeypatch.setattr(run_backup, "delay", lambda *_args, **_kwargs: None)

    president_token = await login(client, president["user"].email, president["password"], owner["tenant"].slug)
    secretary_token = await login(client, secretary["user"].email, secretary["password"], owner["tenant"].slug)
    treasurer_token = await login(client, treasurer["user"].email, treasurer["password"], owner["tenant"].slug)
    other_token = await login(client, other["user"].email, other["password"], other["tenant"].slug)

    created = await client.post(
        "/api/v1/recovery/backups",
        json={"reason": "before association review"},
        headers={"Authorization": f"Bearer {president_token}"},
    )
    assert created.status_code == 202, created.text
    run_id = created.json()["id"]

    visible = await client.get("/api/v1/recovery/backups", headers={"Authorization": f"Bearer {secretary_token}"})
    assert visible.status_code == 200, visible.text
    assert visible.json()["runs"][0]["id"] == run_id

    denied = await client.get("/api/v1/recovery/backups", headers={"Authorization": f"Bearer {treasurer_token}"})
    assert denied.status_code == 403
    hidden = await client.get(f"/api/v1/recovery/backups/{run_id}", headers={"Authorization": f"Bearer {other_token}"})
    assert hidden.status_code == 404


def test_encrypted_archive_signature_and_checksum_reject_corruption(tmp_path: Path) -> None:
    encryption_key = Fernet.generate_key().decode("utf-8")
    signing_key = "test-signing-key"
    archive = tmp_path / "recovery.enc"
    manifest = tmp_path / "recovery.enc.manifest.json"
    encrypted = encrypt_payload(b"private structured data", encryption_key)
    archive.write_bytes(encrypted)
    signed = sign_manifest(
        {
            "format": "kairo-recovery-v1",
            "archive_sha256": sha256_bytes(encrypted),
            "components": {"postgresql": {"included": True}},
        },
        signing_key,
    )
    manifest.write_text(json.dumps(signed), encoding="utf-8")
    assert verify_archive_files(archive, manifest, encryption_key=encryption_key, signing_key=signing_key)["format"] == "kairo-recovery-v1"

    archive.write_bytes(encrypted + b"corrupted")
    with pytest.raises(ValueError, match="SHA-256"):
        verify_archive_files(archive, manifest, encryption_key=encryption_key, signing_key=signing_key)
