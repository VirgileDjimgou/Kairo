<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">Members</h1>
        <p class="text-muted small mb-0">Manage organization member profiles</p>
      </div>
      <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createMemberModal">
        <i class="bi bi-person-plus me-1"></i>Add member
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th class="ps-4">Code</th>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
              <th>Joined</th>
              <th class="text-end pe-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in members" :key="member.id">
              <td class="ps-4 font-monospace small">{{ member.member_code }}</td>
              <td class="fw-medium">{{ member.display_name }}</td>
              <td class="small text-muted">{{ member.email || '—' }}</td>
              <td>
                <span class="badge"
                  :class="member.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">
                  {{ member.status }}
                </span>
              </td>
              <td class="small">{{ formatDate(member.joined_at) }}</td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-secondary me-1" title="Edit"
                  @click="editMember(member)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" title="Delete"
                  @click="confirmDelete(member)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="members.length === 0">
              <td colspan="6" class="text-center text-muted py-4">
                <i class="bi bi-people me-2"></i>No member profiles yet
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Member Modal -->
    <div class="modal fade" id="createMemberModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add member</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Member code</label>
              <input v-model="form.member_code" class="form-control form-control-sm" required />
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">First name</label>
                <input v-model="form.first_name" class="form-control form-control-sm" required />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">Last name</label>
                <input v-model="form.last_name" class="form-control form-control-sm" required />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Display name</label>
              <input v-model="form.display_name" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Email</label>
              <input v-model="form.email" type="email" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Phone</label>
              <input v-model="form.phone" class="form-control form-control-sm" />
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

    <!-- Edit Member Modal -->
    <div class="modal fade" id="editMemberModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit member</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">Member code</label>
              <input v-model="editForm.member_code" class="form-control form-control-sm" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">First name</label>
                <input v-model="editForm.first_name" class="form-control form-control-sm" />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">Last name</label>
                <input v-model="editForm.last_name" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Display name</label>
              <input v-model="editForm.display_name" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Email</label>
              <input v-model="editForm.email" type="email" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Phone</label>
              <input v-model="editForm.phone" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Status</label>
              <select v-model="editForm.status" class="form-select form-select-sm">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
                <option value="resigned">Resigned</option>
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

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteMemberModal" tabindex="-1">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm delete</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0 small">Remove <strong>{{ deletingMember?.display_name }}</strong>?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-sm btn-danger" @click="handleDelete" :disabled="saving">
              {{ saving ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as bootstrap from 'bootstrap'
import { listMembers, createMember, updateMember, deleteMember } from '@/api/membership.api'
import type { MembershipProfileResponse, CreateMemberPayload, UpdateMemberPayload } from '@/api/membership.api'

const loading = ref(true)
const members = ref<MembershipProfileResponse[]>([])
const saving = ref(false)
const deletingMember = ref<MembershipProfileResponse | null>(null)

const form = ref<CreateMemberPayload>({
  member_code: '',
  first_name: '',
  last_name: '',
  display_name: '',
  email: '',
  phone: '',
})

const editForm = ref<UpdateMemberPayload>({})
const editingId = ref<string | null>(null)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadMembers() {
  try {
    members.value = await listMembers()
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

function resetForm() {
  form.value = { member_code: '', first_name: '', last_name: '', display_name: '', email: '', phone: '' }
}

async function handleCreate() {
  saving.value = true
  try {
    await createMember(form.value)
    resetForm()
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('createMemberModal')!)
    modal?.hide()
  } catch { /* handled by interceptor */ }
  finally { saving.value = false }
}

function editMember(member: MembershipProfileResponse) {
  editingId.value = member.id
  editForm.value = {
    member_code: member.member_code,
    first_name: member.first_name,
    last_name: member.last_name,
    display_name: member.display_name,
    email: member.email || '',
    phone: member.phone || '',
    status: member.status,
  }
  nextTick(() => {
    const modal = new bootstrap.Modal(document.getElementById('editMemberModal')!)
    modal.show()
  })
}

async function handleUpdate() {
  if (!editingId.value) return
  saving.value = true
  try {
    await updateMember(editingId.value, editForm.value)
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('editMemberModal')!)
    modal?.hide()
  } catch { /* handled by interceptor */ }
  finally { saving.value = false }
}

function confirmDelete(member: MembershipProfileResponse) {
  deletingMember.value = member
  nextTick(() => {
    const modal = new bootstrap.Modal(document.getElementById('deleteMemberModal')!)
    modal.show()
  })
}

async function handleDelete() {
  if (!deletingMember.value) return
  saving.value = true
  try {
    await deleteMember(deletingMember.value.id)
    await loadMembers()
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteMemberModal')!)
    modal?.hide()
  } catch { /* handled by interceptor */ }
  finally { saving.value = false; deletingMember.value = null }
}

onMounted(loadMembers)
</script>
