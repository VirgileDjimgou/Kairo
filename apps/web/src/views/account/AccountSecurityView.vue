<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ copy.personalAccountSecurity }}
        </div>
        <h1 class="h4 fw-bold mb-1">{{ copy.accountSecurity }}</h1>
        <p class="text-muted mb-0">
          {{ copy.reviewLead }}
        </p>
      </div>
      <div class="d-flex gap-2 align-items-start">
        <RouterLink to="/dashboard" class="btn btn-outline-secondary">
          <i class="bi bi-arrow-left me-1"></i>{{ copy.backToDashboard }}
        </RouterLink>
        <button class="btn om-primary-btn" type="button" @click="loadSecurityState" :disabled="loading">
          {{ loading ? copy.refreshing : copy.refresh }}
        </button>
      </div>
    </div>

    <div v-if="pageError" class="alert alert-warning border-0 shadow-sm mb-4">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ pageError }}
    </div>

    <div class="row g-4 mb-4" data-testid="account-security-summary">
      <div class="col-md-6 col-xl-3" v-for="card in summaryCards" :key="card.id">
        <div class="summary-card h-100">
          <div class="small text-muted mb-2">{{ card.label }}</div>
          <div class="summary-value">{{ card.value }}</div>
          <div class="small text-muted mt-2">{{ card.hint }}</div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-7">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Multi-factor authentication
                </div>
                <h2 class="h6 fw-bold mb-1">Protect sign-in with an authenticator app</h2>
                <p class="text-muted small mb-0">
                  MFA is enforced by the backend. This screen only helps the user complete the secure setup flow.
                </p>
              </div>
              <span class="badge align-self-start" :class="mfaStatus.enabled ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning'">
                {{ mfaStatus.enabled ? 'Enabled' : mfaStatus.enrolled ? 'Pending verification' : 'Not enabled' }}
              </span>
            </div>

            <div v-if="!enrollment.active" class="security-panel">
              <p class="small text-muted mb-3">
                {{
                  mfaStatus.enabled
                    ? 'Your account already requires an authenticator code at sign-in.'
                    : 'Enable MFA to add a second factor at sign-in and reduce account takeover risk.'
                }}
              </p>

              <div class="d-flex flex-wrap gap-2">
                <button
                  v-if="!mfaStatus.enabled"
                  class="btn btn-primary"
                  type="button"
                  :disabled="loadingAction"
                  @click="startEnrollment"
                >
                  {{ loadingAction ? 'Preparing...' : mfaStatus.enrolled ? 'Resume setup' : 'Set up MFA' }}
                </button>
                <button
                  v-if="mfaStatus.enabled"
                  class="btn btn-outline-danger"
                  type="button"
                  :disabled="loadingAction"
                  @click="handleDisableMfa"
                >
                  {{ loadingAction ? 'Updating...' : 'Disable MFA' }}
                </button>
              </div>
            </div>

            <div v-else class="security-panel">
              <div class="row g-4 align-items-start">
                <div class="col-lg-5 text-center">
                  <div v-if="enrollment.qrCodeUrl" class="border rounded d-inline-block p-2 bg-light">
                    <img :src="enrollment.qrCodeUrl" alt="MFA QR code" style="width: 180px; height: 180px" />
                  </div>
                  <div v-else class="border rounded d-inline-block p-3 bg-light small text-break">
                    <code>{{ enrollment.secret }}</code>
                  </div>
                </div>
                <div class="col-lg-7">
                  <ol class="small text-muted ps-3 mb-3">
                    <li>Open your authenticator app.</li>
                    <li>Scan the QR code or enter the secret manually.</li>
                    <li>Enter the 6-digit code below to complete setup.</li>
                  </ol>

                  <div class="small text-muted mb-3">
                    Manual key:
                    <code class="text-break">{{ enrollment.secret }}</code>
                  </div>

                  <div class="mb-3">
                    <label for="mfa-verify-code" class="form-label small fw-medium">Verification code</label>
                    <input
                      id="mfa-verify-code"
                      v-model="verifyCode"
                      type="text"
                      class="form-control text-center"
                      :class="{ 'is-invalid': verifyError }"
                      placeholder="000000"
                      maxlength="6"
                      autocomplete="off"
                    />
                    <div v-if="verifyError" class="invalid-feedback">{{ verifyError }}</div>
                  </div>

                  <div v-if="actionError" class="alert alert-danger py-2 small mb-3">
                    <i class="bi bi-exclamation-circle me-1"></i>{{ actionError }}
                  </div>

                  <div class="d-flex flex-wrap gap-2">
                    <button class="btn btn-primary" type="button" :disabled="loadingAction" @click="completeEnrollment">
                      {{ loadingAction ? 'Verifying...' : 'Enable MFA' }}
                    </button>
                    <button class="btn btn-outline-secondary" type="button" :disabled="loadingAction" @click="cancelEnrollment">
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Password recovery
            </div>
            <h2 class="h6 fw-bold mb-1">Send yourself a secure reset link</h2>
            <p class="text-muted small mb-3">
              This triggers the same backend-protected recovery flow used on the public sign-in screen.
            </p>

            <div class="security-panel">
              <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 align-items-lg-center">
                <div>
                  <div class="fw-medium">{{ authStore.user?.email }}</div>
                  <div class="small text-muted">
                    Use this if you want to rotate your password through the verified reset flow.
                  </div>
                </div>
                <button class="btn btn-outline-primary" type="button" :disabled="passwordResetSending" @click="sendResetLink">
                  {{ passwordResetSending ? 'Sending...' : 'Email reset link' }}
                </button>
              </div>

              <div v-if="passwordResetMessage" class="alert alert-success py-2 small mt-3 mb-0">
                <i class="bi bi-check-circle me-1"></i>{{ passwordResetMessage }}
              </div>

              <div v-if="devResetToken" class="mt-3 p-3 bg-light rounded small">
                <div class="text-muted mb-1">Development reset token</div>
                <code class="text-break">{{ devResetToken }}</code>
                <div class="mt-2">
                  <button class="btn btn-outline-secondary btn-sm" type="button" @click="openResetFlow">
                    Open reset flow
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mt-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Active sessions
                </div>
                <h2 class="h6 fw-bold mb-1">Review and revoke access paths</h2>
                <p class="text-muted small mb-0">
                  The backend tracks active sessions and enforces revocation. Use this area to remove stale access quickly.
                </p>
              </div>
              <div class="d-flex flex-wrap gap-2 align-items-start">
                <button class="btn btn-outline-secondary btn-sm" type="button" :disabled="loadingAction" @click="handleRevokeOtherSessions">
                  Revoke other sessions
                </button>
                <button class="btn btn-outline-danger btn-sm" type="button" :disabled="loadingAction" @click="handleRevokeAllSessions">
                  Log out all sessions
                </button>
              </div>
            </div>

            <div v-if="sessionMessage" class="alert alert-success py-2 small mb-3">
              <i class="bi bi-check-circle me-1"></i>{{ sessionMessage }}
            </div>
            <div v-if="actionError" class="alert alert-danger py-2 small mb-3">
              <i class="bi bi-exclamation-circle me-1"></i>{{ actionError }}
            </div>

            <div v-if="sessions.length === 0" class="security-panel small text-muted">
              No active session inventory is available right now.
            </div>

            <div v-else class="vstack gap-3" data-testid="account-security-sessions">
              <article v-for="session in sessions" :key="session.id" class="security-panel">
                <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
                  <div>
                    <div class="d-flex flex-wrap gap-2 align-items-center mb-2">
                      <span class="badge" :class="session.current ? 'bg-success-subtle text-success' : 'bg-light text-dark border'">
                        {{ session.current ? 'Current session' : 'Active session' }}
                      </span>
                      <span class="small text-muted">{{ formatDateTime(session.last_seen_at) }}</span>
                    </div>
                    <div class="fw-medium small">{{ describeSession(session) }}</div>
                    <div class="small text-muted mt-1">
                      First seen {{ formatDateTime(session.created_at) }}
                      <span v-if="session.last_seen_ip"> · Last IP {{ session.last_seen_ip }}</span>
                    </div>
                  </div>
                  <div class="d-flex align-items-start">
                    <button
                      v-if="!session.current"
                      class="btn btn-outline-danger btn-sm"
                      type="button"
                      :disabled="loadingAction"
                      @click="handleRevokeSession(session.id)"
                    >
                      Revoke
                    </button>
                    <span v-else class="small text-muted">Protected current access</span>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-5">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Security guidance
            </div>
            <div class="vstack gap-3 small text-muted" data-testid="account-security-guidance">
              <div>
                Invitation acceptance gives you a working account; this screen is where you harden it for production usage.
              </div>
              <div>
                Forgot-password remains available on the public sign-in page, but you can also trigger the same flow from here while authenticated.
              </div>
              <div>
                Admins can review MFA enablement and invitation actions from the audit trail, but access decisions still belong exclusively to the backend.
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Recent security activity
            </div>
            <div v-if="securityEvents.length === 0" class="security-panel small text-muted">
              No recent identity events were found for the active tenant context.
            </div>
            <div v-else class="vstack gap-3" data-testid="account-security-events">
              <article v-for="event in securityEvents" :key="event.id" class="security-panel">
                <div class="d-flex justify-content-between gap-3">
                  <div>
                    <div class="fw-medium small">{{ labelSecurityEvent(event.action) }}</div>
                    <div class="small text-muted mt-1">{{ summarizeSecurityEvent(event) }}</div>
                  </div>
                  <div class="small text-muted text-nowrap">{{ formatDateTime(event.created_at) }}</div>
                </div>
              </article>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Recommended path
            </div>
            <div class="timeline-item">
              <div class="timeline-step">1</div>
              <div>
                <div class="fw-semibold small">Accept invite or sign in</div>
                <div class="small text-muted">Use the backend-issued invite or standard login flow.</div>
              </div>
            </div>
            <div class="timeline-item">
              <div class="timeline-step">2</div>
              <div>
                <div class="fw-semibold small">Enable MFA</div>
                <div class="small text-muted">Scan the secret and verify one code to harden the account.</div>
              </div>
            </div>
            <div class="timeline-item mb-0">
              <div class="timeline-step">3</div>
              <div>
                <div class="fw-semibold small">Use reset flow when rotating access</div>
                <div class="small text-muted">Keep password changes inside the audited, rate-limited recovery path.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  type ActiveSessionResponse,
  disableMfa,
  enrollMfa,
  forgotPassword,
  getMfaStatus,
  listActiveSessions,
  listSecurityEvents,
  revokeAllSessions,
  revokeOtherSessions,
  revokeSession,
  type SecurityEventResponse,
  verifyMfa,
} from '@/api/auth.api'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'

