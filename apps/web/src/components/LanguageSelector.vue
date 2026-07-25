<template>
  <div class="d-flex align-items-center gap-2" :class="{ 'language-selector--compact': compact }">
    <label v-if="showLabel" class="small text-muted mb-0">{{ localeStore.t('language.label') }}</label>
    <select
      class="form-select form-select-sm language-select"
      :aria-label="localeStore.t('language.label')"
      :value="localeStore.currentLocale"
      @change="handleChange"
    >
      <option value="fr">{{ compact ? 'FR' : localeStore.t('language.fr') }}</option>
      <option value="en">{{ compact ? 'EN' : localeStore.t('language.en') }}</option>
      <option value="de">{{ compact ? 'DE' : localeStore.t('language.de') }}</option>
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
    compact?: boolean
  }>(),
  {
    showLabel: true,
    compact: false,
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

.language-selector--compact .language-select {
  width: 3.5rem;
  min-width: 3.5rem;
  min-height: 2.75rem;
  padding-inline: 0.5rem 1.35rem;
  font-size: 0.75rem;
  font-weight: 700;
}
</style>
