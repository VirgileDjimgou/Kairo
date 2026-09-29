from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.contributions.models import ReminderDeliveryStatus
from app.modules.contributions.schemas import (
    ContributionReminderBatchRequest,
    ContributionReminderBatchResponse,
    ContributionReminderResponse,
    ContributionReminderSendRequest,
)
from app.modules.finance.base import FinanceServiceBase
from app.modules.membership.models import MembershipProfile
from app.modules.membership.repository import MembershipRepository
from app.providers.notifications.base import NotificationDispatchResult


class RemindersMixin(FinanceServiceBase):
    async def list_reminders(
        self,
        tenant_id: UUID,
        *,
        year: int | None = None,
        profile_id: UUID | None = None,
        limit: int = 50,
    ) -> list[ContributionReminderResponse]:
        reminders = await self._repo.list_reminders_by_tenant(
            tenant_id,
            year=year,
            profile_id=profile_id,
            limit=limit,
        )
        return [ContributionReminderResponse.model_validate(reminder) for reminder in reminders]

    async def send_reminder(
        self,
        tenant_id: UUID,
        contribution_id: UUID,
        payload: ContributionReminderSendRequest,
        *,
        actor_user_id: UUID | None = None,
    ) -> ContributionReminderResponse:
        contribution = await self._repo.get_contribution(tenant_id, contribution_id)
        if not contribution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contribution record not found",
            )

        member_repo = MembershipRepository(self._db)
        profile = await member_repo.get_by_id(tenant_id, contribution.membership_profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found for this contribution",
            )

        reminder = await self._dispatch_reminder(
            tenant_id,
            contribution=contribution,
            profile=profile,
            channel=payload.channel,
            actor_user_id=actor_user_id,
        )
        await self._db.commit()
        return ContributionReminderResponse.model_validate(reminder)

    async def send_batch_reminders(
        self,
        tenant_id: UUID,
        payload: ContributionReminderBatchRequest,
        *,
        actor_user_id: UUID | None = None,
    ) -> ContributionReminderBatchResponse:
        contributions = await self._repo.list_by_tenant(tenant_id, payload.year)
        selected = self._filter_reminder_candidates(contributions, payload)
        if len(selected) > payload.limit:
            selected = selected[: payload.limit]

        member_repo = MembershipRepository(self._db)
        profile_ids = list({contribution.membership_profile_id for contribution in selected})
        profiles = {
            profile.id: profile
            for profile in await member_repo.list_by_ids(tenant_id, profile_ids)
        }
        reminders = []
        for contribution in selected:
            profile = profiles.get(contribution.membership_profile_id)
            if not profile:
                continue
            reminder = await self._dispatch_reminder(
                tenant_id,
                contribution=contribution,
                profile=profile,
                channel=payload.channel,
                actor_user_id=actor_user_id,
            )
            reminders.append(ContributionReminderResponse.model_validate(reminder))

        await self._db.commit()
        return ContributionReminderBatchResponse(
            attempted_count=len(selected),
            reminder_count=len(reminders),
            reminders=reminders,
        )

    def _filter_reminder_candidates(
        self,
        contributions: list,
        payload: ContributionReminderBatchRequest,
    ) -> list:
        now = datetime.now(UTC)
        due_soon_cutoff = now + timedelta(days=14)
        filtered = []
        for contribution in contributions:
            if Decimal(str(contribution.balance)) <= Decimal("0.00"):
                continue
            if contribution.status in {"paid", "waived"}:
                continue
            if payload.status is not None and contribution.status != payload.status.value:
                continue
            due_date = contribution.due_date
            if payload.due_scope == "overdue":
                if not (
                    contribution.status == "overdue"
                    or (due_date is not None and due_date < now)
                ):
                    continue
            elif payload.due_scope == "due_soon":
                if due_date is None or due_date > due_soon_cutoff:
                    continue
            filtered.append(contribution)
        return filtered

    async def _dispatch_reminder(
        self,
        tenant_id: UUID,
        *,
        contribution,
        profile: MembershipProfile,
        channel: str,
        actor_user_id: UUID | None,
    ):
        subject, body = self._build_reminder_message(profile, contribution)
        recipient = (profile.email or "").strip()

        if Decimal(str(contribution.balance)) <= Decimal("0.00") or contribution.status in {"paid", "waived"}:
            return await self._create_reminder_record(
                tenant_id,
                contribution=contribution,
                profile=profile,
                channel=channel,
                subject=subject,
                body=body,
                recipient=recipient or "missing-recipient",
                delivery_status=ReminderDeliveryStatus.skipped.value,
                provider_message="Reminder skipped because the contribution has no outstanding balance.",
                actor_user_id=actor_user_id,
                audit_action="reminder_skipped",
            )

        if channel != "email":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only email reminders are supported in this sprint",
            )

        if not recipient:
            return await self._create_reminder_record(
                tenant_id,
                contribution=contribution,
                profile=profile,
                channel=channel,
                subject=subject,
                body=body,
                recipient="missing-email",
                delivery_status=ReminderDeliveryStatus.skipped.value,
                provider_message="Reminder skipped because the member has no email address.",
                actor_user_id=actor_user_id,
                audit_action="reminder_skipped",
            )

        provider = next(
            (item for item in self._notification_providers if getattr(item, "channel", "") == channel),
            None,
        )
        if provider is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No notification provider is available for channel '{channel}'",
            )

        try:
            dispatched = await provider.send_message(
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                recipient=recipient,
                subject=subject,
                body=body,
            )
        except Exception as exc:  # pragma: no cover - defensive safeguard
            dispatched = NotificationDispatchResult(
                channel=channel,
                status=ReminderDeliveryStatus.failed.value,
                message=f"Reminder delivery failed: {exc}",
                delivered=False,
                simulation_only=False,
            )

        audit_action = (
            "reminder_sent"
            if dispatched.status in {ReminderDeliveryStatus.sent.value, ReminderDeliveryStatus.simulated.value}
            else "reminder_failed"
        )
        return await self._create_reminder_record(
            tenant_id,
            contribution=contribution,
            profile=profile,
            channel=channel,
            subject=subject,
            body=body,
            recipient=recipient,
            delivery_status=dispatched.status,
            provider_message=dispatched.message,
            actor_user_id=actor_user_id,
            audit_action=audit_action,
        )

    async def _create_reminder_record(
        self,
        tenant_id: UUID,
        *,
        contribution,
        profile: MembershipProfile,
        channel: str,
        subject: str,
        body: str,
        recipient: str,
        delivery_status: str,
        provider_message: str | None,
        actor_user_id: UUID | None,
        audit_action: str,
    ):
        reminder = await self._repo.create_reminder(
            tenant_id,
            {
                "contribution_record_id": contribution.id,
                "membership_profile_id": profile.id,
                "member_display_name": profile.display_name,
                "member_code": profile.member_code,
                "balance_snapshot": contribution.balance,
                "due_date_snapshot": contribution.due_date,
                "channel": channel,
                "delivery_status": delivery_status,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "provider_message": provider_message,
                "reminded_by": actor_user_id,
            },
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action=audit_action,
            entity_type="contribution_reminder",
            entity_id=reminder.id,
            module_key="contributions",
            details={
                "contribution_record_id": contribution.id,
                "membership_profile_id": profile.id,
                "channel": channel,
                "delivery_status": delivery_status,
                "recipient": recipient,
            },
        )
        return reminder

    def _build_reminder_message(self, profile: MembershipProfile, contribution) -> tuple[str, str]:
        due_line = ""
        if contribution.due_date is not None:
            due_line = f" The recorded due date is {contribution.due_date.strftime('%Y-%m-%d')}."
        subject = f"Contribution reminder for {contribution.year}"
        body = (
            f"Hello {profile.display_name},\n\n"
            f"This is a reminder that your contribution balance for {contribution.year} is "
            f"{Decimal(str(contribution.balance)).quantize(Decimal('0.01'))} {contribution.currency}."
            f"{due_line}\n\n"
            "If you have already paid or need clarification, please contact the treasury team of your organization.\n\n"
            "Kairo automated reminder"
        )
        return subject, body
