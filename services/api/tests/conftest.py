"""
Pytest configuration and shared fixtures for the Kairo API test suite.

Strategy:
- Session-scoped: create all DB tables once per test session, drop after.
- Function-scoped: each test gets its own DB session with automatic rollback
  so tests are isolated without recreating the schema on every test.
- The `client` fixture overrides get_db to use the same rolled-back session.

Requires:
    TEST_DATABASE_URL env variable pointing to a PostgreSQL test database.
    (default: postgresql+psycopg://orgmind:orgmind_dev_password@localhost:5432/orgmind_test)
"""

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ── Test database ──────────────────────────────────────────────────────────────

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://orgmind:orgmind_dev_password@localhost:5432/orgmind_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ── Schema lifecycle ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop_policy():
    """Use a selector event loop on Windows so psycopg async can connect."""
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.get_event_loop_policy()


@pytest_asyncio.fixture(scope="session")
async def create_tables():
    """Create all ORM tables once before the session, drop them after."""
    import app.db.models  # noqa: F401 — registers all models with Base.metadata
    from app.db.base import Base

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


# ── Per-test DB session ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def db_session(create_tables) -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession that is rolled back after every test.

    Tests can freely INSERT / UPDATE without polluting each other.
    """
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
def disable_ingestion_enqueue():
    """Tests drive ingestion explicitly; skip Celery enqueue during uploads."""
    from app.core.config import settings

    previous = settings.ingestion_auto_enqueue
    settings.ingestion_auto_enqueue = False
    yield
    settings.ingestion_auto_enqueue = previous


# ── HTTP test client ───────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def fake_storage():
    """Shared in-memory object storage used by the API client fixture."""

    class FakeObjectStorageProvider:
        def __init__(self) -> None:
            self.uploads: list[dict] = []

        def ensure_bucket(self, bucket: str) -> None:
            return None

        def upload_bytes(self, bucket: str, object_key: str, data: bytes, content_type: str) -> str:
            self.uploads.append(
                {
                    "bucket": bucket,
                    "object_key": object_key,
                    "data": data,
                    "content_type": content_type,
                }
            )
            return object_key

        def download_bytes(self, bucket: str, object_key: str) -> bytes:
            for item in self.uploads:
                if item["bucket"] == bucket and item["object_key"] == object_key:
                    return item["data"]
            raise FileNotFoundError(f"Object not found: {bucket}/{object_key}")

    return FakeObjectStorageProvider()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession, fake_storage
) -> AsyncGenerator[AsyncClient, None]:
    """
    Yield an AsyncClient wired to the FastAPI app, with get_db overridden
    to use the same rolled-back test session.
    """
    from app.core.dependencies import get_db
    from app.core.dependencies import get_object_storage_provider
    from app.main import app

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_object_storage_provider] = lambda: fake_storage

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ── Helper fixtures ────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def seeded_tenant_and_admin(db_session: AsyncSession):
    """
    Create a demo tenant + admin user and return them.

    Used by auth and isolation tests without relying on the seed script.
    """
    import uuid as _uuid
    from app.core.security import hash_password
    from app.modules.identity.models import User
    from app.modules.tenancy.models import Role, Tenant, TenantUser, user_roles

    tenant = Tenant(
        id=_uuid.uuid4(),
        slug=f"test-{_uuid.uuid4().hex[:8]}",
        name="Test Organization",
        type="association",
    )
    db_session.add(tenant)
    await db_session.flush()

    user = User(
        id=_uuid.uuid4(),
        email=f"admin-{_uuid.uuid4().hex[:6]}@test.org",
        password_hash=hash_password("TestPass123!"),
        display_name="Test Admin",
        status="active",
    )
    db_session.add(user)
    await db_session.flush()

    role = Role(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        code="admin",
        name="Administrator",
        is_system_role=True,
    )
    db_session.add(role)
    await db_session.flush()

    membership = TenantUser(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        profile_type="admin",
        membership_status="active",
    )
    db_session.add(membership)
    await db_session.flush()

    await db_session.execute(
        user_roles.insert().values(
            tenant_user_id=membership.id, role_id=role.id
        )
    )
    await db_session.flush()

    return {
        "tenant": tenant,
        "user": user,
        "role": role,
        "membership": membership,
        "password": "TestPass123!",
    }
