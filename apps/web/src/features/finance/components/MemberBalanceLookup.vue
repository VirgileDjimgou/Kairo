<template>
  <div class="card shadow-sm border-0 mb-4">
    <div class="card-body p-4">
      <div class="d-flex align-items-center justify-content-between mb-3">
        <h2 class="h6 fw-bold mb-0">{{ t('finance.memberLookup') }}</h2>
        <span class="badge text-bg-light border text-dark">{{ members.length }} {{ t('finance.membersCountSuffix') }}</span>
      </div>

      <div class="mb-3">
        <label for="finance-member-search" class="form-label small fw-medium">{{ t('common.member') }}</label>
        <div class="position-relative mb-2">
          <input id="finance-member-search" v-model.trim="memberSearch" class="form-control" :placeholder="t('finance.memberSearchPlaceholder')" @focus="showMemberResults = true" />
          <div v-if="showMemberResults && memberSearch" class="list-group position-absolute w-100 shadow-sm finance-member-results">
            <button v-for="member in filteredMembers.slice(0, 8)" :key="member.id" class="list-group-item list-group-item-action text-start" type="button" @click="selectMember(member)">
              <span class="fw-semibold">{{ member.display_name }}</span><span class="small text-muted ms-2">{{ member.member_code }}</span>
            </button>
            <div v-if="filteredMembers.length === 0" class="list-group-item small text-muted">{{ t('finance.noMemberFound') }}</div>
          </div>
        </div>
        <select
          id="finance-balance-member"
          v-model="selectedMemberId"
          class="form-select"
          @change="selectMemberById"
        >
          <option value="">{{ t('finance.selectMember') }}</option>
          <option v-for="member in members" :key="member.id" :value="member.id">
            {{ member.display_name }} ({{ member.member_code }})
          </option>
        </select>
      </div>

      <div v-if="selectedBalance" class="border rounded-3 p-3 bg-light-subtle" data-testid="finance-member-balance">
        <div class="fw-semibold mb-1">{{ selectedBalance.profile.display_name }}</div>
        <div class="small text-muted mb-3">{{ selectedBalance.profile.member_code }}</div>
        <div class="row g-2 small">
          <div class="col-6">
            <div class="text-muted">{{ t('contributions.expected') }}</div>
            <div class="fw-semibold">{{ selectedBalance.total_expected }} EUR</div>
          </div>
          <div class="col-6">
            <div class="text-muted">{{ t('contributions.paid') }}</div>
            <div class="fw-semibold">{{ selectedBalance.total_paid }} EUR</div>
          </div>
          <div class="col-12">
            <div class="text-muted">{{ t('contributions.balance') }}</div>
            <div class="fw-semibold" :class="Number(selectedBalance.total_balance) > 0 ? 'text-danger' : 'text-success'">
              {{ selectedBalance.total_balance }} EUR
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-muted small mb-0">
        {{ t('finance.selectMemberHint') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MemberBalanceResponse, MembershipProfileResponse } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'

const props = defineProps<{
  members: MembershipProfileResponse[]
  selectedBalance: MemberBalanceResponse | null
}>()

const emit = defineEmits<{ 'member-selected': [] }>()
const selectedMemberId = defineModel<string>('selectedMemberId', { required: true })

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

const memberSearch = ref('')
const showMemberResults = ref(false)

const filteredMembers = computed(() => {
  const query = memberSearch.value.toLocaleLowerCase()
  if (!query) return props.members
  return props.members.filter((member) =>
    `${member.display_name} ${member.first_name} ${member.last_name} ${member.member_code} ${member.phone || ''} ${member.email || ''}`
      .toLocaleLowerCase()
      .includes(query),
  )
})

function selectMember(member: MembershipProfileResponse) {
  selectedMemberId.value = member.id
  memberSearch.value = member.display_name
  showMemberResults.value = false
  emit('member-selected')
}

function selectMemberById() {
  const member = props.members.find((item) => item.id === selectedMemberId.value)
  if (member) selectMember(member)
  else emit('member-selected')
}
</script>

<style scoped>
.finance-member-results { z-index: 1040; max-height: 17rem; overflow-y: auto; }
</style>
