<template>
  <div v-if="suggestions.length" class="mt-3">
    <div class="small text-uppercase text-muted fw-semibold mb-2">
      {{ localeStore.t('chat.suggested') }}
    </div>
    <div class="d-flex flex-wrap gap-2">
      <button
        v-for="suggestion in suggestions"
        :key="suggestion"
        class="btn btn-sm btn-outline-secondary rounded-pill"
        type="button"
        @click="$emit('select', suggestion)"
      >
        {{ suggestion }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLocaleStore } from "@/stores/locale.store";

defineProps<{
  suggestions: string[];
}>();

defineEmits<{
  (e: "select", text: string): void;
}>();

const localeStore = useLocaleStore();
</script>