const authStore = useAuthStore()
const router = useRouter()
const localeStore = useLocaleStore()
const isDev = import.meta.env.DEV

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      personalAccountSecurity: 'Persoenliche Kontosicherheit',
      accountSecurity: 'Kontosicherheit',
      reviewLead: 'Pruefen Sie MFA, stellen Sie sicheren Zugriff wieder her und halten Sie Ihr Konto fuer den echten Betrieb bereit.',
      backToDashboard: 'Zurueck zum Dashboard',
      refreshing: 'Aktualisierung...',
      refresh: 'Aktualisieren',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      personalAccountSecurity: 'Personal account security',
      accountSecurity: 'Account security',
      reviewLead: 'Review MFA, recover access safely, and keep your account ready for real tenant operations.',
      backToDashboard: 'Back to dashboard',
      refreshing: 'Refreshing...',
      refresh: 'Refresh',
    }
  }
  return {
    personalAccountSecurity: 'Sécurité du compte personnel',
    accountSecurity: 'Sécurité du compte',
    reviewLead: 'Vérifiez la MFA, récupérez l’accès en toute sécurité et gardez votre compte prêt pour un usage réel du tenant.',
    backToDashboard: 'Retour au tableau de bord',
    refreshing: 'Actualisation...',
    refresh: 'Actualiser',
  }
})

