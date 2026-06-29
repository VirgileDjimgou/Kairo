"""Test doubles for embedding, vector store, and notification providers."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.providers.notifications.base import (
    NotificationChannelDescriptor,
    NotificationDispatchResult,
)


class FakeEmbeddingProvider:
    vector_size = 8

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = sum(ord(char) for char in text) or 1
            vectors.append([(seed + index) / 100.0 for index in range(self.vector_size)])
        return vectors


class FakeVectorStoreProvider:
    def __init__(self) -> None:
        self.points: dict[str, tuple[list[float], dict[str, Any]]] = {}
        self.deleted_versions: list[tuple[str, str]] = []

    def ensure_collection(self, vector_size: int) -> None:
        return None

    def delete_vectors_for_version(self, tenant_id: UUID, document_version_id: UUID) -> None:
        self.deleted_versions.append((str(tenant_id), str(document_version_id)))
        prefix = f"{tenant_id}:{document_version_id}:"
        for key in list(self.points):
            if key.startswith(prefix):
                del self.points[key]

    def upsert_chunk_vectors(
        self,
        points: list[tuple[UUID, list[float], dict[str, Any]]],
    ) -> None:
        for point_id, vector, payload in points:
            key = f"{payload['tenant_id']}:{payload['document_version_id']}:{point_id}"
            self.points[key] = (vector, payload)

    def search_chunk_vectors(
        self,
        *,
        tenant_id: UUID,
        query_vector: list[float],
        limit: int,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for vector, payload in self.points.values():
            if payload.get("tenant_id") != str(tenant_id):
                continue
            score = float(sum(query_vector) + sum(vector))
            results.append({"id": payload["chunk_id"], "score": score, "payload": payload})
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]


class FakeLlmProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return "Grounded answer from authorized sources."


class FakeEmailNotificationProvider:
    channel = "email"

    def __init__(
        self,
        *,
        configured: bool = True,
        status: str = "sent",
        simulation_only: bool = False,
        delivered: bool = True,
        message: str = "Email accepted by fake provider.",
    ) -> None:
        self._configured = configured
        self._status = status
        self._simulation_only = simulation_only
        self._delivered = delivered
        self._message = message
        self.calls: list[dict[str, Any]] = []

    def describe(self) -> NotificationChannelDescriptor:
        return NotificationChannelDescriptor(
            channel=self.channel,
            display_name="Email",
            description="Fake email provider for tests.",
            configured=self._configured,
            simulation_only=self._simulation_only,
            target_hint="Email address",
        )

    async def send_message(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID | None,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult:
        self.calls.append(
            {
                "tenant_id": str(tenant_id),
                "actor_user_id": str(actor_user_id) if actor_user_id else None,
                "recipient": recipient,
                "subject": subject,
                "body": body,
            }
        )
        return NotificationDispatchResult(
            channel=self.channel,
            status=self._status,
            message=self._message,
            delivered=self._delivered,
            simulation_only=self._simulation_only,
        )

    async def send_test_message(
        self,
        *,
        tenant_id: UUID,
        actor_user_id: UUID,
        recipient: str,
        subject: str | None,
        body: str,
    ) -> NotificationDispatchResult:
        return await self.send_message(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            recipient=recipient,
            subject=subject,
            body=body,
        )
