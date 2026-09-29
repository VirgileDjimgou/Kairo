"""Kairo performance baseline harness.

Seeds a deterministic tenant at a representative size (default 200 and 1000
members with three years of contributions/payments and audit history), measures
representative read paths and outbox drains, and writes a machine-readable
baseline plus a human-readable summary.

Usage (repository root):

    python services/api/scripts/performance_baseline.py
    python services/api/scripts/performance_baseline.py --sizes 200 --iterations 3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import tempfile
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import event, insert  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

DEFAULT_JSON = "docs/performance/performance-baseline.json"
DEFAULT_MARKDOWN = "docs/performance/PERFORMANCE_BASELINE.md"


class StatementCounter:
    """Count SQL statements issued against the engine between resets."""

    def __init__(self, engine) -> None:
        self.count = 0
        self._engine = engine
        event.listen(engine.sync_engine, "before_cursor_execute", self._on_execute)

    def _on_execute(self, *args, **kwargs) -> None:
        self.count += 1

    def reset(self) -> None:
        self.count = 0

    def close(self) -> None:
        event.remove(self._engine.sync_engine, "before_cursor_execute", self._on_execute)


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return ordered[index]


async def seed_dataset(engine, members: int, years: int = 3) -> dict:
    import app.db.models  # noqa: F401  (register all models)
    from app.db.base import Base
    from app.modules.audit.models import AuditEvent as AuditModel
    from app.modules.contributions.models import (
        ContributionRecord,
        ExpenseRecord,
        PaymentMethod,
        PaymentRecord,
    )
    from app.modules.domain_events.models import DomainEvent
    from app.modules.identity.models import User
    from app.modules.membership.models import MembershipProfile
    from app.modules.notifications.user_models import (
        NotificationDevice,
        NotificationDeviceProfile,
        UserNotification,
        WebPushSubscription,
    )
    from app.modules.notifications.user_models import (
        NotificationOutboxEvent as OutboxModel,
    )
    from app.modules.tenancy.models import Role, Tenant, TenantUser, user_roles

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    random = __import__("random").Random(42)
    now = datetime.now(UTC)

    async with session_factory() as db:
        tenant_id = uuid.uuid4()
        await db.execute(
            insert(Tenant),
            [
                {
                    "id": tenant_id,
                    "slug": f"perf-baseline-{members}",
                    "name": f"Perf Baseline {members}",
                    "type": "association",
                    "status": "active",
                    "default_language": "fr",
                    "branding_json": "{}",
                    "settings_json": "{}",
                }
            ],
        )

        role_codes = ("member", "treasurer", "auditor", "president", "principal_admin", "admin")
        role_ids = {code: uuid.uuid4() for code in role_codes}
        await db.execute(
            insert(Role),
            [
                {
                    "id": role_ids[code],
                    "tenant_id": tenant_id,
                    "code": code,
                    "name": code.title(),
                    "is_system_role": True,
                }
                for code in role_codes
            ],
        )

        def user_row(index: int, prefix: str) -> dict:
            return {
                "id": uuid.uuid4(),
                "email": f"{prefix}-{index}@perf.example.org",
                "password_hash": "perf-baseline-not-a-real-hash",
                "display_name": f"{prefix.title()} {index:04d}",
                "status": "active",
            }

        admin_user_id = uuid.uuid4()
        member_rows = [user_row(index, "member") for index in range(members)]
        await db.execute(
            insert(User),
            [
                {
                    "id": admin_user_id,
                    "email": "admin-perf@perf.example.org",
                    "password_hash": "perf-baseline-not-a-real-hash",
                    "display_name": "Perf Admin",
                    "status": "active",
                },
                *member_rows,
            ],
        )

        admin_membership_id = uuid.uuid4()
        member_memberships = [
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "user_id": row["id"],
                "membership_status": "active",
                "profile_type": "member",
            }
            for row in member_rows
        ]
        await db.execute(
            insert(TenantUser),
            [
                {
                    "id": admin_membership_id,
                    "tenant_id": tenant_id,
                    "user_id": admin_user_id,
                    "membership_status": "active",
                    "profile_type": "staff",
                },
                *member_memberships,
            ],
        )
        role_assignments = [
            {"tenant_user_id": admin_membership_id, "role_id": role_ids["principal_admin"]},
            {"tenant_user_id": admin_membership_id, "role_id": role_ids["admin"]},
        ]
        for membership in member_memberships:
            role_assignments.append(
                {"tenant_user_id": membership["id"], "role_id": role_ids["member"]}
            )
        await db.execute(insert(user_roles), role_assignments)

        profile_rows = []
        for index, row in enumerate(member_rows):
            profile_rows.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "user_id": row["id"],
                    "member_code": f"PERF-{index:05d}",
                    "first_name": f"Member{index}",
                    "last_name": "Perf",
                    "display_name": row["display_name"],
                    "email": row["email"],
                    "membership_type": "individual",
                    "status": "active",
                }
            )
        await db.execute(insert(MembershipProfile), profile_rows)
        member_profile_id = profile_rows[0]["id"]
        member_user_id = member_rows[0]["id"]

        current_year = now.year
        contribution_rows = []
        payment_rows = []
        for profile in profile_rows:
            for year in range(current_year - years + 1, current_year + 1):
                expected = random.choice((60, 90, 120, 150))
                paid = expected if random.random() < 0.8 else random.choice((0, 20, 40))
                contribution_rows.append(
                    {
                        "id": uuid.uuid4(),
                        "tenant_id": tenant_id,
                        "membership_profile_id": profile["id"],
                        "year": year,
                        "expected_amount": expected,
                        "paid_amount": paid,
                        "balance": expected - paid,
                        "currency": "EUR",
                        "status": "paid" if paid >= expected else "open",
                    }
                )
        await db.execute(insert(ContributionRecord), contribution_rows)
        for contribution in contribution_rows:
            if float(contribution["paid_amount"]) <= 0:
                continue
            payment_rows.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "contribution_record_id": contribution["id"],
                    "amount": contribution["paid_amount"],
                    "currency": "EUR",
                    "paid_at": datetime(
                        contribution["year"], 6, 15, 12, 0, tzinfo=UTC
                    ),
                    "payment_method": PaymentMethod.bank_transfer.value,
                }
            )
        await db.execute(insert(PaymentRecord), payment_rows)
        await db.execute(
            insert(ExpenseRecord),
            [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "category": "administration",
                    "amount": 42 + index,
                    "currency": "EUR",
                    "spent_at": datetime(current_year, (index % 12) + 1, 5, tzinfo=UTC),
                    "description": f"Perf expense {index}",
                    "payment_method": PaymentMethod.bank_transfer.value,
                }
                for index in range(min(members, 500))
            ],
        )

        audit_rows = []
        for index in range(min(members * 5, 5000)):
            audit_rows.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "module_key": "contributions",
                    "action": "perf_audit_event" if index % 2 else "payment_recorded",
                    "entity_type": "payment_record",
                    "entity_id": str(uuid.uuid4()),
                    "details_json": "{}",
                    "created_at": now - timedelta(minutes=index),
                }
            )
        await db.execute(insert(AuditModel), audit_rows)

        notification_rows = []
        for index in range(min(members, 1000)):
            notification_rows.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "recipient_user_id": member_rows[index]["id"],
                    "event_type": "finance.payment_recorded",
                    "category": "finance",
                    "priority": "normal",
                    "target_path": "/finance",
                    "metadata_json": "{}",
                    "deduplication_key": f"perf-notification-{index}",
                    "created_at": now - timedelta(minutes=index),
                }
            )
        await db.execute(insert(UserNotification), notification_rows)

        device_rows = []
        profile_bindings = []
        subscription_rows = []
        for index in range(0, min(members, 1000), 2):
            device_id = uuid.uuid4()
            device_rows.append(
                {
                    "id": device_id,
                    "tenant_id": tenant_id,
                    "installation_id": f"perf-installation-{index:05d}",
                    "platform": "web",
                }
            )
            profile_bindings.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "device_id": device_id,
                    "user_id": member_rows[index]["id"],
                    "push_enabled": True,
                    "preferences_json": "{}",
                    "opted_in_at": now,
                }
            )
            subscription_rows.append(
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "device_id": device_id,
                    "endpoint": f"https://push.perf.example.org/{index:05d}",
                    "p256dh": "perf-p256dh-key-material",
                    "auth": "perf-auth-key-material",
                }
            )
        if device_rows:
            await db.execute(insert(NotificationDevice), device_rows)
            await db.execute(insert(NotificationDeviceProfile), profile_bindings)
            await db.execute(insert(WebPushSubscription), subscription_rows)

        await db.execute(
            insert(OutboxModel),
            [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "event_type": "finance.payment_recorded",
                    "payload_json": json.dumps(
                        {
                            "recipients": [str(member_user_id)],
                            "category": "finance",
                            "target_path": "/finance",
                            "priority": "normal",
                        }
                    ),
                    "deduplication_key": f"perf-outbox-{index}",
                    "status": "pending",
                    "available_at": now,
                }
                for index in range(100)
            ],
        )
        await db.execute(
            insert(DomainEvent),
            [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "event_type": "perf.unmapped_event",
                    "aggregate_type": "performance_probe",
                    "aggregate_id": str(index),
                    "occurred_at": now,
                    "deduplication_key": f"perf-domain-event-{index}",
                    "payload_json": "{}",
                    "applied_handlers_json": "[]",
                    "status": "pending",
                    "available_at": now,
                }
                for index in range(100)
            ],
        )
        await db.commit()

    return {
        "tenant_id": tenant_id,
        "admin_user_id": admin_user_id,
        "member_user_id": member_user_id,
        "member_profile_id": member_profile_id,
        "current_year": current_year,
        "members": members,
    }


def build_operations(context: dict) -> dict:
    from app.modules.attention.service import AttentionService
    from app.modules.audit.service import AuditService
    from app.modules.domain_events.service import DomainEventService
    from app.modules.finance.service import ContributionService
    from app.modules.identity.service import AuthService
    from app.modules.membership.service import MembershipService
    from app.modules.notifications.user_service import UserNotificationService
    from app.modules.search.service import SearchService

    tenant_id = context["tenant_id"]
    admin_user_id = context["admin_user_id"]
    member_user_id = context["member_user_id"]
    year = context["current_year"]

    async def members_list(db):
        await MembershipService(db).list_profiles(tenant_id)

    async def contribution_summary(db):
        await ContributionService(db).get_summary(tenant_id)

    async def annual_budget(db):
        await ContributionService(db).get_annual_budget(tenant_id, year=year)

    async def audit_journal(db):
        await AuditService(db).list_events(tenant_id, limit=100)

    async def managed_users(db):
        await AuthService(db).list_managed_users(
            tenant_id=tenant_id, requesting_user_id=admin_user_id
        )

    async def unreachable_notifications(db):
        await UserNotificationService(db).unreachable_recipients(tenant_id)

    async def attention_overview(db):
        await AttentionService(db).overview(tenant_id, member_user_id, ["member"])

    async def global_search(db):
        await SearchService(db).search(
            tenant_id, admin_user_id, ["principal_admin"], "perf member", limit=20
        )

    async def member_statement(db):
        await MembershipService(db).get_my_statement(tenant_id, member_user_id)

    async def notification_outbox_drain(db):
        from sqlalchemy import insert as sql_insert

        from app.modules.notifications.user_models import NotificationOutboxEvent

        now = datetime.now(UTC)
        await db.execute(
            sql_insert(NotificationOutboxEvent),
            [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "event_type": "finance.payment_recorded",
                    "payload_json": json.dumps(
                        {
                            "recipients": [str(member_user_id)],
                            "category": "finance",
                            "target_path": "/finance",
                        }
                    ),
                    "deduplication_key": f"perf-drain-{uuid.uuid4()}",
                    "status": "pending",
                    "available_at": now,
                }
                for _index in range(50)
            ],
        )
        await db.commit()
        await UserNotificationService(db).process_outbox(batch_size=50)

    async def domain_event_outbox_drain(db):
        from sqlalchemy import insert as sql_insert

        from app.modules.domain_events.models import DomainEvent

        now = datetime.now(UTC)
        await db.execute(
            sql_insert(DomainEvent),
            [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "event_type": "perf.unmapped_event",
                    "aggregate_type": "performance_probe",
                    "aggregate_id": str(uuid.uuid4()),
                    "occurred_at": now,
                    "deduplication_key": f"perf-domain-drain-{uuid.uuid4()}",
                    "payload_json": "{}",
                    "applied_handlers_json": "[]",
                    "status": "pending",
                    "available_at": now,
                }
                for _index in range(50)
            ],
        )
        await db.commit()
        await DomainEventService(db).process_pending(batch_size=50)

    return {
        "members_list": members_list,
        "member_statement": member_statement,
        "contribution_summary": contribution_summary,
        "annual_budget": annual_budget,
        "audit_journal": audit_journal,
        "managed_users": managed_users,
        "unreachable_notifications": unreachable_notifications,
        "attention_overview": attention_overview,
        "global_search": global_search,
        "notification_outbox_drain": notification_outbox_drain,
        "domain_event_outbox_drain": domain_event_outbox_drain,
    }


async def measure_operations(engine, context: dict, iterations: int) -> dict:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    counter = StatementCounter(engine)
    operations = build_operations(context)
    results: dict[str, dict] = {}
    for name, operation in operations.items():
        durations: list[float] = []
        max_statements = 0
        for _ in range(iterations):
            counter.reset()
            started = time.perf_counter()
            async with session_factory() as db:
                await operation(db)
            durations.append((time.perf_counter() - started) * 1000)
            max_statements = max(max_statements, counter.count)
        results[name] = {
            "p50_ms": round(statistics.median(durations), 2),
            "p95_ms": round(_percentile(durations, 0.95), 2),
            "statements": max_statements,
        }
    counter.close()
    return results


def build_thresholds(sizes: dict[str, dict]) -> dict[str, dict]:
    thresholds: dict[str, dict] = {}
    names = {name for size in sizes.values() for name in size}
    for name in sorted(names):
        p95_values = [size[name]["p95_ms"] for size in sizes.values() if name in size]
        statement_values = [size[name]["statements"] for size in sizes.values() if name in size]
        thresholds[name] = {
            "max_p95_ms": round(max(p95_values) * 4 + 100, 2),
            "max_statements": max(statement_values) * 2,
        }
    return thresholds


def render_markdown(report: dict) -> str:
    lines = [
        "# Kairo Performance Baseline",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "Harness: `services/api/scripts/performance_baseline.py` (deterministic seed, SQLite).",
        "Regenerate with `npm run perf:baseline`; check with `npm run perf:check`.",
        "",
    ]
    for size, operations in report["sizes"].items():
        lines.append(f"## {size} members")
        lines.append("")
        lines.append("| Operation | p50 ms | p95 ms | SQL statements |")
        lines.append("| --- | ---: | ---: | ---: |")
        for name, values in operations.items():
            lines.append(
                f"| {name} | {values['p50_ms']} | {values['p95_ms']} | {values['statements']} |"
            )
        lines.append("")
    lines.append("## Thresholds")
    lines.append("")
    lines.append("| Operation | max p95 ms | max statements |")
    lines.append("| --- | ---: | ---: |")
    for name, values in report["thresholds"].items():
        lines.append(f"| {name} | {values['max_p95_ms']} | {values['max_statements']} |")
    lines.append("")
    lines.append(
        "Thresholds are regression signals, not service level objectives: they allow a"
    )
    lines.append("4x p95 margin over the recorded baseline and 2x the statement count.")
    lines.append("")
    return "\n".join(lines)


async def run(args) -> dict:
    sizes = [int(value) for value in args.sizes.split(",") if value]
    report: dict = {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "database": "sqlite" if args.database_url is None else args.database_url.split(":")[0],
            "iterations": args.iterations,
        },
        "sizes": {},
    }
    for members in sizes:
        database_url = args.database_url
        temp_path: str | None = None
        if database_url is None:
            handle, temp_path = tempfile.mkstemp(prefix=f"kairo-perf-{members}-", suffix=".sqlite3")
            import os

            os.close(handle)
            database_url = f"sqlite+aiosqlite:///{Path(temp_path).as_posix()}"
        engine = create_async_engine(
            database_url,
            echo=False,
            connect_args={"check_same_thread": False}
            if database_url.startswith("sqlite+aiosqlite")
            else {},
        )
        try:
            context = await seed_dataset(engine, members)
            report["sizes"][str(members)] = await measure_operations(
                engine, context, args.iterations
            )
        finally:
            await engine.dispose()
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
    report["thresholds"] = build_thresholds(report["sizes"])
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="200,1000")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output", default=DEFAULT_JSON)
    parser.add_argument("--markdown", default=DEFAULT_MARKDOWN)
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args()

    report = asyncio.run(run(args))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = Path(args.markdown)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {output} and {markdown}")
    for size, operations in report["sizes"].items():
        summary = ", ".join(
            f"{name}={values['p95_ms']}ms/{values['statements']}st"
            for name, values in operations.items()
        )
        print(f"{size} members: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