const loading = ref(false)
const loadingAction = ref(false)
const passwordResetSending = ref(false)
const pageError = ref('')
const actionError = ref('')
const passwordResetMessage = ref('')
const devResetToken = ref<string | null>(null)
const sessionMessage = ref('')
const verifyCode = ref('')
const verifyError = ref('')
const sessions = ref<ActiveSessionResponse[]>([])
const securityEvents = ref<SecurityEventResponse[]>([])

const mfaStatus = reactive({
  enabled: false,
  enrolled: false,
})

const enrollment = reactive({
  active: false,
  secret: '',
  qrCodeUrl: '',
})

const summaryCards = computed(() => [
  {
    id: 'mfa',
    label: 'MFA status',
    value: mfaStatus.enabled ? 'Enabled' : 'Not enabled',
    hint: mfaStatus.enabled ? 'Authenticator verification required at login' : 'Second factor still recommended',
  },
  {
    id: 'enrollment',
    label: 'Enrollment state',
    value: enrollment.active || mfaStatus.enrolled ? 'Prepared' : 'Not prepared',
    hint: enrollment.active ? 'Awaiting verification code' : 'Secret not currently staged',
  },
  {
    id: 'recovery',
    label: 'Recovery flow',
    value: 'Available',
    hint: 'Password reset is rate-limited and backend controlled',
  },
  {
    id: 'sessions',
    label: 'Active sessions',
    value: String(sessions.value.length),
    hint: sessions.value.some((session) => !session.current) ? 'Other access paths can be revoked' : 'Only the current session remains',
  },
])

