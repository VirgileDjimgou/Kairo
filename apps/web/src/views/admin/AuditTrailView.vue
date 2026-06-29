<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">Audit</div>
        <h1 class="h4 fw-bold mb-1">Audit trail</h1>
        <p class="text-muted mb-0">
          Review sensitive administrative actions across settings, documents, memberships,
          contributions, governance, and operational tools.
        </p>
      </div>
      <div class="d-flex gap-2 align-self-start">
        <button class="btn btn-outline-secondary" type="button" @click="downloadCsv" :disabled="loading">
          Export CSV
        </button>
        <button class="btn om-primary-btn" type="button" @click="refreshEvents" :disabled="loading">
          {{ loading ? "Refreshing..." : "Refresh audit" }}
        </button>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-sm-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center py-3">
            <div class="fs-4 fw-bold">{{ stats.total }}</div>
            <div class="small text-muted">Total events</div>
          </div>
        </div>
      </div>
      <div class="col-sm-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center py-3">
            <div class="fs-4 fw-bold text-success">{{ stats.create }}</div>
            <div class="small text-muted">Creates</div>
          </div>
        </div>
      </div>
      <div class="col-sm-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center py-3">
            <div class="fs-4 fw-bold text-warning">{{ stats.update }}</div>
            <div class="small text-muted">Updates</div>
          </div>
        </div>
      </div>
      <div class="col-sm-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center py-3">
            <div class="fs-4 fw-bold text-danger">{{ stats.delete }}</div>
            <div class="small text-muted">Deletes</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-sm-6 col-lg-3">
            <label class="form-label small fw-semibold text-muted mb-1">Search</label>
            <input v-model="searchText" type="text" class="form-control form-control-sm" placeholder="Search action, entity, details..." />
          </div>
          <div class="col-sm-6 col-lg-2">
            <label class="form-label small fw-semibold text-muted mb-1">Action</label>
            <select v-model="actionFilter" class="form-select form-select-sm">
              <option value="">All</option>
              <option value="create">Create</option>
              <option value="update">Update</option>
              <option value="delete">Delete</option>
              <option value="access_updated">Document access</option>
              <option value="reindex_requested">Reindex</option>
              <option value="settings_updated">Settings</option>
              <option value="invite_created">Invite created</option>
              <option value="invite_cancelled">Invite cancelled</option>
              <option value="invite_accepted">Invite accepted</option>
              <option value="payment_recorded">Payment recorded</option>
              <option value="notification_test">Notification test</option>
            </select>
          </div>
          <div class="col-sm-6 col-lg-2">
            <label class="form-label small fw-semibold text-muted mb-1">Entity</label>
            <select v-model="entityTypeFilter" class="form-select form-select-sm">
              <option value="">All</option>
              <option value="tenant_settings">Tenant settings</option>
              <option value="document">Document</option>
              <option value="membership_profile">Member profile</option>
              <option value="contribution_record">Contribution</option>
              <option value="payment_record">Payment</option>
              <option value="policy_record">Policy</option>
              <option value="disciplinary_record">Disciplinary</option>
              <option value="event">Event</option>
              <option value="announcement">Announcement</option>
              <option value="invitation">Invitation</option>
              <option value="mfa">MFA</option>
              <option value="notification">Notification</option>
            </select>
          </div>
          <div class="col-sm-6 col-lg-2">
            <label class="form-label small fw-semibold text-muted mb-1">Actor UUID</label>
            <input v-model="actorUserId" type="text" class="form-control form-control-sm" placeholder="Optional actor id" />
          </div>
          <div class="col-sm-6 col-lg-1">
            <label class="form-label small fw-semibold text-muted mb-1">Limit</label>
            <select v-model.number="limit" class="form-select form-select-sm">
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
            </select>
          </div>
          <div class="col-sm-6 col-lg-2">
            <label class="form-label small fw-semibold text-muted mb-1">From</label>
            <input v-model="createdFrom" type="datetime-local" class="form-control form-control-sm" />
          </div>
          <div class="col-sm-6 col-lg-2">
            <label class="form-label small fw-semibold text-muted mb-1">To</label>
            <input v-model="createdTo" type="datetime-local" class="form-control form-control-sm" />
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-4">
        <div v-if="loading" class="text-muted py-5 text-center">
          Loading audit trail...
        </div>

        <div v-else-if="filteredEvents.length === 0" class="empty-state">
          <i class="bi bi-shield-check display-6 text-secondary"></i>
          <p class="mb-1 fw-semibold">No matching audit events</p>
          <p class="text-muted mb-0">Adjust the filters or trigger a sensitive action to generate new entries.</p>
        </div>

        <div v-else class="vstack gap-3">
          <article v-for="event in filteredEvents" :key="event.id" class="audit-card">
            <div class="d-flex justify-content-between gap-3 flex-wrap mb-2">
              <div>
                <div class="fw-semibold">{{ event.action }} · {{ event.entity_type }}</div>
                <div class="small text-muted">
                  {{ formatDate(event.created_at) }}
                  <span v-if="event.actor_user_id"> · actor {{ shortId(event.actor_user_id) }}</span>
                  <span v-if="event.module_key"> · {{ event.module_key }}</span>
                </div>
              </div>
              <div class="d-flex gap-2 flex-wrap">
                <span class="badge text-bg-light text-dark border">{{ event.entity_id ?? 'no entity id' }}</span>
              </div>
            </div>

            <div class="mb-2">
              <div class="small text-uppercase text-muted fw-semibold mb-1">Details</div>
              <div class="details-grid">
                <div v-for="(value, key) in event.details" :key="key" class="detail-pill">
                  <span class="detail-key">{{ key }}</span>
                  <span class="detail-value">{{ formatValue(value) }}</span>
                </div>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { exportAuditEventsCsv, listAuditEvents, type AuditEventResponse } from '@/api/audit.api'

