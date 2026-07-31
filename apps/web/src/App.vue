<template>
  <div v-if="updateAvailable" class="pwa-update-notice shadow-sm" role="status">
    <span>{{ localeStore.t('app.updateAvailable') }}</span>
    <button class="btn btn-sm btn-light" type="button" @click="applyUpdate">{{ localeStore.t('app.updateNow') }}</button>
  </div>
  <RouterView />
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { RouterView } from "vue-router";
import { useToast } from "vue-toastification";
import { useAuthStore } from "@/stores/auth.store";
import { useLocaleStore } from "@/stores/locale.store";
import { listenForOperationNotifications, type OperationNotification } from "@/services/operation-notifications";

const authStore = useAuthStore();
const localeStore = useLocaleStore();
const updateAvailable = ref(false)
const toast = useToast()
let removeNotificationListener: (() => void) | undefined

function markUpdateAvailable() {
  updateAvailable.value = true
}

function applyUpdate() {
  window.dispatchEvent(new Event('kairo:pwa-apply-update'))
}

function displayOperationNotification(notification: OperationNotification) {
  const message = notification.detail
    ? `${localeStore.t(notification.messageKey)} ${notification.detail}`
    : localeStore.t(notification.messageKey)
  const options = { timeout: 5000, closeButton: true }
  toast[notification.level](message, options)
}

onMounted(() => {
  localeStore.initialize();
  void authStore.restoreSession();
  window.addEventListener('kairo:pwa-update-available', markUpdateAvailable)
  removeNotificationListener = listenForOperationNotifications(displayOperationNotification)
});

onBeforeUnmount(() => {
  window.removeEventListener('kairo:pwa-update-available', markUpdateAvailable)
  removeNotificationListener?.()
})
</script>

<style scoped>
.pwa-update-notice {
  position: fixed;
  z-index: 1100;
  right: max(1rem, env(safe-area-inset-right));
  bottom: max(1rem, env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: min(28rem, calc(100vw - 2rem));
  padding: 0.75rem 0.9rem;
  border-radius: 0.75rem;
  background: #1a3f6b;
  color: #fff;
  font-size: 0.9rem;
}
</style>
