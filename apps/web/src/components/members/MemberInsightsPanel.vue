<template>
  <aside class="member-insights-panel card shadow-sm border-0" :aria-label="t('members.detailsTitle')">
    <div class="card-body p-4">
      <div class="d-flex justify-content-between gap-3 mb-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-1">{{ t('members.detailsKicker') }}</div>
          <h2 class="h5 fw-bold mb-1">{{ member.display_name }}</h2>
          <div class="small text-muted font-monospace">{{ member.member_code }}</div>
        </div>
        <button class="btn-close" type="button" :aria-label="t('common.close')" @click="$emit('close')"></button>
      </div>

      <section class="insight-section identity-section mb-3">
        <div class="d-flex justify-content-between align-items-start gap-2">
          <div>
            <div class="small text-secondary">{{ t('common.status') }}</div>
            <span class="badge" :class="member.status === 'active' ? 'text-bg-success' : 'text-bg-secondary'">{{ member.status }}</span>
          </div>
          <div class="text-end">
            <div class="small text-secondary">{{ t('members.joined') }}</div>
            <div class="small fw-semibold">{{ formatDate(member.joined_at) }}</div>
          </div>
        </div>
        <hr />
        <dl class="row mb-0 small">
          <dt class="col-5">{{ t('common.email') }}</dt><dd class="col-7 text-break">{{ member.email || '—' }}</dd>
          <dt class="col-5">{{ t('members.phone') }}</dt><dd class="col-7">{{ member.phone || '—' }}</dd>
          <dt class="col-5">{{ t('members.address') }}</dt><dd class="col-7">{{ address || '—' }}</dd>
        </dl>
      </section>

      <section v-if="canReadFinance" class="insight-section finance-section mb-3">
        <div class="d-flex align-items-center justify-content-between mb-2">
          <h3 class="h6 fw-bold mb-0"><i class="bi bi-wallet2 me-2"></i>{{ t('members.financeHistory') }}</h3>
          <span v-if="loadingFinance" class="spinner-border spinner-border-sm text-primary" aria-hidden="true"></span>
        </div>
        <template v-if="statement">
          <div class="row g-2 mb-3 text-center small">
            <div class="col-4"><div class="metric expected"><span>{{ t('contributions.expected') }}</span><strong>{{ statement.summary.total_expected }} €</strong></div></div>
            <div class="col-4"><div class="metric paid"><span>{{ t('contributions.paid') }}</span><strong>{{ statement.summary.total_paid }} €</strong></div></div>
            <div class="col-4"><div class="metric balance"><span>{{ t('contributions.balance') }}</span><strong>{{ statement.summary.total_balance }} €</strong></div></div>
          </div>
          <div v-if="statement.contributions.length" class="history-list">
            <div v-for="item in statement.contributions" :key="item.id" class="history-row">
              <div><strong>{{ item.year }}</strong><div class="small text-secondary">{{ item.status }}</div></div>
              <div class="text-end"><div>{{ item.paid_amount }} / {{ item.expected_amount }} €</div><strong :class="Number(item.balance) > 0 ? 'text-danger' : 'text-success'">{{ item.balance }} €</strong></div>
            </div>
          </div>
          <p v-else class="small text-muted mb-0">{{ t('members.noFinanceHistory') }}</p>
        </template>
      </section>

      <section v-if="canReadDisciplinary" class="insight-section discipline-section">
        <div class="d-flex align-items-center justify-content-between mb-2">
          <h3 class="h6 fw-bold mb-0"><i class="bi bi-shield-exclamation me-2"></i>{{ t('members.disciplinaryHistory') }}</h3>
          <span v-if="loadingDisciplinary" class="spinner-border spinner-border-sm text-primary" aria-hidden="true"></span>
        </div>
        <div v-if="disciplinaryRecords.length" class="history-list">
          <div v-for="record in disciplinaryRecords" :key="record.id" class="history-row">
            <div><strong>{{ record.title }}</strong><div class="small text-secondary">{{ formatDate(record.recorded_at) }} · {{ record.status }}</div><div v-if="record.description" class="small mt-1">{{ record.description }}</div></div>
            <strong class="text-danger text-nowrap">{{ record.amount }} {{ record.currency }}</strong>
          </div>
        </div>
        <p v-else class="small text-muted mb-0">{{ t('members.noDisciplinaryHistory') }}</p>
      </section>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { getMemberStatement, type MemberStatementResponse, type MembershipProfileResponse } from '@/api/membership.api'
import { listDisciplinaryRecords, type DisciplinaryRecordResponse } from '@/api/disciplinary.api'
import { useLocaleStore } from '@/stores/locale.store'

const props = defineProps<{ member: MembershipProfileResponse; canReadFinance: boolean; canReadDisciplinary: boolean }>()
defineEmits<{ close: [] }>()
const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const statement = ref<MemberStatementResponse | null>(null)
const disciplinaryRecords = ref<DisciplinaryRecordResponse[]>([])
const loadingFinance = ref(false)
const loadingDisciplinary = ref(false)
const address = computed(() => [props.member.street_name, props.member.house_number, props.member.postal_code, props.member.city].filter(Boolean).join(', '))

function formatDate(value: string) { return new Date(value).toLocaleDateString(localeStore.currentLocale === 'fr' ? 'fr-FR' : localeStore.currentLocale === 'de' ? 'de-DE' : 'en-US') }

async function load() {
  statement.value = null
  disciplinaryRecords.value = []
  if (props.canReadFinance) {
    loadingFinance.value = true
    try { statement.value = await getMemberStatement(props.member.id) } finally { loadingFinance.value = false }
  }
  if (props.canReadDisciplinary) {
    loadingDisciplinary.value = true
    try { disciplinaryRecords.value = (await listDisciplinaryRecords()).filter((record) => record.membership_profile_id === props.member.id) } finally { loadingDisciplinary.value = false }
  }
}

watch(() => props.member.id, load, { immediate: true })
</script>

<style scoped>
.member-insights-panel { position: sticky; top: 1rem; }
.insight-section { border: 1px solid var(--bs-border-color); border-radius: 1rem; padding: 1rem; }
.identity-section { background: var(--bs-light-bg-subtle); }
.finance-section { border-color: #b8d6ff; background: #f7fbff; }
.discipline-section { border-color: #f1cfb7; background: #fffaf6; }
.metric { border-radius: .75rem; padding: .5rem .25rem; display: grid; gap: .2rem; }
.metric span { color: var(--bs-secondary-color); font-size: .72rem; }
.metric.expected { background: #dcecff; }.metric.paid { background: #d9f2e5; }.metric.balance { background: #fff0c8; }
.history-list { display: grid; gap: .5rem; max-height: 20rem; overflow-y: auto; }
.history-row { display: flex; justify-content: space-between; gap: .75rem; border-top: 1px solid var(--bs-border-color); padding-top: .65rem; }
@media (max-width: 1199.98px) { .member-insights-panel { position: static; } }
</style>
