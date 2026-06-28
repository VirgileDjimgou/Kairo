<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">Announcements</h1>
        <p class="text-muted small mb-0">Manage organization announcements</p>
      </div>
      <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createModal">
        <i class="bi bi-plus-circle me-1"></i>Add announcement
      </button>
    </div>

    <div v-if="loading" class="text-center py-5 text-muted">Loading announcements...</div>

    <div v-else class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th class="ps-4">Title</th>
              <th>Published</th>
              <th>Expires</th>
              <th>Visibility</th>
              <th class="text-end pe-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in announcements" :key="a.id">
              <td class="ps-4 fw-medium">{{ a.title }}</td>
              <td class="small">{{ a.published_at ? formatDate(a.published_at) : '—' }}</td>
              <td class="small">{{ a.expires_at ? formatDate(a.expires_at) : '—' }}</td>
              <td>
                <span class="badge bg-info-subtle text-info border border-info-subtle">{{ a.visibility_scope }}</span>
              </td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-secondary me-1" @click="editItem(a)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="confirmDelete(a)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="announcements.length === 0">
              <td colspan="5" class="text-center text-muted py-4">No announcements yet</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal fade" id="createModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingId ? 'Edit' : 'Add' }} announcement</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Title</label>
              <input v-model="form.title" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Body</label>
              <textarea v-model="form.body" class="form-control form-control-sm" rows="4" required></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Visibility</label>
              <select v-model="form.visibility_scope" class="form-select form-select-sm">
                <option value="members_only">Members only</option>
                <option value="tenant_public">Tenant public</option>
                <option value="admin_only">Admin only</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Expires at (optional)</label>
              <input v-model="form.expires_at" type="datetime-local" class="form-control form-control-sm" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleSave" :disabled="saving">
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
import { listAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement, type AnnouncementResponse } from '@/api/announcements.api'

const loading = ref(true)
const saving = ref(false)
const announcements = ref<AnnouncementResponse[]>([])
const editingId = ref<string | null>(null)

const form = ref({ title: '', body: '', visibility_scope: 'members_only', expires_at: '' })

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function load() {
  try {
    announcements.value = await listAnnouncements()
  } finally { loading.value = false }
}

async function handleSave() {
  saving.value = true
  try {
    const payload: any = { ...form.value }
    if (payload.expires_at) payload.expires_at = new Date(payload.expires_at).toISOString()
    else payload.expires_at = null
    if (editingId.value) {
      await updateAnnouncement(editingId.value, payload)
    } else {
      await createAnnouncement(payload)
    }
    await load()
    const modal = bootstrap.Modal.getInstance(document.getElementById('createModal')!)
    modal?.hide()
    form.value = { title: '', body: '', visibility_scope: 'members_only', expires_at: '' }
    editingId.value = null
  } finally { saving.value = false }
}

function editItem(a: AnnouncementResponse) {
  editingId.value = a.id
  form.value = {
    title: a.title,
    body: a.body,
    visibility_scope: a.visibility_scope,
    expires_at: a.expires_at ? a.expires_at.slice(0, 16) : '',
  }
  nextTick(() => new bootstrap.Modal(document.getElementById('createModal')!).show())
}

function confirmDelete(a: AnnouncementResponse) {
  if (confirm(`Delete announcement "${a.title}"?`)) {
    deleteAnnouncement(a.id).then(load)
  }
}

onMounted(load)
</script>
