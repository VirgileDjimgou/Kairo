"""Host-safe commands used by the Windows recovery scripts.

Commands run inside the worker image so the host never needs PostgreSQL client
tools or recovery secrets in command history.
"""

from __future__ import annotations

import argparse
import asyncio
import tarfile
from pathlib import Path

import boto3
from botocore.client import Config
from sqlalchemy import select

from app.core.config import settings
from app.db.session import async_session_factory
from app.modules.backup.archive import decrypt_payload, verify_archive_files
from app.modules.backup.service import BackupService
from app.modules.tenancy.models import Tenant


async def _backup(tenant_slug: str | None) -> int:
    async with async_session_factory() as session:
        statement = select(Tenant.id)
        if tenant_slug:
            statement = statement.where(Tenant.slug == tenant_slug)
        tenant_id = await session.scalar(statement.order_by(Tenant.created_at).limit(1))
        if tenant_id is None:
            raise RuntimeError("No tenant was found for the recovery backup")
        service = BackupService(session)
        run = await service.request_backup(
            tenant_id=tenant_id, actor_user_id=None, trigger="host_manual"
        )
        result = await service.execute_run(run.id)
        if result.status != "available":
            raise RuntimeError(f"Backup failed: {result.error_code or 'unknown'}")
        print(result.storage_reference)
    return 0


def _verify(archive: Path, manifest: Path) -> int:
    verify_archive_files(
        archive,
        manifest,
        encryption_key=settings.backup_encryption_key or "",
        signing_key=settings.backup_manifest_signing_key or "",
    )
    print("verified")
    return 0


def _extract(archive: Path, manifest: Path, output: Path) -> int:
    verify_archive_files(
        archive,
        manifest,
        encryption_key=settings.backup_encryption_key or "",
        signing_key=settings.backup_manifest_signing_key or "",
    )
    output.mkdir(parents=True, exist_ok=True)
    clear_archive = decrypt_payload(archive.read_bytes(), settings.backup_encryption_key or "")
    temporary = output / "payload.tar.gz"
    temporary.write_bytes(clear_archive)
    try:
        with tarfile.open(temporary, "r:gz") as bundle:
            destination = output.resolve()
            for member in bundle.getmembers():
                target = (destination / member.name).resolve()
                if not target.is_relative_to(destination):
                    raise ValueError("Unsafe path in backup archive")
            bundle.extractall(destination, filter="data")
    finally:
        temporary.unlink(missing_ok=True)
    print(str(output))
    return 0


def _restore_documents(source: Path, *, replace: bool = False) -> int:
    if not source.is_dir():
        raise ValueError("Extracted documents directory is missing")
    client = boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_root_user,
        aws_secret_access_key=settings.minio_root_password,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
    try:
        client.head_bucket(Bucket=settings.minio_bucket_documents)
    except Exception:
        client.create_bucket(Bucket=settings.minio_bucket_documents)
    if replace:
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=settings.minio_bucket_documents):
            objects = [{"Key": str(item["Key"])} for item in page.get("Contents", [])]
            if objects:
                client.delete_objects(
                    Bucket=settings.minio_bucket_documents,
                    Delete={"Objects": objects, "Quiet": True},
                )
    count = 0
    for path in source.rglob("*"):
        if path.is_file():
            client.upload_file(
                str(path), settings.minio_bucket_documents, path.relative_to(source).as_posix()
            )
            count += 1
    print(count)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    backup = commands.add_parser("backup")
    backup.add_argument("--tenant-slug")
    verify = commands.add_parser("verify")
    verify.add_argument("archive", type=Path)
    verify.add_argument("manifest", type=Path)
    extract = commands.add_parser("extract")
    extract.add_argument("archive", type=Path)
    extract.add_argument("manifest", type=Path)
    extract.add_argument("output", type=Path)
    restore_documents = commands.add_parser("restore-documents")
    restore_documents.add_argument("source", type=Path)
    replace_documents = commands.add_parser("replace-documents")
    replace_documents.add_argument("source", type=Path)
    args = parser.parse_args()
    if args.command == "backup":
        return asyncio.run(_backup(args.tenant_slug))
    if args.command == "verify":
        return _verify(args.archive, args.manifest)
    if args.command == "restore-documents":
        return _restore_documents(args.source)
    if args.command == "replace-documents":
        return _restore_documents(args.source, replace=True)
    return _extract(args.archive, args.manifest, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
