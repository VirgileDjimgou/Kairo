import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { messages, type SupportedLocale } from '@/i18n/messages'
import { updateLanguagePreference } from '@/api/auth.api'

const LOCALE_STORAGE_KEY = 'preferred_locale'
const DEFAULT_LOCALE: SupportedLocale = 'fr'

export const useLocaleStore = defineStore('locale', () => {
  const locale = ref<SupportedLocale>(normalizeLocale(localStorage.getItem(LOCALE_STORAGE_KEY)))

  const currentLocale = computed(() => locale.value)

  function initialize() {
    applyLocale(locale.value)
  }

  function resolvePreferredLocale(input: {
    preferredLanguage?: string | null
    tenantDefaultLanguage?: string | null
  }): SupportedLocale {
    if (input.preferredLanguage) return normalizeLocale(input.preferredLanguage)
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
    if (stored) return normalizeLocale(stored)
    if (input.tenantDefaultLanguage) return normalizeLocale(input.tenantDefaultLanguage)
    return DEFAULT_LOCALE
  }

  function applyLocale(nextLocale: SupportedLocale) {
    locale.value = nextLocale
    localStorage.setItem(LOCALE_STORAGE_KEY, nextLocale)
    document.documentElement.lang = nextLocale
    document.title = messages[nextLocale]['app.name']
  }

  async function setLocale(nextLocale: SupportedLocale, syncWithBackend = false) {
    const normalized = normalizeLocale(nextLocale)
    applyLocale(normalized)
    if (syncWithBackend) {
      await updateLanguagePreference({ preferred_language: normalized })
    }
  }

  function t(key: string, replacements?: Record<string, string | number>): string {
    const dictionary = messages[locale.value]
    let value = dictionary[key] ?? messages.fr[key] ?? key
    if (!replacements) {
      return value
    }
    for (const [replacementKey, replacementValue] of Object.entries(replacements)) {
      value = value.replaceAll(`{${replacementKey}}`, String(replacementValue))
    }
    return value
  }

  return {
    currentLocale,
    initialize,
    resolvePreferredLocale,
    setLocale,
    applyLocale,
    t,
  }
})

function normalizeLocale(value: string | null | undefined): SupportedLocale {
  const normalized = (value || DEFAULT_LOCALE).trim().toLowerCase()
  if (normalized === 'en' || normalized === 'de') {
    return normalized
  }
  return 'fr'
}
