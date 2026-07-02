<template>
  <div class="p-4 p-lg-5">
    <div class="sports-hero rounded-4 p-4 p-lg-5 mb-4" data-testid="sports-workspace-hero">
      <div class="d-flex flex-column flex-xl-row justify-content-between gap-4 align-items-xl-end">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">Sports manager</div>
          <h1 class="h3 fw-bold mb-2">Sports workspace</h1>
          <p class="text-muted mb-0 hero-copy">
            Plan training sessions, fixtures, and club activities from a focused workspace that stays inside the sports remit.
          </p>
        </div>
        <div class="d-flex gap-2 align-items-start">
          <button class="btn btn-outline-secondary btn-sm" type="button" @click="refresh" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            Refresh
          </button>
          <button class="btn btn-primary btn-sm" type="button" @click="resetForm">
            <i class="bi bi-plus-circle me-1"></i>New sports event
          </button>
        </div>
      </div>

      <div class="row g-3 mt-3">
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">Total events</div>
            <div class="fs-4 fw-bold">{{ totalEvents }}</div>
            <div class="small text-secondary">Sports-tagged entries in this tenant.</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">Published</div>
            <div class="fs-4 fw-bold">{{ publishedEvents }}</div>
            <div class="small text-secondary">Visible to members when published.</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">Upcoming</div>
            <div class="fs-4 fw-bold">{{ upcomingEvents }}</div>
            <div class="small text-secondary">Starting on or after today.</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <div class="row g-4">
      <div class="col-xl-4">
        <div class="card shadow-sm border-0" data-testid="sports-event-form">
          <div class="card-body p-4">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-1">Editor</div>
                <h2 class="h6 fw-bold mb-0">{{ editingId ? 'Edit sports event' : 'Create sports event' }}</h2>
              </div>
              <span class="badge text-bg-light border text-dark">{{ editingId ? 'Editing' : 'New' }}</span>
            </div>

            <form class="vstack gap-3" @submit.prevent="handleSubmit">
              <div>
                <label class="form-label small fw-medium" for="sports-title">Title</label>
                <input id="sports-title" v-model="form.title" class="form-control form-control-sm" required />
              </div>
              <div>
                <label class="form-label small fw-medium" for="sports-sport-type">Sport type</label>
                <input id="sports-sport-type" v-model="form.sport_type" class="form-control form-control-sm" placeholder="training, match, camp" />
              </div>
              <div>
                <label class="form-label small fw-medium" for="sports-description">Description</label>
                <textarea id="sports-description" v-model="form.description" class="form-control form-control-sm" rows="3"></textarea>
              </div>
              <div class="row g-2">
                <div class="col-6">
                  <label class="form-label small fw-medium" for="sports-start">Start</label>
                  <input id="sports-start" v-model="form.start_at" type="datetime-local" class="form-control form-control-sm" required />
                </div>
                <div class="col-6">
                  <label class="form-label small fw-medium" for="sports-end">End</label>
                  <input id="sports-end" v-model="form.end_at" type="datetime-local" class="form-control form-control-sm" />
                </div>
              </div>
              <div>
                <label class="form-label small fw-medium" for="sports-location">Location</label>
                <input id="sports-location" v-model="form.location" class="form-control form-control-sm" />
              </div>
              <div>
                <label class="form-label small fw-medium" for="sports-visibility">Visibility</label>
                <select id="sports-visibility" v-model="form.visibility_scope" class="form-select form-select-sm">
                  <option value="members_only">Members only</option>
                  <option value="tenant_public">Tenant public</option>
                  <option value="role_restricted">Role restricted</option>
                  <option value="admin_only">Admin only</option>
                </select>
              </div>
              <div>
                <label class="form-label small fw-medium" for="sports-status">Status</label>
                <select id="sports-status" v-model="form.status" class="form-select form-select-sm">
                  <option value="published">Published</option>
                  <option value="draft">Draft</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div class="d-flex gap-2 pt-1">
                <button class="btn btn-primary btn-sm" type="submit" :disabled="saving">
                  {{ saving ? 'Saving...' : editingId ? 'Update event' : 'Create event' }}
                </button>
                <button class="btn btn-outline-secondary btn-sm" type="button" @click="resetForm">
                  Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-8">
        <div class="card shadow-sm border-0">
          <div class="card-body p-0">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="events.length === 0" class="empty-state p-5">
              <i class="bi bi-trophy display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No sports events yet</p>
              <p class="text-muted mb-0">Create the first sports session, match, or training activity from the form.</p>
            </div>

            <div v-else class="table-responsive" data-testid="sports-events-table">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4" scope="col">Title</th>
                    <th scope="col">Sport type</th>
                    <th scope="col">Start</th>
                    <th scope="col">Location</th>
                    <th scope="col">Visibility</th>
                    <th scope="col">Status</th>
                    <th class="text-end pe-4" scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="event in events" :key="event.id">
                    <td class="ps-4 fw-medium">{{ event.title }}</td>
                    <td class="small text-muted">{{ sportType(event) }}</td>
                    <td class="small">{{ formatDate(event.start_at) }}</td>
                    <td class="small text-muted">{{ event.location || '—' }}</td>
                    <td>
                      <span class="badge bg-info-subtle text-info border border-info-subtle">{{ event.visibility_scope }}</span>
                    </td>
                    <td>
                      <span class="badge" :class="statusBadgeClass(event.status)">{{ event.status }}</span>
                    </td>
                    <td class="text-end pe-4">
                      <button class="btn btn-sm btn-outline-secondary me-1" type="button" aria-label="Edit sports event" @click="editEvent(event)">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger" type="button" aria-label="Delete sports event" @click="confirmDelete(event)">
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ConfirmModal
      v-if="showDeleteModal && deletingEvent"
      title="Delete sports event"
      :message="`Delete sports event &quot;${deletingEvent.title}&quot;?`"
      @confirm="handleDelete"
      @cancel="showDeleteModal = false; deletingEvent = null"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import {
  createSportsEvent,
  deleteSportsEvent,
  listSportsEvents,
  updateSportsEvent,
  type EventResponse,
} from '@/api/events.api'

