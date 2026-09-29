<template>
  <div class="card shadow-sm border-0 mb-4" data-testid="dashboard-workspace-focus">
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis mb-2">
            {{ focus.kicker }}
          </div>
          <h2 class="h5 fw-bold mb-1">{{ focus.title }}</h2>
          <p class="text-muted mb-0">
            {{ focus.description }}
          </p>
        </div>
        <RouterLink :to="focus.primary.to" class="btn btn-primary align-self-start">
          {{ focus.primary.label }}
        </RouterLink>
      </div>

      <div class="d-flex flex-wrap gap-2 mt-3">
        <RouterLink
          v-for="action in focus.links"
          :key="action.to + action.label"
          :to="action.to"
          class="btn btn-outline-secondary btn-sm"
        >
          {{ action.label }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { WorkspaceFocus } from '../composables/useWorkspaceFocus'

defineProps<{ focus: WorkspaceFocus }>()
</script>
