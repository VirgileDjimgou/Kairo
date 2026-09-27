from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class PushOutcome(StrEnum):
    DELIVERED = "delivered"
    INVALID_TARGET = "invalid_target"
    TRANSIENT = "transient"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class PushMessage:
    """Generic delivery-hint payload. Detailed content stays in the inbox."""

    title: str
    body: str
    target_path: str


@dataclass(frozen=True, slots=True)
class WebPushTarget:
    endpoint: str
    p256dh: str
    auth: str


@dataclass(frozen=True, slots=True)
class FirebasePushTarget:
    token: str


class WebPushProvider(Protocol):
    def send(self, target: WebPushTarget, message: PushMessage) -> PushOutcome: ...


class FirebasePushProvider(Protocol):
    def send(self, target: FirebasePushTarget, message: PushMessage) -> PushOutcome: ...
