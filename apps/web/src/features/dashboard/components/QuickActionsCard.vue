<template>
  <div class="card shadow-sm border-0" data-testid="dashboard-quick-actions">
    <div class="card-body p-4">
      <div class="text-uppercase small fw-semibold text-secondary mb-2">
        {{ copy.quickActions }}
      </div>
      <div class="vstack gap-2">
        <RouterLink
          v-for="action in actions"
          :key="action.to + action.label"
          :to="action.to"
          class="btn btn-outline-secondary text-start"
        >
          <i :class="action.icon" class="me-2"></i>{{ action.label }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { DashboardCopy } from '../composables/useDashboardCopy'
import type { DashboardQuickAction } from '../composables/useDashboardQuickActions'

defineProps<{
  copy: DashboardCopy
  actions: DashboardQuickAction[]
}>()
</script>
