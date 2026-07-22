"""Operational recovery evidence tests."""

from datetime import UTC, datetime, timedelta

import pytest
from helpers import create_tenant_with_user, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.integration


def _iso(days_ago: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days_ago)).isoformat()


@pytest.mark.asyncio
async def test_recovery_evidence_round_trip_and_health_flags(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    data = await create_tenant_with_user(db_session, f"recovery-{datetime.now().strftime('%H%M%S')}")
    token = await login(client, data["user"].email, data["password"], data["tenant"].slug)

    payload = {
        "operations": {
            "last_backup_at": _iso(1),
            "last_backup_status": "completed",
            "last_backup_reference": "kairo-backup-20260703_030000.tar.gz",
            "last_restore_drill_at": _iso(14),
            "last_restore_drill_status": "passed",
            "alert_posture": "healthy",
            "alert_contacts_configured": True,
            "backup_retention_days": 30,
            "notes": "Restore drill completed against the current backup.",
        }
    }

    update = await client.put(
        f"/api/v1/tenants/{data['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert update.status_code == 200, update.text
    body = update.json()
    assert body["operations"]["overall_status"] == "healthy"
    assert body["operations"]["backup_is_stale"] is False
    assert body["operations"]["restore_drill_is_stale"] is False
    assert body["operations"]["alert_is_healthy"] is True

    read_back = await client.get(
        f"/api/v1/tenants/{data['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert read_back.status_code == 200, read_back.text
    read_body = read_back.json()
    assert read_body["operations"]["last_backup_reference"] == payload["operations"]["last_backup_reference"]
    assert read_body["operations"]["notes"] == payload["operations"]["notes"]


@pytest.mark.asyncio
async def test_recovery_evidence_is_tenant_scoped_and_warns_when_stale(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    first = await create_tenant_with_user(db_session, f"recovery-a-{datetime.now().strftime('%H%M%S')}")
    second = await create_tenant_with_user(db_session, f"recovery-b-{datetime.now().strftime('%H%M%S')}")

    first_token = await login(client, first["user"].email, first["password"], first["tenant"].slug)
    second_token = await login(client, second["user"].email, second["password"], second["tenant"].slug)

    first_payload = {
        "operations": {
            "last_backup_at": _iso(120),
            "last_backup_status": "completed",
            "last_restore_drill_at": _iso(200),
            "last_restore_drill_status": "passed",
            "alert_posture": "warning",
            "alert_contacts_configured": False,
            "backup_retention_days": 14,
            "notes": "Stale evidence for tenant A.",
        }
    }
    second_payload = {
        "operations": {
            "last_backup_at": _iso(2),
            "last_backup_status": "completed",
            "last_restore_drill_at": _iso(20),
            "last_restore_drill_status": "passed",
            "alert_posture": "healthy",
            "alert_contacts_configured": True,
            "backup_retention_days": 30,
            "notes": "Fresh evidence for tenant B.",
        }
    }

    first_update = await client.put(
        f"/api/v1/tenants/{first['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {first_token}"},
        json=first_payload,
    )
    assert first_update.status_code == 200, first_update.text
    first_body = first_update.json()
    assert first_body["operations"]["backup_is_stale"] is True
    assert first_body["operations"]["restore_drill_is_stale"] is True
    assert first_body["operations"]["overall_status"] in {"warning", "critical"}

    second_update = await client.put(
        f"/api/v1/tenants/{second['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {second_token}"},
        json=second_payload,
    )
    assert second_update.status_code == 200, second_update.text
    second_body = second_update.json()
    assert second_body["operations"]["overall_status"] == "healthy"
    assert second_body["operations"]["backup_is_stale"] is False

    first_read = await client.get(
        f"/api/v1/tenants/{first['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert first_read.status_code == 200, first_read.text
    assert first_read.json()["operations"]["notes"] == "Stale evidence for tenant A."

    second_read = await client.get(
        f"/api/v1/tenants/{second['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert second_read.status_code == 200, second_read.text
    assert second_read.json()["operations"]["notes"] == "Fresh evidence for tenant B."
