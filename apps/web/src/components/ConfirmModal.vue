<template>
  <div class="modal fade" tabindex="-1" ref="modalRef" data-bs-backdrop="static">
    <div class="modal-dialog modal-sm modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header border-0 pb-0">
          <h5 class="modal-title">{{ title }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" @click="$emit('cancel')"></button>
        </div>
        <div class="modal-body">
          <p class="mb-0">{{ message }}</p>
        </div>
        <div class="modal-footer border-0 pt-0">
          <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal" @click="$emit('cancel')">Cancel</button>
          <button type="button" class="btn btn-sm btn-danger" @click="handleConfirm" :disabled="busy">
            {{ busy ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as bootstrap from 'bootstrap'

const props = defineProps<{
  title: string
  message: string
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const busy = ref(false)
const modalRef = ref<HTMLElement | null>(null)
let modalInstance: bootstrap.Modal | null = null

onMounted(() => {
  if (modalRef.value) {
    modalInstance = new bootstrap.Modal(modalRef.value)
    modalInstance.show()
  }
})

function handleConfirm() {
  busy.value = true
  emit('confirm')
}

function hide() {
  modalInstance?.hide()
}

defineExpose({ hide, busy })
</script>
