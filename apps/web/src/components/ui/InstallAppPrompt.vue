<template>
  <div v-if="visible" class="install-prompt" role="region" :aria-label="localeStore.t('install.title')">
    <div class="install-prompt__copy">
      <strong class="install-prompt__title">
        {{ localeStore.t('install.title', { name: appName }) }}
      </strong>
      <span class="install-prompt__body">{{ localeStore.t('install.body') }}</span>
    </div>
    <div class="install-prompt__actions">
      <button class="btn btn-sm btn-primary" type="button" :disabled="busy" @click="install">
        {{ localeStore.t('install.cta') }}
      </button>
      <button class="btn btn-sm btn-outline-secondary" type="button" @click="dismiss">
        {{ localeStore.t('install.dismiss') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useToast } from 'vue-toastification'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import { effectiveBranding } from '@/services/branding'
import {
  dismissInstallPrompt,
  installPromptAvailable,
  promptInstall,
} from '@/services/pwa-install'

const localeStore = useLocaleStore()
const tenantStore = useTenantStore()
const toast = useToast()
const revision = ref(0)
const busy = ref(false)

const appName = computed(() => {
  const branding = effectiveBranding(tenantStore.currentTenant?.branding)
  return branding.short_name || branding.display_name
})

const visible = computed(() => {
  void revision.value
  return installPromptAvailable()
})

function handleInstalled() {
  revision.value += 1
  toast.success(localeStore.t('install.installed', { name: appName.value }))
}

function install() {
  busy.value = true
  void promptInstall()
    .then((outcome) => {
      if (outcome !== 'unavailable') revision.value += 1
    })
    .finally(() => {
      busy.value = false
    })
}

function dismiss() {
  dismissInstallPrompt()
  revision.value += 1
}

onMounted(() => {
  window.addEventListener('kairo:app-installed', handleInstalled)
  revision.value += 1
})

onBeforeUnmount(() => {
  window.removeEventListener('kairo:app-installed', handleInstalled)
})
</script>

<style scoped>
.install-prompt {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin: 0.75rem auto 0;
  width: 100%;
  max-width: var(--om-content-max-width);
  padding: 0.75rem 1rem;
  border: 1px solid var(--om-neutral-200);
  border-radius: var(--om-radius-base);
  background: var(--om-neutral-0);
  box-shadow: 0 1px 2px rgb(15 23 42 / 6%);
}

.install-prompt__copy {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.install-prompt__title {
  color: var(--om-neutral-900);
  font-size: 0.9375rem;
}

.install-prompt__body {
  color: var(--om-neutral-600);
  font-size: 0.8125rem;
}

.install-prompt__actions {
  display: flex;
  gap: 0.5rem;
  flex: 0 0 auto;
}
</style>
