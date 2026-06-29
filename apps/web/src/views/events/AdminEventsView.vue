<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">Events</h1>
        <p class="text-muted small mb-0">Manage organization calendar events</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary btn-sm" @click="exportEvents" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>Export CSV
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createEventModal">
          <i class="bi bi-plus-circle me-1"></i>Add event
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-3" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="events.length > 0" class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle" aria-label="Events list">
          <thead class="table-light">
            <tr>
              <th class="ps-4" scope="col">Title</th>
              <th scope="col">Start</th>
              <th scope="col">End</th>
              <th scope="col">Location</th>
              <th scope="col">Visibility</th>
              <th scope="col">Status</th>
              <th class="text-end pe-4" scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="event in events" :key="event.id">
              <td class="ps-4 fw-medium">{{ event.title }}</td>
              <td class="small">{{ formatDate(event.start_at) }}</td>
              <td class="small">{{ event.end_at ? formatDate(event.end_at) : '—' }}</td>
              <td class="small text-muted">{{ event.location || '—' }}</td>
              <td>
                <span class="badge bg-info-subtle text-info border border-info-subtle">{{ event.visibility_scope }}</span>
              </td>
              <td>
                <span class="badge"
                  :class="event.status === 'published' ? 'bg-success-subtle text-success' : event.status === 'cancelled' ? 'bg-danger-subtle text-danger' : 'bg-secondary-subtle text-secondary'">
                  {{ event.status }}
                </span>
              </td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-secondary me-1" aria-label="Edit event" @click="editEvent(event)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" aria-label="Delete event" @click="confirmDelete(event)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="empty-state">
      <i class="bi bi-calendar-event display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">No events yet</p>
      <p class="text-muted mb-0">Create events for your organization members.</p>
    </div>

    <!-- Create Event Modal -->
    <div class="modal fade" id="createEventModal" tabindex="-1" aria-labelledby="createEventModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="createEventModalLabel">Add event</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Title</label>
              <input v-model="form.title" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Description</label>
              <textarea v-model="form.description" class="form-control form-control-sm" rows="3"></textarea>
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">Start</label>
                <input v-model="form.start_at" type="datetime-local" class="form-control form-control-sm" required />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">End</label>
                <input v-model="form.end_at" type="datetime-local" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Location</label>
              <input v-model="form.location" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Visibility</label>
              <select v-model="form.visibility_scope" class="form-select form-select-sm">
                <option value="members_only">Members only</option>
                <option value="tenant_public">Tenant public</option>
                <option value="admin_only">Admin only</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleCreate" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Event Modal -->
    <div class="modal fade" id="editEventModal" tabindex="-1" aria-labelledby="editEventModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editEventModalLabel">Edit event</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Title</label>
              <input v-model="editForm.title" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Description</label>
              <textarea v-model="editForm.description" class="form-control form-control-sm" rows="3"></textarea>
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">Start</label>
                <input v-model="editForm.start_at" type="datetime-local" class="form-control form-control-sm" />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">End</label>
                <input v-model="editForm.end_at" type="datetime-local" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Location</label>
              <input v-model="editForm.location" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Visibility</label>
              <select v-model="editForm.visibility_scope" class="form-select form-select-sm">
                <option value="members_only">Members only</option>
                <option value="tenant_public">Tenant public</option>
                <option value="admin_only">Admin only</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Status</label>
              <select v-model="editForm.status" class="form-select form-select-sm">
                <option value="published">Published</option>
                <option value="draft">Draft</option>
                <option value="cancelled">Cancelled</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleUpdate" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue'
import * as bootstrap from 'bootstrap'
import { listAllEvents, createEvent, updateEvent, deleteEvent, exportEventsCsv, type EventResponse } from '@/api/events.api'
import { useCsvExport } from '@/composables/useCsvExport'

const loading = ref(true)
const error = ref('')
const saving = ref(false)
const events = ref<EventResponse[]>([])
const editingId = ref<string | null>(null)

function setError(err: unknown) {
  error.value = (err as any)?.response?.data?.detail || (err as any)?.message || 'An unexpected error occurred'
}

const form = ref({ title: '', description: '', start_at: '', end_at: '', location: '', visibility_scope: 'members_only' })
const editForm = ref({ title: '', description: '', start_at: '', end_at: '', location: '', visibility_scope: 'members_only', status: 'published' })

const { exportCsv, exporting } = useCsvExport()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadEvents() {
  try {
    events.value = await listAllEvents()
  } catch (err) { setError(err) }
  finally { loading.value = false }
}

function toLocalDatetime(dateStr: string): string {
  const d = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function handleCreate() {
  saving.value = true
  try {
    await createEvent({ ...form.value, start_at: new Date(form.value.start_at).toISOString(), end_at: form.value.end_at ? new Date(form.value.end_at).toISOString() : null })
    await loadEvents()
    const modal = bootstrap.Modal.getInstance(document.getElementById('createEventModal')!)
    modal?.hide()
    form.value = { title: '', description: '', start_at: '', end_at: '', location: '', visibility_scope: 'members_only' }
  } finally { saving.value = false }
}

function editEvent(event: EventResponse) {
  editingId.value = event.id
  editForm.value = {
    title: event.title,
    description: event.description || '',
    start_at: toLocalDatetime(event.start_at),
    end_at: event.end_at ? toLocalDatetime(event.end_at) : '',
    location: event.location || '',
    visibility_scope: event.visibility_scope,
    status: event.status,
  }
  nextTick(() => new bootstrap.Modal(document.getElementById('editEventModal')!).show())
}

async function handleUpdate() {
  if (!editingId.value) return
  saving.value = true
  try {
    const payload: any = { ...editForm.value }
    if (payload.start_at) payload.start_at = new Date(payload.start_at).toISOString()
    if (payload.end_at) payload.end_at = new Date(payload.end_at).toISOString()
    await updateEvent(editingId.value, payload)
    await loadEvents()
    bootstrap.Modal.getInstance(document.getElementById('editEventModal')!)?.hide()
  } finally { saving.value = false }
}

function confirmDelete(event: EventResponse) {
  if (confirm(`Delete event "${event.title}"?`)) {
    deleteEvent(event.id).then(loadEvents)
  }
}

async function exportEvents() {
  try {
    await exportCsv(exportEventsCsv, 'events.csv')
  } catch (err) { setError(err) }
}

onMounted(loadEvents)
</script>