function resetEnrollmentState() {
  enrollment.active = false
  enrollment.secret = ''
  enrollment.qrCodeUrl = ''
  verifyCode.value = ''
  verifyError.value = ''
}

async function loadSecurityState() {
  loading.value = true
  pageError.value = ''

  try {
    const [status, activeSessions, recentSecurityEvents] = await Promise.all([
      getMfaStatus(),
      listActiveSessions(),
      listSecurityEvents(),
    ])
    mfaStatus.enabled = status.enabled
    mfaStatus.enrolled = status.enrolled
    sessions.value = activeSessions
    securityEvents.value = recentSecurityEvents

    if (status.enabled) {
      resetEnrollmentState()
    }
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    pageError.value = detail || 'Could not load account security state.'
  } finally {
    loading.value = false
  }
}

async function startEnrollment() {
  loadingAction.value = true
  actionError.value = ''
  verifyError.value = ''

  try {
    const response = await enrollMfa()
    enrollment.secret = response.secret
    enrollment.qrCodeUrl = response.qr_code_url
    enrollment.active = true
    mfaStatus.enrolled = true
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    actionError.value = detail || 'Could not prepare MFA enrollment.'
  } finally {
    loadingAction.value = false
  }
}

async function completeEnrollment() {
  verifyError.value = ''
  actionError.value = ''

  if (!verifyCode.value || verifyCode.value.length !== 6) {
    verifyError.value = 'Enter a 6-digit verification code'
    return
  }

  loadingAction.value = true
  try {
    await verifyMfa({ code: verifyCode.value })
    resetEnrollmentState()
    await loadSecurityState()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    actionError.value = detail || 'Could not enable MFA.'
  } finally {
    loadingAction.value = false
  }
}

function cancelEnrollment() {
  resetEnrollmentState()
}

