# Direct Member Access

When an elected office holder creates a member profile, the existing profile-only
workflow remains available. The president, vice president, secretary general,
treasurer, auditor, censor, and sports manager can additionally enable **direct
member access**. Deleting a member profile remains reserved for the president and
secretary general.

The direct-access form requires a temporary password and at least one login route:

- personal email address;
- international telephone number in E.164 form, for example `+49123456789`;
- unique login identifier containing letters, digits, dots, hyphens, or underscores.

Kairo creates the linked member account, assigns the member role in the current
tenant, and marks the password as temporary. The member can sign in using any
supplied login route. Until the member chooses a personal password, the backend
allows only the account profile check and the initial-password endpoint. Every
other protected route is rejected by the backend.

The password change is recorded in the tenant audit trail. No password is stored
in plaintext or included in the audit event.
