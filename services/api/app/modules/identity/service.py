from app.modules.identity.administration.service import AdministrationMixin
from app.modules.identity.authentication.service import AuthenticationMixin
from app.modules.identity.base import IdentityServiceBase
from app.modules.identity.invitations.service import InvitationsMixin
from app.modules.identity.mfa.service import MfaMixin
from app.modules.identity.passwords.service import PasswordsMixin
from app.modules.identity.recovery.service import RecoveryMixin
from app.modules.identity.sessions.service import SessionsMixin
from app.modules.identity.tenancy.service import TenancyMixin


class AuthService(
    AuthenticationMixin,
    PasswordsMixin,
    SessionsMixin,
    MfaMixin,
    InvitationsMixin,
    RecoveryMixin,
    AdministrationMixin,
    TenancyMixin,
    IdentityServiceBase,
):
    """Facade composing the identity domains (auth, passwords, sessions,
    MFA, invitations, recovery, tenant administration, tenancy)."""
