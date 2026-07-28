<template>
  <main class="initial-password-page d-flex align-items-center justify-content-center p-3">
    <section class="card shadow-sm border-0 initial-password-card">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <div class="initial-password-icon mx-auto mb-3"><i class="bi bi-key-fill"></i></div>
          <h1 class="h4 fw-bold mb-2">{{ t('initialPassword.title') }}</h1>
          <p class="text-muted mb-0">{{ t('initialPassword.lead') }}</p>
        </div>
        <div class="alert alert-info small">{{ t('initialPassword.notice') }}</div>
        <form @submit.prevent="submit" novalidate>
          <div class="mb-3">
            <label for="new-password" class="form-label fw-medium">{{ t('initialPassword.newPassword') }}</label>
            <input id="new-password" v-model="newPassword" class="form-control" type="password" autocomplete="new-password" minlength="8" required />
          </div>
          <div class="mb-3">
            <label for="confirm-password" class="form-label fw-medium">{{ t('initialPassword.confirmPassword') }}</label>
            <input id="confirm-password" v-model="confirmation" class="form-control" type="password" autocomplete="new-password" minlength="8" required />
          </div>
          <div v-if="error" class="alert alert-danger small">{{ error }}</div>
          <button class="btn btn-primary w-100" type="submit" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>{{ saving ? t('initialPassword.saving') : t('initialPassword.submit') }}
          </button>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { changeInitialPassword } from '@/api/auth.api'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { getApiErrorDetail } from '@/utils/authErrors'

const router = useRouter()
const authStore = useAuthStore()
const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const newPassword = ref('')
const confirmation = ref('')
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (newPassword.value.length < 8) { error.value = t('initialPassword.errorLength'); return }
  if (newPassword.value !== confirmation.value) { error.value = t('initialPassword.errorMismatch'); return }
  saving.value = true
  try {
    await changeInitialPassword({ new_password: newPassword.value })
    await authStore.fetchMe()
    await router.replace('/dashboard')
  } catch (err) {
    error.value = getApiErrorDetail(err) || t('initialPassword.errorFailed')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.initial-password-page { min-height: 100dvh; background: #eef2f7; }
.initial-password-card { width: min(100%, 460px); }
.initial-password-icon { width: 3rem; height: 3rem; display: grid; place-items: center; border-radius: .875rem; background: #e8f0fb; color: #25589a; font-size: 1.35rem; }
</style>
