from __future__ import annotations

from io import BytesIO

import boto3
from botocore.client import Config

from app.core.config import settings


class MinIOObjectStorageProvider:
    """S3-compatible object storage provider backed by MinIO."""

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_root_user,
            aws_secret_access_key=settings.minio_root_password,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

    def ensure_bucket(self, bucket: str) -> None:
        try:
            self._client.head_bucket(Bucket=bucket)
        except Exception:
            self._client.create_bucket(Bucket=bucket)

    def upload_bytes(
        self,
        bucket: str,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> str:
        self.ensure_bucket(bucket)
        self._client.upload_fileobj(
            Fileobj=BytesIO(data),
            Bucket=bucket,
            Key=object_key,
            ExtraArgs={"ContentType": content_type},
        )
        return object_key

    def download_bytes(self, bucket: str, object_key: str) -> bytes:
        response = self._client.get_object(Bucket=bucket, Key=object_key)
        return response["Body"].read()