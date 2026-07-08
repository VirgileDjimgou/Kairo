<template>
  <div class="d-flex align-items-center gap-2">
    <label v-if="showLabel" class="small text-muted mb-0">{{ localeStore.t('language.label') }}</label>
    <select
      class="form-select form-select-sm language-select"
      :value="localeStore.currentLocale"
      @change="handleChange"
    >
      <option value="fr">{{ localeStore.t('language.fr') }}</option>
      <option value="en">{{ localeStore.t('language.en') }}</option>
      <option value="de">{{ localeStore.t('language.de') }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import type { SupportedLocale } from '@/i18n/messages'

withDefaults(
  defineProps<{
    showLabel?: boolean
  }>(),
  {
    showLabel: true,
  },
)

const authStore = useAuthStore()
const localeStore = useLocaleStore()

async function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const nextLocale = target.value as SupportedLocale
  if (authStore.isAuthenticated) {
    await authStore.updatePreferredLanguage(nextLocale)
    return
  }
  await localeStore.setLocale(nextLocale, false)
}
</script>

<style scoped>
.language-select {
  min-width: 8.5rem;
}
</style>
