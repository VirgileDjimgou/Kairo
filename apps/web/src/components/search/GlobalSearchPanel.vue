<template>
  <div class="global-search-panel">
    <form class="global-search-form" @submit.prevent="run">
      <div class="input-group">
        <span class="input-group-text" aria-hidden="true"><i class="bi bi-search"></i></span>
        <input
          ref="inputElement"
          v-model="query"
          type="search"
          class="form-control"
          :placeholder="copy.placeholder"
          :aria-label="copy.title"
          autocomplete="off"
          @keydown.esc="$emit('close')"
        />
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ copy.submit }}
        </button>
      </div>
    </form>

    <ErrorState
      v-if="errorMessage"
      :title="copy.title"
      :message="errorMessage"
      :retry-label="copy.submit"
      :retrying="loading"
      @retry="run"
    />

    <template v-else-if="searched">
      <p class="text-muted small mb-2">{{ results.length }} {{ copy.results }}</p>
      <EmptyState
        v-if="!results.length"
        icon="bi-search"
        :title="copy.emptyTitle"
        :description="copy.emptyBody"
      />
      <div v-else class="list-group global-search-results">
        <RouterLink
          v-for="row in results"
          :key="`${row.type}-${row.id}`"
          :to="row.target_path"
          class="list-group-item list-group-item-action"
          @click="$emit('navigate')"
        >
          <span class="d-flex align-items-center gap-2">
            <StatusBadge :label="typeLabel(row.type)" tone="neutral" />
            <span class="flex-grow-1">
              <span class="d-block fw-semibold">{{ row.title }}</span>
              <span v-if="row.subtitle" class="d-block small text-muted">{{ row.subtitle }}</span>
            </span>
          </span>
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { globalSearch, type SearchType } from '@/api/search.api'
import { useLocaleStore } from '@/stores/locale.store'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'navigate'): void
}>()

const localeStore = useLocaleStore()

const copy = computed(() => ({
  title: localeStore.t('search.title'),
  placeholder: localeStore.t('search.placeholder'),
  submit: localeStore.t('search.submit'),
  emptyTitle: localeStore.t('search.emptyTitle'),
  emptyBody: localeStore.t('search.emptyBody'),
  results: localeStore.t('search.results'),
}))

const query = ref('')
const loading = ref(false)
const searched = ref(false)
const errorMessage = ref('')
const results = ref<Awaited<ReturnType<typeof globalSearch>>['results']>([])

function typeLabel(type: SearchType): string {
  return localeStore.t(`search.types.${type}`)
}

async function run() {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await globalSearch(query.value)
    results.value = response.results
    searched.value = true
  } catch {
    errorMessage.value = localeStore.t('common.recoveryHint')
    searched.value = false
  } finally {
    loading.value = false
  }
}

defineExpose({ run, query })
</script>

<style scoped>
.global-search-form {
  margin-bottom: var(--om-space-base);
}

.global-search-results {
  border-radius: var(--om-radius-lg);
  overflow: hidden;
  max-height: min(60vh, 28rem);
  overflow-y: auto;
}
</style>