const loading = ref(false)
const events = ref<AuditEventResponse[]>([])
const searchText = ref('')
const actionFilter = ref('')
const entityTypeFilter = ref('')
const actorUserId = ref('')
const limit = ref(50)
const createdFrom = ref('')
const createdTo = ref('')

const filteredEvents = computed(() => {
  return events.value.filter((event) => {
    if (actionFilter.value && event.action !== actionFilter.value) return false
    if (entityTypeFilter.value && event.entity_type !== entityTypeFilter.value) return false
    if (actorUserId.value && event.actor_user_id !== actorUserId.value) return false
    if (searchText.value) {
      const needle = searchText.value.toLowerCase()
      const haystack = `${event.action} ${event.entity_type} ${event.entity_id ?? ''} ${JSON.stringify(event.details)}`.toLowerCase()
      if (!haystack.includes(needle)) return false
    }
    return true
  })
})

const stats = computed(() => {
  const total = events.value.length
  return {
    total,
    create: events.value.filter((event) => event.action === 'create').length,
    update: events.value.filter((event) => event.action === 'update').length,
    delete: events.value.filter((event) => event.action === 'delete').length,
  }
})

async function refreshEvents() {
  loading.value = true
  try {
    events.value = await listAuditEvents({
      limit: limit.value,
      actor_user_id: actorUserId.value || undefined,
      action: actionFilter.value || undefined,
      entity_type: entityTypeFilter.value || undefined,
      search: searchText.value || undefined,
      created_from: toIso(createdFrom.value),
      created_to: toIso(createdTo.value),
    })
  } finally {
    loading.value = false
  }
}

async function downloadCsv() {
  const blob = await exportAuditEventsCsv({
    limit: limit.value,
    actor_user_id: actorUserId.value || undefined,
    action: actionFilter.value || undefined,
    entity_type: entityTypeFilter.value || undefined,
    search: searchText.value || undefined,
    created_from: toIso(createdFrom.value),
    created_to: toIso(createdTo.value),
  })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'audit-events.csv'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

function toIso(value: string): string | undefined {
  if (!value) return undefined
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString()
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString()
}

function shortId(value: string): string {
  return value.slice(0, 8)
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return 'null'
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return JSON.stringify(value)
}

watch([limit, actionFilter, entityTypeFilter, actorUserId, searchText, createdFrom, createdTo], () => {
  refreshEvents()
})

onMounted(async () => {
  await refreshEvents()
})
</script>

<style scoped>
.audit-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}

.details-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.detail-pill {
  display: inline-flex;
  flex-direction: column;
  gap: 0.15rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.55rem 0.75rem;
  min-width: 180px;
}

.detail-key {
  font-size: 0.72rem;
  text-transform: uppercase;
  font-weight: 700;
  color: #64748b;
}

.detail-value {
  font-size: 0.875rem;
  color: #0f172a;
  word-break: break-word;
}
</style>

