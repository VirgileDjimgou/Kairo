<template>
  <ResponsiveDataView
    class="card shadow-sm border-0"
    :items="members"
    :item-key="(member) => member.id"
    :mobile-aria-label="t('members.title')"
  >
    <template #thead>
      <tr>
        <th class="ps-4" scope="col">{{ t('members.code') }}</th>
        <th scope="col">{{ t('common.name') }}</th>
        <th scope="col">{{ t('common.email') }}</th>
        <th scope="col">{{ t('common.status') }}</th>
        <th scope="col">{{ t('members.joined') }}</th>
        <th class="text-end pe-4" scope="col">{{ t('common.actions') }}</th>
      </tr>
    </template>
    <template #rows>
      <tr v-for="member in members" :key="member.id" class="member-row" tabindex="0" @click="emit('select', member)" @keydown.enter="emit('select', member)">
        <td class="ps-4 font-monospace small">{{ member.member_code }}</td>
        <td class="fw-medium">{{ member.display_name }}</td>
        <td class="small text-muted">{{ member.email || '—' }}</td>
        <td><span class="badge" :class="member.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">{{ member.status }}</span></td>
        <td class="small">{{ formatMemberDate(member.joined_at) }}</td>
        <td class="text-end pe-4">
          <button class="btn btn-sm btn-outline-secondary me-1" :aria-label="t('members.editMember')" @click.stop="emit('edit', member)"><i class="bi bi-pencil"></i></button>
          <button v-if="canRecoverMemberAccess && member.user_id" class="btn btn-sm btn-outline-primary me-1" :aria-label="t('members.recoverAccess')" @click.stop="emit('recover-access', member)"><i class="bi bi-key"></i></button>
          <button class="btn btn-sm btn-outline-warning me-1" :aria-label="member.status === 'active' ? t('members.pauseMember') : t('members.reactivateMember')" @click.stop="emit('toggle-pause', member)"><i :class="member.status === 'active' ? 'bi bi-pause-circle' : 'bi bi-play-circle'"></i></button>
          <button v-if="canDeleteMembers" class="btn btn-sm btn-outline-danger" :aria-label="t('members.deleteMember')" @click.stop="emit('delete', member)"><i class="bi bi-trash"></i></button>
        </td>
      </tr>
    </template>
    <template #mobile-title="{ item: member }">
      <div>{{ member.display_name }}</div>
      <div class="small text-muted font-monospace">{{ member.member_code }}</div>
    </template>
    <template #mobile-status="{ item: member }">
      <span class="badge" :class="member.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">{{ member.status }}</span>
    </template>
    <template #mobile-fields="{ item: member }">
      <div class="om-data-card-row"><span class="om-data-card-label">{{ t('common.email') }}</span><span class="om-data-card-value om-technical-value">{{ member.email || '—' }}</span></div>
      <div class="om-data-card-row"><span class="om-data-card-label">{{ t('members.joined') }}</span><span class="om-data-card-value">{{ formatMemberDate(member.joined_at) }}</span></div>
    </template>
    <template #mobile-actions="{ item: member }">
      <button class="btn btn-outline-primary" type="button" @click="emit('select', member)"><i class="bi bi-person-vcard me-2"></i>{{ t('members.viewDetails') }}</button>
      <button class="btn btn-outline-secondary" type="button" @click="emit('edit', member)"><i class="bi bi-pencil me-2"></i>{{ t('members.editMember') }}</button>
      <button v-if="canRecoverMemberAccess && member.user_id" class="btn btn-outline-primary" type="button" @click="emit('recover-access', member)"><i class="bi bi-key me-2"></i>{{ t('members.recoverAccess') }}</button>
      <button class="btn btn-outline-warning" type="button" @click="emit('toggle-pause', member)"><i :class="member.status === 'active' ? 'bi bi-pause-circle me-2' : 'bi bi-play-circle me-2'"></i>{{ member.status === 'active' ? t('members.pauseMember') : t('members.reactivateMember') }}</button>
      <button v-if="canDeleteMembers" class="btn btn-outline-danger" type="button" @click="emit('delete', member)"><i class="bi bi-trash me-2"></i>{{ t('members.deleteMember') }}</button>
    </template>
  </ResponsiveDataView>
</template>

<script setup lang="ts">
import type { MembershipProfileResponse } from '@/api/membership.api'
import ResponsiveDataView from '@/components/ui/ResponsiveDataView.vue'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { CAP_IDENTITY_ACCESS_RECOVERY, CAP_MEMBERSHIP_DELETE } from '@/config/capabilities'
import { formatMemberDate } from '../memberFormatting'

defineProps<{ members: MembershipProfileResponse[] }>()

const emit = defineEmits<{
  select: [member: MembershipProfileResponse]
  edit: [member: MembershipProfileResponse]
  'recover-access': [member: MembershipProfileResponse]
  'toggle-pause': [member: MembershipProfileResponse]
  delete: [member: MembershipProfileResponse]
}>()

const localeStore = useLocaleStore()
const authStore = useAuthStore()
const t = (key: string) => localeStore.t(key)

const canDeleteMembers = authStore.hasCapability(CAP_MEMBERSHIP_DELETE)
const canRecoverMemberAccess = authStore.hasCapability(CAP_IDENTITY_ACCESS_RECOVERY)
</script>
