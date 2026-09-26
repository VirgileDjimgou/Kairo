<template>
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
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import * as bootstrap from 'bootstrap'
import { deleteMember, type MembershipProfileResponse } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { notifyOperation } from '@/services/operation-notifications'
import { memberErrorMessage } from '../memberErrors'

const emit = defineEmits<{
  deleted: []
  error: [message: string]
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const deletingMember = ref<MembershipProfileResponse | null>(null)
const saving = ref(false)

function open(member: MembershipProfileResponse) {
  deletingMember.value = member
  notifyOperation({ level: 'warning', messageKey: 'toast.deleteWarning' })
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
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteMemberModal')!)
    modal?.hide()
    emit('deleted')
  } catch (err) {
    emit('error', memberErrorMessage(err))
  } finally {
    saving.value = false
    deletingMember.value = null
  }
}

defineExpose({ open })
</script>