type SportsEventForm = {
  title: string
  description: string
  start_at: string
  end_at: string
  location: string
  visibility_scope: string
  status: string
  sport_type: string
}

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const events = ref<EventResponse[]>([])
const editingId = ref<string | null>(null)
const showDeleteModal = ref(false)
const deletingEvent = ref<EventResponse | null>(null)

const form = ref<SportsEventForm>({
  title: '',
  description: '',
  start_at: '',
  end_at: '',
  location: '',
  visibility_scope: 'members_only',
  status: 'published',
  sport_type: 'training',
})

const totalEvents = computed(() => events.value.length)
const publishedEvents = computed(() => events.value.filter((event) => event.status === 'published').length)
const upcomingEvents = computed(
  () => events.value.filter((event) => new Date(event.start_at).getTime() >= Date.now()).length,
)

function sportType(event: EventResponse): string {
  const raw = event.metadata_json?.sport_type
  return typeof raw === 'string' && raw.length > 0 ? raw : 'training'
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

function statusBadgeClass(status: string): string {
  const map: Record<string, string> = {
    published: 'bg-success-subtle text-success',
    draft: 'bg-secondary-subtle text-secondary',
    cancelled: 'bg-danger-subtle text-danger',
    completed: 'bg-info-subtle text-info',
  }
  return map[status] || 'bg-light text-dark'
}

function toLocalDatetime(value: string): string {
  const date = new Date(value)
  const pad = (input: number) => input.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function resetForm() {
  editingId.value = null
  deletingEvent.value = null
  showDeleteModal.value = false
  form.value = {
    title: '',
    description: '',
    start_at: '',
    end_at: '',
    location: '',
    visibility_scope: 'members_only',
    status: 'published',
    sport_type: 'training',
  }
}

function editEvent(event: EventResponse) {
  editingId.value = event.id
  form.value = {
    title: event.title,
    description: event.description || '',
    start_at: toLocalDatetime(event.start_at),
    end_at: event.end_at ? toLocalDatetime(event.end_at) : '',
    location: event.location || '',
    visibility_scope: event.visibility_scope,
    status: event.status,
    sport_type: sportType(event),
  }
}

function confirmDelete(event: EventResponse) {
  deletingEvent.value = event
  showDeleteModal.value = true
}

async function loadEvents() {
  try {
    events.value = await listSportsEvents()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load sports events.'
  } finally {
    loading.value = false
  }
}

async function refresh() {
  loading.value = true
  error.value = ''
  await loadEvents()
}

async function handleSubmit() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      title: form.value.title.trim(),
      description: form.value.description.trim() || null,
      start_at: new Date(form.value.start_at).toISOString(),
      end_at: form.value.end_at ? new Date(form.value.end_at).toISOString() : null,
      location: form.value.location.trim() || null,
      visibility_scope: form.value.visibility_scope,
      status: form.value.status,
      metadata_json: {
        sport_type: form.value.sport_type.trim() || 'training',
      },
    }

    if (editingId.value) {
      await updateSportsEvent(editingId.value, payload)
    } else {
      await createSportsEvent(payload)
    }

    await loadEvents()
    resetForm()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to save the sports event.'
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!deletingEvent.value) return
  try {
    await deleteSportsEvent(deletingEvent.value.id)
    await loadEvents()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to delete the sports event.'
  } finally {
    showDeleteModal.value = false
    deletingEvent.value = null
  }
}

onMounted(loadEvents)
</script>

<style scoped>
.sports-hero {
  background:
    radial-gradient(circle at top right, rgba(255, 215, 0, 0.22), transparent 28%),
    radial-gradient(circle at bottom left, rgba(37, 99, 235, 0.12), transparent 32%),
    linear-gradient(135deg, #f7fafc 0%, #ffffff 72%);
  border: 1px solid #e3e8ef;
}

.hero-copy {
  max-width: 44rem;
}

.metric-card {
  border: 1px solid #dbe3ed;
  border-radius: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.85);
}
</style>
