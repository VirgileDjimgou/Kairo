from __future__ import annotations

import json
import os
import re
import subprocess
import tarfile
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

import boto3
from botocore.client import Config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.audit.service import AuditService
from app.modules.backup.archive import (
    encrypt_payload,
    sha256_bytes,
    sign_manifest,
    verify_archive_files,
)
from app.modules.backup.models import BackupRun
from app.modules.backup.schemas import BackupOverviewResponse, BackupRunResponse


class BackupService:
    """Coordinates encrypted platform backups without exposing archives to HTTP clients."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._audit = AuditService(db)

    async def request_backup(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID | None,
        trigger: str,
        reason: str | None = None,
    ) -> BackupRun:
        if not settings.backup_enabled:
            raise ValueError("Backup operations are disabled by deployment configuration")
        run = BackupRun(
            tenant_id=tenant_id, requested_by=actor_user_id, trigger=trigger, status="queued"
        )
        self._db.add(run)
        await self._db.flush()
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="backup_requested",
            entity_type="backup_run",
            entity_id=run.id,
            module_key="recovery",
            details={"trigger": trigger, "reason": reason or ""},
        )
        await self._db.commit()
        return run

    async def list_overview(self, tenant_id: UUID) -> BackupOverviewResponse:
        rows = await self._db.execute(
            select(BackupRun)
            .where(BackupRun.tenant_id == tenant_id)
            .order_by(BackupRun.requested_at.desc())
            .limit(20)
        )
        runs = list(rows.scalars().all())
        successful = next((row for row in runs if row.status == "available"), None)
        last_drill = next((row for row in runs if row.status == "restore_drill_passed"), None)
        return BackupOverviewResponse(
            automatic_enabled=settings.backup_auto_enabled,
            retention_days=settings.backup_retention_days,
            external_storage_configured=self._external_storage_configured(),
            point_in_time_recovery_enabled=settings.backup_pitr_enabled,
            last_successful_backup_at=successful.completed_at if successful else None,
            last_restore_drill_at=last_drill.completed_at if last_drill else None,
            runs=[self.to_response(run) for run in runs],
        )

    async def get_owned_run(self, tenant_id: UUID, run_id: UUID) -> BackupRun | None:
        return await self._db.scalar(
            select(BackupRun).where(BackupRun.tenant_id == tenant_id, BackupRun.id == run_id)
        )

    async def stage_import(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID,
        archive_name: str,
        archive: bytes,
        manifest: bytes,
    ) -> BackupRun:
        """Verify an imported encrypted archive and register it for host-side restore.

        Actual restoration is deliberately not done from a web request. It
        requires maintenance mode and a host-side confirmation script.
        """
        self._require_keys()
        if not archive_name.endswith(".enc") or len(archive) < 64 or len(manifest) < 32:
            raise ValueError("Invalid encrypted backup archive or manifest")
        safe_name = Path(archive_name).name
        target_dir = self._storage_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        archive_path = target_dir / safe_name
        manifest_path = target_dir / f"{safe_name}.manifest.json"
        archive_path.write_bytes(archive)
        manifest_path.write_bytes(manifest)
        try:
            verified = verify_archive_files(
                archive_path,
                manifest_path,
                encryption_key=settings.backup_encryption_key or "",
                signing_key=settings.backup_manifest_signing_key or "",
            )
        except Exception:
            archive_path.unlink(missing_ok=True)
            manifest_path.unlink(missing_ok=True)
            raise
        run = BackupRun(
            tenant_id=tenant_id,
            requested_by=actor_user_id,
            trigger="import",
            status="staged",
            storage_reference=archive_path.name,
            archive_sha256=str(verified["archive_sha256"]),
            manifest_sha256=sha256_bytes(manifest),
            archive_size_bytes=len(archive),
            components_json=json.dumps(verified.get("components", {})),
            completed_at=datetime.now(UTC),
            verified_at=datetime.now(UTC),
        )
        self._db.add(run)
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="backup_import_verified",
            entity_type="backup_run",
            entity_id=run.id,
            module_key="recovery",
            details={"archive": archive_path.name, "verified": True},
        )
        await self._db.commit()
        return run

    async def execute_run(self, run_id: UUID) -> BackupRun:
        run = await self._db.get(BackupRun, run_id)
        if run is None:
            raise ValueError("Backup run not found")
        if run.status not in {"queued", "failed"}:
            return run
        self._require_keys()
        run.status, run.started_at, run.error_code = "running", datetime.now(UTC), None
        await self._db.commit()
        try:
            result = self._create_encrypted_archive(run)
            run.status = "available"
            run.storage_reference = result["storage_reference"]
            run.archive_sha256 = result["archive_sha256"]
            run.manifest_sha256 = result["manifest_sha256"]
            run.archive_size_bytes = result["archive_size_bytes"]
            run.components_json = json.dumps(result["components"])
            run.completed_at = datetime.now(UTC)
            run.verified_at = datetime.now(UTC)
            await self._audit.record_event(
                tenant_id=run.tenant_id,
                actor_user_id=run.requested_by,
                action="backup_completed",
                entity_type="backup_run",
                entity_id=run.id,
                module_key="recovery",
                details={
                    "trigger": run.trigger,
                    "archive_sha256": run.archive_sha256,
                    "components": result["components"],
                },
            )
        except Exception as exc:
            run.status, run.error_code, run.completed_at = (
                "failed",
                type(exc).__name__,
                datetime.now(UTC),
            )
            await self._audit.record_event(
                tenant_id=run.tenant_id,
                actor_user_id=run.requested_by,
                action="backup_failed",
                entity_type="backup_run",
                entity_id=run.id,
                module_key="recovery",
                details={"trigger": run.trigger, "error_code": type(exc).__name__},
            )
        await self._db.commit()
        return run

    async def prune_archives(self) -> int:
        cutoff = datetime.now(UTC) - timedelta(days=settings.backup_retention_days)
        rows = await self._db.execute(
            select(BackupRun).where(
                BackupRun.status == "available", BackupRun.completed_at < cutoff
            )
        )
        removed = 0
        for run in rows.scalars().all():
            if run.storage_reference:
                archive = self._storage_dir() / run.storage_reference
                archive.unlink(missing_ok=True)
                Path(f"{archive}.manifest.json").unlink(missing_ok=True)
            run.status = "expired"
            removed += 1
        await self._db.commit()
        return removed

    @staticmethod
    def to_response(run: BackupRun) -> BackupRunResponse:
        try:
            components = json.loads(run.components_json)
        except json.JSONDecodeError:
            components = {}
        return BackupRunResponse(
            id=run.id,
            tenant_id=run.tenant_id,
            trigger=run.trigger,
            status=run.status,
            storage_reference=run.storage_reference,
            archive_sha256=run.archive_sha256,
            manifest_sha256=run.manifest_sha256,
            archive_size_bytes=run.archive_size_bytes,
            components=components,
            error_code=run.error_code,
            requested_at=run.requested_at,
            started_at=run.started_at,
            completed_at=run.completed_at,
            verified_at=run.verified_at,
        )

    def _create_encrypted_archive(self, run: BackupRun) -> dict[str, object]:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        stem = f"kairo-recovery-{stamp}-{str(run.id)[:8]}"
        target_dir = self._storage_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="kairo-backup-") as temporary:
            root = Path(temporary)
            database_path = root / "postgres.sql"
            self._dump_postgres(database_path)
            documents_count = self._dump_documents(root / "documents")
            components = {
                "postgresql": {
                    "included": True,
                    "sha256": sha256_bytes(database_path.read_bytes()),
                },
                "minio_documents": {"included": True, "objects": documents_count},
                "redis": {"included": False, "reason": "non_authoritative_queue_cache"},
                "qdrant": {"included": False, "reason": "rebuild_from_documents"},
                "wal": {"enabled": settings.backup_pitr_enabled, "reason": "host_archive_volume"},
            }
            tar_path = root / f"{stem}.tar.gz"
            with tarfile.open(tar_path, "w:gz") as bundle:
                bundle.add(database_path, arcname="postgres.sql")
                documents_dir = root / "documents"
                if documents_dir.exists():
                    bundle.add(documents_dir, arcname="documents")
            encrypted = encrypt_payload(tar_path.read_bytes(), settings.backup_encryption_key or "")
        archive_path = target_dir / f"{stem}.enc"
        archive_path.write_bytes(encrypted)
        manifest = sign_manifest(
            {
                "format": "kairo-recovery-v1",
                "created_at": datetime.now(UTC).isoformat(),
                "archive": archive_path.name,
                "archive_sha256": sha256_bytes(encrypted),
                "components": components,
            },
            settings.backup_manifest_signing_key or "",
        )
        manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
        manifest_path = Path(f"{archive_path}.manifest.json")
        manifest_path.write_bytes(manifest_bytes)
        verify_archive_files(
            archive_path,
            manifest_path,
            encryption_key=settings.backup_encryption_key or "",
            signing_key=settings.backup_manifest_signing_key or "",
        )
        self._upload_external(archive_path, manifest_path)
        return {
            "storage_reference": archive_path.name,
            "archive_sha256": manifest["archive_sha256"],
            "manifest_sha256": sha256_bytes(manifest_bytes),
            "archive_size_bytes": archive_path.stat().st_size,
            "components": components,
        }

    def _dump_postgres(self, target: Path) -> None:
        parsed = urlparse(
            settings.database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        )
        if not parsed.hostname:
            raise RuntimeError("Backup requires a PostgreSQL DATABASE_URL")
        environment = os.environ.copy()
        if parsed.password:
            environment["PGPASSWORD"] = parsed.password
        command = [
            "pg_dump",
            "--host",
            parsed.hostname,
            "--port",
            str(parsed.port or 5432),
            "--username",
            parsed.username or "postgres",
            "--format=plain",
            "--clean",
            "--if-exists",
            "--create",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(target),
            (parsed.path or "/postgres").lstrip("/"),
        ]
        subprocess.run(  # noqa: S603 -- fixed pg_dump binary; args come from deployment config
            command,
            env=environment,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        # The Debian base image may provide a newer pg_dump client than the
        # PostgreSQL 16 server image. PostgreSQL 17 emits this harmless session
        # setting, which PostgreSQL 16 does not recognise during recovery.
        # Remove only that version-specific preamble so a generated archive
        # remains restorable to the supported production server version.
        dump = target.read_bytes().replace(b"SET transaction_timeout = 0;\n", b"")
        # pg_dump 17 also adds psql-only \restrict directives. They are not
        # understood by the PostgreSQL 16 client used in the recovery target.
        dump = re.sub(br"^\\(?:un)?restrict.*\r?\n", b"", dump, flags=re.MULTILINE)
        target.write_bytes(dump)

    def _dump_documents(self, target_dir: Path) -> int:
        client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_root_user,
            aws_secret_access_key=settings.minio_root_password,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        try:
            paginator = client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=settings.minio_bucket_documents):
                for entry in page.get("Contents", []):
                    key = str(entry["Key"])
                    destination = target_dir / key
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    client.download_file(settings.minio_bucket_documents, key, str(destination))
                    count += 1
        except Exception as exc:
            # An empty, not-yet-created documents bucket is legitimate. Other
            # failures must fail the backup rather than silently dropping files.
            if "NoSuchBucket" not in str(exc):
                raise
        return count

    def _upload_external(self, archive_path: Path, manifest_path: Path) -> None:
        if not self._external_storage_configured():
            return
        client = boto3.client(
            "s3",
            endpoint_url=settings.backup_external_s3_endpoint,
            aws_access_key_id=settings.backup_external_s3_access_key,
            aws_secret_access_key=settings.backup_external_s3_secret_key,
            config=Config(signature_version="s3v4"),
        )
        bucket = settings.backup_external_s3_bucket or ""
        client.upload_file(str(archive_path), bucket, archive_path.name)
        client.upload_file(str(manifest_path), bucket, manifest_path.name)

    def _storage_dir(self) -> Path:
        return Path(settings.backup_storage_dir).resolve()

    def _require_keys(self) -> None:
        if not settings.backup_encryption_key or not settings.backup_manifest_signing_key:
            raise ValueError("Recovery encryption and manifest signing keys must be configured")

    @staticmethod
    def _external_storage_configured() -> bool:
        return all(
            [
                settings.backup_external_s3_endpoint,
                settings.backup_external_s3_bucket,
                settings.backup_external_s3_access_key,
                settings.backup_external_s3_secret_key,
            ]
        )
