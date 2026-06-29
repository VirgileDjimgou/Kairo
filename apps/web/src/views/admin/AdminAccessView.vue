<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Team onboarding and lifecycle
          </div>
        <h1 class="h4 fw-bold mb-1">Access and lifecycle operations</h1>
        <p class="text-muted mb-0">
          Invite teammates, contain risky access, and keep tenant user lifecycle visible from one admin surface.
        </p>
      </div>
      <div class="d-flex gap-2 align-items-start">
        <RouterLink to="/admin" class="btn btn-outline-secondary">
          <i class="bi bi-arrow-left me-1"></i>Back to overview
        </RouterLink>
        <button class="btn om-primary-btn" type="button" @click="loadAccessConsole" :disabled="loading">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="pageError" class="alert alert-warning border-0 shadow-sm mb-4">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ pageError }}
    </div>

    <div class="row g-4 mb-4" data-testid="admin-access-summary">
      <div class="col-md-6 col-xl-3" v-for="card in summaryCards" :key="card.id">
        <div class="summary-card h-100">
          <div class="small text-muted mb-2">{{ card.label }}</div>
          <div class="summary-value">{{ card.value }}</div>
          <div class="small text-muted mt-2">{{ card.hint }}</div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-5">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Invite teammate
                </div>
                <h2 class="h6 fw-bold mb-1">Create a tenant invitation</h2>
                <p class="text-muted small mb-0">
                  The backend remains the access control authority. This form only triggers the admin flow.
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ roleOptions.length }} role(s)
              </span>
            </div>

            <form class="vstack gap-3" @submit.prevent="submitInvite" novalidate>
              <div>
                <label for="invite-email" class="form-label small fw-medium">Email</label>
                <input
                  id="invite-email"
                  v-model.trim="inviteForm.email"
                  type="email"
                  class="form-control"
                  :class="{ 'is-invalid': formErrors.email }"
                  placeholder="teammate@example.org"
                  autocomplete="email"
                  required
                />
                <div v-if="formErrors.email" class="invalid-feedback">{{ formErrors.email }}</div>
              </div>

              <div>
                <label for="invite-role" class="form-label small fw-medium">Role</label>
                <select
                  id="invite-role"
                  v-model="inviteForm.roleCode"
                  class="form-select"
                  :class="{ 'is-invalid': formErrors.roleCode }"
                  :disabled="roleOptions.length === 0"
                >
                  <option value="" disabled>Select a role</option>
                  <option v-for="role in roleOptions" :key="role.id" :value="role.code">
                    {{ role.name }} ({{ role.code }})
                  </option>
                </select>
                <div v-if="formErrors.roleCode" class="invalid-feedback">{{ formErrors.roleCode }}</div>
              </div>

              <div v-if="submitError" class="alert alert-danger py-2 small mb-0">
                <i class="bi bi-exclamation-circle me-1"></i>{{ submitError }}
              </div>

              <button type="submit" class="btn btn-primary" :disabled="submitting || !tenantId">
                <span
                  v-if="submitting"
                  class="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                ></span>
                {{ submitting ? 'Sending invitation...' : 'Send invitation' }}
              </button>
            </form>
          </div>
        </div>

        <div v-if="latestInvite" class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Latest invitation
            </div>
            <h2 class="h6 fw-bold mb-2">Delivery outcome</h2>
            <p class="small text-muted mb-2">
              Invitation delivery is handled by the backend. Manual link sharing is exposed only for simulation or fallback scenarios.
            </p>
            <div class="d-flex flex-wrap gap-2 align-items-center mb-3">
              <span class="badge" :class="deliveryBadgeClass(latestInvite.delivery_status)">
                {{ latestInvite.delivery_status }}
              </span>
              <span class="small text-muted">
                {{ latestInvite.delivery_message || 'No provider detail returned.' }}
              </span>
            </div>
            <template v-if="latestInvite.acceptUrl">
              <div class="invite-link-box small mb-3">{{ latestInvite.acceptUrl }}</div>
              <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-outline-primary btn-sm" type="button" @click="copyLatestInviteLink">
                  <i class="bi bi-clipboard me-1"></i>{{ copiedInviteId === latestInvite.invitation_id ? 'Copied' : 'Copy link' }}
                </button>
                <a :href="latestInvite.acceptUrl" class="btn btn-outline-secondary btn-sm" target="_blank" rel="noreferrer">
                  Open acceptance page
                </a>
              </div>
            </template>
            <p v-else class="small text-muted mb-0">
              The secure link was delivered through the configured email channel and is intentionally not exposed here.
            </p>
          </div>
        </div>
      </div>

      <div class="col-xl-7">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Invitation lifecycle
                </div>
                <h2 class="h6 fw-bold mb-1">Current invitation status</h2>
                <p class="text-muted small mb-0">
                  Pending invitations can be cancelled. Accepted, expired, and cancelled items stay visible for operational traceability.
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ invitations.length }} total
              </span>
            </div>

            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="invitations.length === 0" class="empty-state">
              <i class="bi bi-person-plus display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No invitations yet</p>
              <p class="text-muted mb-0">
                Start by inviting the first teammate so access operations become visible to the tenant admin team.
              </p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle mb-0" aria-label="Tenant invitations">
                <thead class="table-light">
                  <tr>
                    <th scope="col">Email</th>
                    <th scope="col">Role</th>
                    <th scope="col">Status</th>
                    <th scope="col">Expires</th>
                    <th class="text-end" scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="invitation in invitations" :key="invitation.id">
                    <td class="fw-medium">{{ invitation.email }}</td>
                    <td class="small text-muted">{{ invitation.role_code }}</td>
                    <td>
                      <span class="badge" :class="statusBadgeClass(invitation.status)">
                        {{ invitation.status }}
                      </span>
                    </td>
                    <td class="small">{{ formatDateTime(invitation.expires_at) }}</td>
                    <td class="text-end">
                      <button
                        v-if="invitation.status === 'pending'"
                        class="btn btn-sm btn-outline-danger"
                        type="button"
                        :disabled="cancellingId === invitation.id"
                        @click="cancelInvite(invitation.id)"
                      >
                        {{ cancellingId === invitation.id ? 'Cancelling...' : 'Cancel' }}
                      </button>
                      <span v-else class="small text-muted">No action</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Tenant user lifecycle
                </div>
                <h2 class="h6 fw-bold mb-1">Current user access state</h2>
                <p class="text-muted small mb-0">
                  Suspend or reactivate tenant users, and revoke active tenant sessions when incident response is needed.
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ managedUsers.length }} user(s)
              </span>
            </div>

            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="managedUsers.length === 0" class="empty-state">
              <i class="bi bi-people display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No tenant users found</p>
              <p class="text-muted mb-0">
                User lifecycle controls appear here once the tenant has active or historical memberships.
              </p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle mb-0" aria-label="Tenant user lifecycle" data-testid="admin-user-lifecycle">
                <thead class="table-light">
                  <tr>
                    <th scope="col">User</th>
                    <th scope="col">Profile</th>
                    <th scope="col">Status</th>
                    <th scope="col">Sessions</th>
                    <th scope="col">Last activity</th>
                    <th class="text-end" scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="managedUser in managedUsers" :key="managedUser.user_id">
                    <td>
                      <div class="fw-medium">{{ managedUser.display_name }}</div>
                      <div class="small text-muted">{{ managedUser.email }}</div>
                    </td>
                    <td>
                      <div class="small">{{ managedUser.profile_type }}</div>
                      <div class="small text-muted">{{ managedUser.roles.join(', ') || 'No roles' }}</div>
                    </td>
                    <td>
                      <span class="badge" :class="membershipStatusBadgeClass(managedUser.membership_status)">
                        {{ managedUser.membership_status }}
                      </span>
                    </td>
                    <td>
                      <div class="fw-medium">{{ managedUser.active_session_count }}</div>
                      <div class="small text-muted">{{ managedUser.active_session_count === 1 ? 'active session' : 'active sessions' }}</div>
                    </td>
                    <td class="small">
                      <div>{{ managedUser.last_security_event_at ? formatDateTime(managedUser.last_security_event_at) : 'No recent event' }}</div>
                      <div class="text-muted">{{ managedUser.last_security_event_action || 'No identity activity yet' }}</div>
                    </td>
                    <td class="text-end">
                      <div class="d-flex flex-wrap gap-2 justify-content-end">
                        <button
                          v-if="managedUser.membership_status === 'active'"
                          class="btn btn-sm btn-outline-danger"
                          type="button"
                          :disabled="lifecycleActionId === `${managedUser.user_id}:suspend`"
                          @click="suspendUser(managedUser.user_id)"
                        >
                          {{ lifecycleActionId === `${managedUser.user_id}:suspend` ? 'Suspending...' : 'Suspend' }}
                        </button>
                        <button
                          v-if="managedUser.membership_status !== 'active'"
                          class="btn btn-sm btn-outline-success"
                          type="button"
                          :disabled="lifecycleActionId === `${managedUser.user_id}:reactivate`"
                          @click="reactivateUser(managedUser.user_id)"
                        >
                          {{ lifecycleActionId === `${managedUser.user_id}:reactivate` ? 'Reactivating...' : 'Reactivate' }}
                        </button>
                        <button
                          class="btn btn-sm btn-outline-secondary"
                          type="button"
                          :disabled="lifecycleActionId === `${managedUser.user_id}:revoke`"
                          @click="revokeUserSessions(managedUser.user_id)"
                        >
                          {{ lifecycleActionId === `${managedUser.user_id}:revoke` ? 'Revoking...' : 'Revoke sessions' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Access guidance
            </div>
            <div class="vstack gap-3 small text-muted" data-testid="admin-access-guidance">
              <div>
                Invitees accept access through the dedicated acceptance route and create their own password there.
              </div>
              <div>
                Password reset and MFA already exist as self-service identity flows and stay protected by backend checks.
              </div>
              <div>
                Use the audit trail to review invitation, suspension, reactivation, and forced-session-revocation actions.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import {
  cancelInvitation,
  inviteUser,
  listInvitations,
  listManagedUsers,
  reactivateManagedUser,
  revokeManagedUserSessions,
  suspendManagedUser,
  type InvitationStatusResponse,
  type InviteResponse,
  type ManagedTenantUserResponse,
} from '@/api/auth.api'
import { getTenantRoles, type RoleResponse } from '@/api/settings.api'
import { useTenantStore } from '@/stores/tenant.store'

const tenantStore = useTenantStore()

const loading = ref(false)
const pageError = ref('')
const submitError = ref('')
const submitting = ref(false)
const cancellingId = ref<string | null>(null)
const lifecycleActionId = ref<string | null>(null)
const copiedInviteId = ref<string | null>(null)

const roleOptions = ref<RoleResponse[]>([])
const invitations = ref<InvitationStatusResponse[]>([])
const managedUsers = ref<ManagedTenantUserResponse[]>([])
const latestInvite = ref<(InviteResponse & { acceptUrl: string | null }) | null>(null)

const inviteForm = reactive({
  email: '',
  roleCode: '',
})

const formErrors = reactive({
  email: '',
  roleCode: '',
})

const tenantId = computed(() => tenantStore.currentTenant?.tenant_id ?? '')

const summaryCards = computed(() => {
  const pending = invitations.value.filter((item) => item.status === 'pending').length
  const accepted = invitations.value.filter((item) => item.status === 'accepted').length
  const cancelled = invitations.value.filter((item) => item.status === 'cancelled').length
  const expired = invitations.value.filter((item) => isExpired(item)).length
  const suspended = managedUsers.value.filter((item) => item.membership_status !== 'active').length

  return [
    { id: 'pending', label: 'Pending', value: String(pending), hint: 'Awaiting invitee action' },
    { id: 'accepted', label: 'Accepted', value: String(accepted), hint: 'Successfully onboarded' },
    { id: 'cancelled', label: 'Cancelled', value: String(cancelled), hint: 'Stopped before use' },
    { id: 'suspended', label: 'Suspended', value: String(suspended), hint: 'Need admin reactivation' },
    { id: 'roles', label: 'Available roles', value: String(roleOptions.value.length), hint: 'Selectable tenant roles' },
    ...(expired > 0
      ? [{ id: 'expired', label: 'Expired', value: String(expired), hint: 'Need a new invite link' }]
      : []),
  ]
})

function normalizeInvitation(invitation: InvitationStatusResponse): InvitationStatusResponse {
  if (invitation.status === 'pending' && isExpired(invitation)) {
    return { ...invitation, status: 'expired' }
  }
  return invitation
}

function isExpired(invitation: Pick<InvitationStatusResponse, 'status' | 'expires_at'>) {
  return invitation.status === 'pending' && new Date(invitation.expires_at).getTime() < Date.now()
}

function statusBadgeClass(status: string) {
  if (status === 'accepted') return 'bg-success-subtle text-success'
  if (status === 'cancelled') return 'bg-secondary-subtle text-secondary'
  if (status === 'expired') return 'bg-danger-subtle text-danger'
  return 'bg-warning-subtle text-warning'
}

function deliveryBadgeClass(status: string) {
  if (status === 'sent') return 'bg-success-subtle text-success'
  if (status === 'failed') return 'bg-danger-subtle text-danger'
  if (status === 'manual') return 'bg-secondary-subtle text-secondary'
  return 'bg-warning-subtle text-warning'
}

function membershipStatusBadgeClass(status: string) {
  if (status === 'active') return 'bg-success-subtle text-success'
  if (status === 'suspended') return 'bg-danger-subtle text-danger'
  return 'bg-secondary-subtle text-secondary'
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

function buildAcceptUrl(rawToken: string) {
  const url = new URL('/accept-invite', window.location.origin)
  url.searchParams.set('token', rawToken)
  return url.toString()
}

function clearFormErrors() {
  formErrors.email = ''
  formErrors.roleCode = ''
  submitError.value = ''
}

function validateInviteForm() {
  clearFormErrors()

  if (!inviteForm.email || !inviteForm.email.includes('@')) {
    formErrors.email = 'A valid email is required'
  }

  if (!inviteForm.roleCode) {
    formErrors.roleCode = 'Select a tenant role'
  }

  return !formErrors.email && !formErrors.roleCode
}

async function loadAccessConsole() {
  if (!tenantId.value) {
    pageError.value = 'No active tenant is selected.'
    return
  }

  loading.value = true
  pageError.value = ''

  try {
    const [roles, invitationItems, managedUserItems] = await Promise.all([
      getTenantRoles(tenantId.value),
      listInvitations(tenantId.value),
      listManagedUsers(tenantId.value),
    ])
    roleOptions.value = roles.sort((left, right) => left.name.localeCompare(right.name))
    invitations.value = invitationItems
      .map(normalizeInvitation)
      .sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime())
    managedUsers.value = managedUserItems
      .slice()
      .sort((left, right) => left.display_name.localeCompare(right.display_name))

    if (!inviteForm.roleCode && roleOptions.value.length > 0) {
      inviteForm.roleCode = roleOptions.value[0].code
    }
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    pageError.value = detail || 'Could not load access operations.'
  } finally {
    loading.value = false
  }
}

async function submitInvite() {
  if (!tenantId.value || !validateInviteForm()) {
    return
  }

  submitting.value = true
  submitError.value = ''

  try {
    const created = await inviteUser({
      email: inviteForm.email,
      role_code: inviteForm.roleCode,
      tenant_id: tenantId.value,
    })
    latestInvite.value = {
      ...created,
      acceptUrl: created.invite_token ? buildAcceptUrl(created.invite_token) : null,
    }
    inviteForm.email = ''
    await loadAccessConsole()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    submitError.value = detail || 'Invitation failed.'
  } finally {
    submitting.value = false
  }
}

async function cancelInvite(invitationId: string) {
  cancellingId.value = invitationId
  pageError.value = ''

  try {
    await cancelInvitation(invitationId)
    await loadAccessConsole()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    pageError.value = detail || 'Could not cancel invitation.'
  } finally {
    cancellingId.value = null
  }
}

async function suspendUser(userId: string) {
  lifecycleActionId.value = `${userId}:suspend`
  pageError.value = ''
  try {
    await suspendManagedUser(userId)
    await loadAccessConsole()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    pageError.value = detail || 'Could not suspend this tenant user.'
  } finally {
    lifecycleActionId.value = null
  }
}

async function reactivateUser(userId: string) {
  lifecycleActionId.value = `${userId}:reactivate`
  pageError.value = ''
  try {
    await reactivateManagedUser(userId)
    await loadAccessConsole()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    pageError.value = detail || 'Could not reactivate this tenant user.'
  } finally {
    lifecycleActionId.value = null
  }
}

async function revokeUserSessions(userId: string) {
  lifecycleActionId.value = `${userId}:revoke`
  pageError.value = ''
  try {
    await revokeManagedUserSessions(userId)
    await loadAccessConsole()
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    pageError.value = detail || 'Could not revoke sessions for this tenant user.'
  } finally {
    lifecycleActionId.value = null
  }
}

async function copyLatestInviteLink() {
  if (!latestInvite.value?.acceptUrl) return
  await navigator.clipboard.writeText(latestInvite.value.acceptUrl)
  copiedInviteId.value = latestInvite.value.invitation_id
}

watch(tenantId, (nextTenantId, previousTenantId) => {
  if (nextTenantId && nextTenantId !== previousTenantId) {
    void loadAccessConsole()
  }
})

onMounted(() => {
  void loadAccessConsole()
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

.invite-link-box {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.85rem;
  background: #f8fafc;
  padding: 0.9rem;
  word-break: break-all;
}

.empty-state {
  border: 1px dashed var(--om-border, #d9e2ec);
  border-radius: 1rem;
  padding: 2rem 1.5rem;
  text-align: center;
  background: #fbfdff;
}
</style>
