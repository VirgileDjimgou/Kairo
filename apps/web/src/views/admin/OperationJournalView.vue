<template>
  <section class="container-fluid p-4 p-lg-5">
    <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary">{{ t('operationJournal.kicker') }}</div>
        <h1 class="h3 fw-bold mb-1">{{ t('operationJournal.title') }}</h1>
        <p class="text-muted mb-0">{{ t('operationJournal.description') }}</p>
      </div>
      <button class="btn btn-outline-primary align-self-start" type="button" :disabled="loading" @click="load">
        <i class="bi bi-arrow-clockwise me-2" aria-hidden="true"></i>{{ t('common.refresh') }}
      </button>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <label class="form-label fw-semibold" for="operation-journal-search">{{ t('operationJournal.search') }}</label>
        <input id="operation-journal-search" v-model.trim="search" class="form-control mb-4" :placeholder="t('operationJournal.searchPlaceholder')" @input="scheduleLoad" />
        <div v-if="loading" class="py-5 text-center text-muted"><span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>{{ t('common.loading') }}</div>
        <div v-else-if="events.length === 0" class="py-5 text-center text-muted">{{ t('operationJournal.empty') }}</div>
        <div v-else class="table-responsive">
          <table class="table align-middle mb-0">
            <thead><tr><th>{{ t('operationJournal.date') }}</th><th>{{ t('operationJournal.operation') }}</th><th>{{ t('operationJournal.actor') }}</th><th>{{ t('operationJournal.details') }}</th></tr></thead>
            <tbody>
              <tr v-for="event in events" :key="event.id">
                <td class="text-nowrap">{{ formatDate(event.created_at) }}</td>
                <td><span class="badge" :class="event.action === 'operation_failed' ? 'text-bg-danger' : 'text-bg-success'">{{ formatAction(event) }}</span><div class="small text-muted mt-1">{{ formatEntity(event.entity_type) }}</div></td>
                <td class="small"><div class="fw-semibold">{{ formatActor(event) }}</div><div v-if="event.actor" class="text-muted">{{ formatRoles(event.actor.roles) }}</div></td>
                <td class="small text-break">{{ formatDetails(event) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { listOperationJournal, type AuditEventResponse } from '@/api/audit.api'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const t = localeStore.t
const loading = ref(false)
const search = ref('')
const events = ref<AuditEventResponse[]>([])
let searchTimer: ReturnType<typeof setTimeout> | undefined

async function load() {
  loading.value = true
  try {
    events.value = await listOperationJournal(search.value || undefined)
  } finally {
    loading.value = false
  }
}

function scheduleLoad() {
  if (searchTimer) window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => void load(), 300)
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString(localeStore.currentLocale)
}

function formatActor(event: AuditEventResponse): string {
  return event.actor?.display_name || event.actor?.email || t('operationJournal.systemActor')
}

function formatRoles(roles: string[]): string {
  if (!roles.length) return t('operationJournal.roleOrdinaryMember')
  return roles.map((role) => t(`operationJournal.role.${role}`)).join(', ')
}

function formatAction(event: AuditEventResponse): string {
  const actionKeys: Record<string, string> = {
    login_succeeded: 'operationJournal.action.loginSucceeded',
    login_failed: 'operationJournal.action.loginFailed',
    initial_password_changed: 'operationJournal.action.initialPasswordChanged',
    operation_failed: 'operationJournal.action.operationFailed',
    create: 'operationJournal.action.create',
    update: 'operationJournal.action.update',
    delete: 'operationJournal.action.delete',
  }
  return t(actionKeys[event.action] || 'operationJournal.action.recorded')
}

function formatEntity(entityType: string): string {
  const entityKeys: Record<string, string> = {
    session: 'operationJournal.entity.session',
    user: 'operationJournal.entity.user',
    membership_profile: 'operationJournal.entity.membershipProfile',
    client_request: 'operationJournal.entity.clientRequest',
  }
  return t(entityKeys[entityType] || 'operationJournal.entity.other')
}

function formatDetails(event: AuditEventResponse): string {
  const details = event.details
  if (event.action === 'login_succeeded') return t('operationJournal.detail.loginSucceeded')
  if (event.action === 'login_failed') return t('operationJournal.detail.loginFailed')
  if (event.action === 'initial_password_changed') return t('operationJournal.detail.initialPasswordChanged')
  if (event.action === 'operation_failed') {
    const path = String(details.path || '')
    const status = Number(details.status_code || 0)
    const target = path.includes('memberships') ? t('operationJournal.target.members')
      : path.includes('contributions') ? t('operationJournal.target.contributions')
        : path.includes('documents') ? t('operationJournal.target.documents')
          : t('operationJournal.target.application')
    return status === 422
      ? t('operationJournal.detail.validationFailure', { target })
      : t('operationJournal.detail.requestFailure', { target })
  }
  if (event.action === 'create' && event.entity_type === 'membership_profile') {
    const memberCode = typeof details.member_code === 'string' ? details.member_code : null
    return memberCode
      ? t('operationJournal.detail.memberCreatedWithCode', { memberCode })
      : t('operationJournal.detail.memberCreated')
  }
  return t('operationJournal.detail.recorded')
}

onMounted(() => void load())
onBeforeUnmount(() => { if (searchTimer) window.clearTimeout(searchTimer) })
</script>
