<template>
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
              <div class="table-responsive">
                <table class="table table-sm small mb-0">
                  <thead><tr><th>{{ t('common.row') }}</th><th>{{ t('common.errorColumn') }}</th></tr></thead>
                  <tbody>
                    <tr v-for="err in importResult.errors" :key="err.row">
                      <td>{{ err.row }}</td>
                      <td><div class="text-break">{{ err.message }}</div></td>
                    </tr>
                  </tbody>
                </table>
              </div>
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
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { importMembersCsv, type ImportResult } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { memberErrorMessage } from '../memberErrors'

const emit = defineEmits<{
  imported: []
  error: [message: string]
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const importSelectedFile = ref<File | null>(null)
const importDryRun = ref(true)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)
const importFileInput = ref<HTMLInputElement | null>(null)

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
  } catch (err) {
    emit('error', memberErrorMessage(err))
  } finally {
    importing.value = false
  }
}

async function confirmImport() {
  importDryRun.value = false
  await handleImport()
  if (importResult.value && importResult.value.error_count > 0) {
    importDryRun.value = true
  } else if (importResult.value) {
    emit('imported')
  }
}
</script>