async function handleDisableMfa() {
  loadingAction.value = true
  actionError.value = ''

  try {
    await disableMfa()
    resetEnrollmentState()
    await loadSecurityState()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    actionError.value = detail || 'Could not disable MFA.'
  } finally {
    loadingAction.value = false
  }
}

async function sendResetLink() {
  if (!authStore.user?.email) return

  passwordResetSending.value = true
  passwordResetMessage.value = ''
  devResetToken.value = null
  sessionMessage.value = ''

  try {
    const response = await forgotPassword({ email: authStore.user.email })
    passwordResetMessage.value = response.message
    if (isDev && response.reset_token) {
      devResetToken.value = response.reset_token
    }
  } catch {
    passwordResetMessage.value = 'The reset flow could not be triggered right now.'
  } finally {
    passwordResetSending.value = false
  }
}

async function openResetFlow() {
  if (!devResetToken.value) return
  authStore.logout()
  await router.push({ path: '/reset-password', query: { token: devResetToken.value } })
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function describeSession(session: ActiveSessionResponse) {
  return session.last_seen_user_agent || session.created_user_agent || 'Unknown device'
}

function labelSecurityEvent(action: string) {
  if (action === 'login_succeeded') return 'Successful sign-in'
  if (action === 'mfa_enabled') return 'MFA enabled'
  if (action === 'mfa_disabled') return 'MFA disabled'
  if (action === 'password_reset_requested') return 'Password reset requested'
  if (action === 'password_reset_completed') return 'Password reset completed'
  if (action === 'session_revoked') return 'Session revoked'
  return action
}

function summarizeSecurityEvent(event: SecurityEventResponse) {
  const reason = typeof event.details.reason === 'string' ? event.details.reason : null
  if (event.action === 'session_revoked' && reason) {
    return `Reason: ${reason.replaceAll('_', ' ')}`
  }
  if (event.action === 'login_succeeded') {
    return event.details.mfa_completed ? 'Authentication completed with MFA.' : 'Authentication completed without MFA.'
  }
  if (event.action === 'password_reset_completed') {
    const count = typeof event.details.revoked_session_count === 'number' ? event.details.revoked_session_count : 0
    return `${count} session(s) were revoked as part of the reset.`
  }
  return 'Recorded by the backend audit trail.'
}

async function handleRevokeSession(sessionId: string) {
  loadingAction.value = true
  actionError.value = ''
  sessionMessage.value = ''

  try {
    const response = await revokeSession(sessionId)
    sessionMessage.value = response.message
    await loadSecurityState()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    actionError.value = detail || 'Could not revoke that session.'
  } finally {
    loadingAction.value = false
  }
}

async function handleRevokeOtherSessions() {
  loadingAction.value = true
  actionError.value = ''
  sessionMessage.value = ''

  try {
    const response = await revokeOtherSessions()
    sessionMessage.value = response.message
    await loadSecurityState()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    actionError.value = detail || 'Could not revoke other sessions.'
  } finally {
    loadingAction.value = false
  }
}

async function handleRevokeAllSessions() {
  loadingAction.value = true
  actionError.value = ''
  sessionMessage.value = ''

  try {
    await revokeAllSessions()
    authStore.logout()
    await router.push('/login')
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    actionError.value = detail || 'Could not revoke all sessions.'
  } finally {
    loadingAction.value = false
  }
}

onMounted(() => {
  void loadSecurityState()
})
</script>

<style scoped>
.summary-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(247, 250, 252, 1) 100%);
  padding: 1rem;
}

.summary-value {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1;
  color: #0f172a;
}

.security-panel {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fbfdff;
  padding: 1rem;
}

.timeline-item {
  display: flex;
  gap: 0.85rem;
  margin-bottom: 1rem;
}

.timeline-step {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(31, 79, 143, 0.12);
  color: #1f4f8f;
  font-weight: 700;
  flex-shrink: 0;
}
</style>
