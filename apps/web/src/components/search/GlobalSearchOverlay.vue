<template>
  <div
    v-if="open"
    class="global-search-overlay"
    role="dialog"
    aria-modal="true"
    :aria-label="copy.title"
    @click.self="$emit('close')"
  >
    <div class="global-search-sheet card border-0 shadow-lg">
      <div class="card-body p-3 p-md-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h2 class="h6 fw-bold mb-0">{{ copy.title }}</h2>
          <button class="btn btn-sm btn-outline-secondary" type="button" :aria-label="copy.close" @click="$emit('close')">
            <i class="bi bi-x-lg" aria-hidden="true"></i>
          </button>
        </div>
        <GlobalSearchPanel ref="panel" @close="$emit('close')" @navigate="$emit('close')" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, watch } from 'vue'
import GlobalSearchPanel from '@/components/search/GlobalSearchPanel.vue'
import { useLocaleStore } from '@/stores/locale.store'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const localeStore = useLocaleStore()
const copy = computed(() => ({
  title: localeStore.t('search.title'),
  close: localeStore.t('search.close'),
}))

const panel = ref<{ query: string } | null>(null)

function handleEscape(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    event.preventDefault()
    emit('close')
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      window.addEventListener('keydown', handleEscape)
      void nextTick(() => {
        const input = document.querySelector<HTMLInputElement>('.global-search-sheet input[type="search"]')
        input?.focus()
      })
    } else {
      window.removeEventListener('keydown', handleEscape)
    }
  },
)

onUnmounted(() => window.removeEventListener('keydown', handleEscape))

defineExpose({ panel })
</script>

<style scoped>
.global-search-overlay {
  position: fixed;
  inset: 0;
  z-index: 1080;
  background: rgba(23, 33, 43, 0.45);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--om-space-base);
  padding-top: 10vh;
}

.global-search-sheet {
  width: min(40rem, 100%);
  border-radius: var(--om-radius-xl);
}
</style>
