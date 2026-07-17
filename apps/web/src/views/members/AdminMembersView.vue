<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">{{ t('members.title') }}</h1>
        <p class="text-muted small mb-0">{{ t('members.subtitle') }}</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary btn-sm" @click="exportMembers" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>{{ t('common.exportCsv') }}
        </button>
        <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#importMemberModal">
          <i class="bi bi-upload me-1"></i>{{ t('common.importCsv') }}
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createMemberModal">
          <i class="bi bi-person-plus me-1"></i>{{ t('members.addMember') }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-3" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('common.loading') }}</span>
      </div>
    </div>

    <div v-else-if="members.length === 0" class="empty-state">
      <i class="bi bi-people display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">{{ t('members.noMembers') }}</p>
      <p class="text-muted mb-3">
        {{ t('members.addFirst') }}
      </p>
      <div class="d-flex flex-wrap justify-content-center gap-2">
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createMemberModal">
          {{ t('members.addFirstMember') }}
        </button>
        <button class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#importMemberModal">
          {{ t('common.importCsv') }}
        </button>
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary btn-sm">
          {{ t('members.reviewSettings') }}
        </RouterLink>
      </div>
    </div>

    <div v-else class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle" aria-label="Members list">
          <thead class="table-light">
            <tr>
              <th class="ps-4" scope="col">{{ t('members.code') }}</th>
              <th scope="col">{{ t('common.name') }}</th>
              <th scope="col">{{ t('common.email') }}</th>
              <th scope="col">{{ t('common.status') }}</th>
              <th scope="col">{{ t('members.joined') }}</th>
              <th class="text-end pe-4" scope="col">{{ t('common.actions') }}</th>
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
                <button class="btn btn-sm btn-outline-secondary me-1" :aria-label="t('members.editMember')"
                  @click="editMember(member)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" :aria-label="t('members.deleteMember')"
                  @click="confirmDelete(member)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>

          </tbody>
        </table>
      </div>
    </div>

    <!-- Import Members Modal -->
    <div class="modal fade" id="importMemberModal" tabindex="-1" aria-labelledby="importMemberModalLabel">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="importMemberModalLabel">{{ t('members.importTitle') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" @click="resetImport"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.csvFile') }}</label>
              <input ref="importFileInput" class="form-control form-control-sm" type="file" accept=".csv" @change="onImportFileChange" />
              <div class="form-text small">{{ t('members.requiredColumns') }}</div>
            </div>
            <div class="form-check mb-3">
              <input id="importDryRun" v-model="importDryRun" type="checkbox" class="form-check-input" />
              <label for="importDryRun" class="form-check-label small">{{ t('common.dryRun') }}</label>
            </div>
            <div v-if="importResult" class="mt-3">
              <hr />
              <div class="d-flex gap-3 mb-3">
                <span class="badge bg-secondary">{{ t('common.total') }}: {{ importResult.total }}</span>
                <span class="badge bg-success">{{ t('common.successCount') }}: {{ importResult.success_count }}</span>
                <span class="badge" :class="importResult.error_count > 0 ? 'bg-danger' : 'bg-success'">{{ t('common.errorCount') }}: {{ importResult.error_count }}</span>
              </div>
              <div v-if="importResult.errors.length > 0" class="mb-3">
                <h6 class="small fw-bold text-danger">{{ t('common.validationErrors') }}</h6>
                <table class="table table-sm small mb-0">
                  <thead><tr><th>{{ t('common.row') }}</th><th>{{ t('common.errorColumn') }}</th></tr></thead>
                  <tbody>
                    <tr v-for="err in importResult.errors" :key="err.row">
                      <td>{{ err.row }}</td>
                      <td>{{ err.message }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="importResult.error_count === 0 && !importDryRun" class="alert alert-success small py-2 mb-0">
                {{ t('members.successfullyImported').replace('{count}', String(importResult.success_count)) }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal" @click="resetImport">{{ t('common.cancel') }}</button>
            <button v-if="importDryRun && importResult && importResult.error_count === 0" type="button" class="btn btn-sm btn-primary" @click="confirmImport" :disabled="importing">
              {{ importing ? t('common.importing') : t('common.confirmImport') }}
            </button>
            <button v-else type="button" class="btn btn-sm btn-primary" @click="handleImport" :disabled="importing || !importSelectedFile">
              {{ importing ? t('common.importing') : importDryRun ? t('common.validate') : t('common.import') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Member Modal -->
    <div class="modal fade" id="createMemberModal" tabindex="-1" aria-labelledby="createMemberModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="createMemberModalLabel">{{ t('members.addMember') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.memberCode') }}</label>
              <input v-model="form.member_code" class="form-control form-control-sm" required />
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">{{ t('members.firstName') }}</label>
                <input v-model="form.first_name" class="form-control form-control-sm" required />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">{{ t('members.lastName') }}</label>
                <input v-model="form.last_name" class="form-control form-control-sm" required />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.displayName') }}</label>
              <input v-model="form.display_name" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.email') }}</label>
              <input v-model="form.email" type="email" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.phone') }}</label>
              <input v-model="form.phone" class="form-control form-control-sm" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleCreate" :disabled="saving">
              {{ saving ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Member Modal -->
    <div class="modal fade" id="editMemberModal" tabindex="-1" aria-labelledby="editMemberModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editMemberModalLabel">{{ t('members.editMember') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.memberCode') }}</label>
              <input v-model="editForm.member_code" class="form-control form-control-sm" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col">
                <label class="form-label small fw-medium">{{ t('members.firstName') }}</label>
                <input v-model="editForm.first_name" class="form-control form-control-sm" />
              </div>
              <div class="col">
                <label class="form-label small fw-medium">{{ t('members.lastName') }}</label>
                <input v-model="editForm.last_name" class="form-control form-control-sm" />
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.displayName') }}</label>
              <input v-model="editForm.display_name" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.email') }}</label>
              <input v-model="editForm.email" type="email" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('members.phone') }}</label>
              <input v-model="editForm.phone" class="form-control form-control-sm" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ t('common.status') }}</label>
              <select v-model="editForm.status" class="form-select form-select-sm">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
                <option value="resigned">Resigned</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleUpdate" :disabled="saving">
              {{ saving ? t('common.saving') : t('common.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteMemberModal" tabindex="-1" aria-labelledby="deleteMemberModalLabel">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteMemberModalLabel">{{ t('common.confirm') }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0 small">{{ t('members.deleteMember') }}: <strong>{{ deletingMember?.display_name }}</strong>?</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ t('common.cancel') }}</button>
            <button type="button" class="btn btn-sm btn-danger" @click="handleDelete" :disabled="saving">
              {{ saving ? t('common.loading') : t('common.delete') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import * as bootstrap from 'bootstrap'
import { listMembers, createMember, updateMember, deleteMember, importMembersCsv, exportMembersCsv } from '@/api/membership.api'
import type { MembershipProfileResponse, CreateMemberPayload, UpdateMemberPayload, ImportResult } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const loading = ref(true)
const error = ref('')
const members = ref<MembershipProfileResponse[]>([])
const saving = ref(false)
const deletingMember = ref<MembershipProfileResponse | null>(null)

function setError(err: unknown) {
  error.value = (err as any)?.response?.data?.detail || (err as any)?.message || 'An unexpected error occurred'
}

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

const importSelectedFile = ref<File | null>(null)
const importDryRun = ref(true)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)
const importFileInput = ref<HTMLInputElement | null>(null)

const { exportCsv, exporting } = useCsvExport()

function resetImport() {
  importSelectedFile.value = null
  importDryRun.value = true
  importing.value = false
  importResult.value = null
  if (importFileInput.value) importFileInput.value.value = ''
}

function onImportFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  importSelectedFile.value = input.files?.[0] ?? null
  importResult.value = null
}

async function handleImport() {
  if (!importSelectedFile.value) return
  importing.value = true
  try {
    importResult.value = await importMembersCsv(importSelectedFile.value, importDryRun.value)
  } finally { importing.value = false }
}

async function confirmImport() {
  importDryRun.value = false
  await handleImport()
  if (importResult.value && importResult.value.error_count > 0) {
    importDryRun.value = true
  } else {
    await loadMembers()
  }
}

async function exportMembers() {
  try {
    await exportCsv(exportMembersCsv, 'members.csv')
  } catch (err) { setError(err) }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadMembers() {
  try {
    members.value = await listMembers()
  } catch (err) { setError(err) }
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
  } catch (err) { setError(err) }
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
  } catch (err) { setError(err) }
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
  } catch (err) { setError(err) }
  finally { saving.value = false; deletingMember.value = null }
}

onMounted(loadMembers)
</script>
