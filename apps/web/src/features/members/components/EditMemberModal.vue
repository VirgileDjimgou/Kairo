<template>
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
              <option value="active">{{ t('members.status.active') }}</option>
              <option value="inactive">{{ t('members.status.inactive') }}</option>
              <option value="suspended">{{ t('members.status.suspended') }}</option>
              <option value="resigned">{{ t('members.status.resigned') }}</option>
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
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import * as bootstrap from 'bootstrap'
import { updateMember, type MembershipProfileResponse, type UpdateMemberPayload } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { memberErrorMessage } from '../memberErrors'

const emit = defineEmits<{
  saved: []
  error: [message: string]
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const editingId = ref<string | null>(null)
const editForm = ref<UpdateMemberPayload>({})
const saving = ref(false)

function open(member: MembershipProfileResponse) {
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
    const modal = bootstrap.Modal.getInstance(document.getElementById('editMemberModal')!)
    modal?.hide()
    emit('saved')
  } catch (err) {
    emit('error', memberErrorMessage(err))
  } finally {
    saving.value = false
  }
}

defineExpose({ open })
</script>
