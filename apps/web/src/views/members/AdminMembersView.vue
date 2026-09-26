<template>
  <div class="p-4 members-view">
    <div class="d-flex flex-column flex-md-row align-items-md-start align-items-center justify-content-between gap-3 mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">{{ t('members.title') }}</h1>
        <p class="text-muted small mb-0">{{ t('members.subtitle') }}</p>
      </div>
      <div class="d-flex flex-wrap gap-2 justify-content-end w-100 w-md-auto">
        <button v-if="canUseBulkMemberTools" class="btn btn-outline-secondary btn-sm" @click="exportMembers" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>{{ t('common.exportCsv') }}
        </button>
        <button v-if="canUseBulkMemberTools" class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#importMemberModal">
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

    <div class="input-group mb-3">
      <span class="input-group-text"><i class="bi bi-search"></i></span>
      <input v-model.trim="searchQuery" class="form-control" :placeholder="t('members.searchPlaceholder')" @input="scheduleSearch" />
      <button v-if="searchQuery" class="btn btn-outline-secondary" type="button" @click="clearSearch">{{ t('common.reset') }}</button>
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

    <div v-else class="row g-4 align-items-start">
      <div :class="selectedMember ? 'col-xl-8' : 'col-12'">
        <MemberDirectory
          :members="members"
          @select="selectMember"
          @edit="openEditMember"
          @recover-access="openAccessRecovery"
          @toggle-pause="toggleMemberPause"
          @delete="openDeleteMember"
        />
      </div>
      <div v-if="selectedMember" class="col-xl-4">
        <MemberInsightsPanel
          :member="selectedMember"
          :can-read-finance="canReadMemberFinance"
          :can-read-disciplinary="canReadMemberDiscipline"
          @close="selectedMember = null"
        />
      </div>
      <AssistedAccessRecoveryModal :member="accessRecoveryMember" @close="accessRecoveryMember = null" />
    </div>

    <CreateMemberModal @created="loadMembers" @error="setError" />
    <MemberImportModal @imported="loadMembers" @error="setError" />
    <EditMemberModal ref="editMemberModal" @saved="loadMembers" @error="setError" />
    <DeleteMemberModal ref="deleteMemberModal" @deleted="loadMembers" @error="setError" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { listMembers, updateMember, exportMembersCsv } from '@/api/membership.api'
import type { MembershipProfileResponse } from '@/api/membership.api'
import { useCsvExport } from '@/composables/useCsvExport'
import { useLocaleStore } from '@/stores/locale.store'
import { useAuthStore } from '@/stores/auth.store'
import { CAP_DISCIPLINARY_TENANT_READ, CAP_FINANCE_TENANT_READ, CAP_TENANT_ADMINISTRATION } from '@/config/capabilities'
import MemberInsightsPanel from '@/components/members/MemberInsightsPanel.vue'
import AssistedAccessRecoveryModal from '@/components/members/AssistedAccessRecoveryModal.vue'
import MemberDirectory from '@/features/members/components/MemberDirectory.vue'
import CreateMemberModal from '@/features/members/components/CreateMemberModal.vue'
import MemberImportModal from '@/features/members/components/MemberImportModal.vue'
import EditMemberModal from '@/features/members/components/EditMemberModal.vue'
import DeleteMemberModal from '@/features/members/components/DeleteMemberModal.vue'
import { notifyOperation } from '@/services/operation-notifications'
import { memberErrorMessage } from '@/features/members/memberErrors'

const localeStore = useLocaleStore()
const authStore = useAuthStore()
const canUseBulkMemberTools = authStore.hasCapability(CAP_TENANT_ADMINISTRATION)
const canReadMemberFinance = authStore.hasCapability(CAP_FINANCE_TENANT_READ)
const canReadMemberDiscipline = authStore.hasCapability(CAP_DISCIPLINARY_TENANT_READ)
const t = (key: string) => localeStore.t(key)

const loading = ref(true)
const error = ref('')
const members = ref<MembershipProfileResponse[]>([])
const selectedMember = ref<MembershipProfileResponse | null>(null)
const accessRecoveryMember = ref<MembershipProfileResponse | null>(null)
const saving = ref(false)
const searchQuery = ref('')
let searchTimer: ReturnType<typeof setTimeout> | undefined
const editMemberModal = ref<InstanceType<typeof EditMemberModal> | null>(null)
const deleteMemberModal = ref<InstanceType<typeof DeleteMemberModal> | null>(null)

function setError(err: unknown) {
  error.value = memberErrorMessage(err)
}

function selectMember(member: MembershipProfileResponse) {
  selectedMember.value = member
}

function openAccessRecovery(member: MembershipProfileResponse) {
  accessRecoveryMember.value = member
}

function openEditMember(member: MembershipProfileResponse) {
  editMemberModal.value?.open(member)
}

function openDeleteMember(member: MembershipProfileResponse) {
  deleteMemberModal.value?.open(member)
}

const { exportCsv, exporting } = useCsvExport()

async function exportMembers() {
  try {
    await exportCsv(exportMembersCsv, 'members.csv')
  } catch (err) { setError(err) }
}

async function loadMembers(query = searchQuery.value) {
  try {
    members.value = await listMembers(query)
  } catch (err) { setError(err) }
  finally { loading.value = false }
}

function scheduleSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadMembers(), 250)
}

function clearSearch() {
  searchQuery.value = ''
  void loadMembers('')
}

async function toggleMemberPause(member: MembershipProfileResponse) {
  saving.value = true
  try {
    const isActive = member.status === 'active'
    await updateMember(member.id, { status: isActive ? 'suspended' : 'active' })
    notifyOperation({ level: 'success', messageKey: isActive ? 'members.pauseSuccess' : 'members.reactivateSuccess' })
    await loadMembers()
  } catch (err) {
    setError(err)
    notifyOperation({ level: 'error', messageKey: 'common.error' })
  } finally {
    saving.value = false
  }
}

onMounted(loadMembers)
</script>

<style scoped>
@media (max-width: 767.98px) {
  .members-view :deep(.mobile-data-card__actions) {
    grid-template-columns: 1fr;
  }
}
</style>
