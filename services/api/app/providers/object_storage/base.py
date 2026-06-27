from typing import Protocol


class ObjectStorageProvider(Protocol):
    def ensure_bucket(self, bucket: str) -> None: ...

    def upload_bytes(
        self,
        bucket: str,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> str: ...

    def download_bytes(self, bucket: str, object_key: str) -> bytes: ...