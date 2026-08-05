<template>
  <section class="card shadow-sm border-0" data-testid="change-password-card">
    <div class="card-body p-4">
      <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ copy.kicker }}</div>
      <h2 class="h6 fw-bold mb-1">{{ copy.title }}</h2>
      <p class="text-muted small mb-3">{{ copy.description }}</p>

      <form class="row g-3" novalidate @submit.prevent="submit">
        <div class="col-12">
          <label class="form-label small fw-semibold" for="current-password">{{ copy.currentPassword }}</label>
          <div class="input-group">
            <input id="current-password" v-model="currentPassword" class="form-control" :class="{ 'is-invalid': errors.current }" :type="showCurrent ? 'text' : 'password'" autocomplete="current-password" />
            <button class="btn btn-outline-secondary" type="button" @click="showCurrent = !showCurrent"><i :class="showCurrent ? 'bi bi-eye-slash' : 'bi bi-eye'"></i><span class="visually-hidden">{{ copy.toggleVisibility }}</span></button>
          </div>
          <div v-if="errors.current" class="invalid-feedback d-block">{{ errors.current }}</div>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-semibold" for="new-password">{{ copy.newPassword }}</label>
          <input id="new-password" v-model="newPassword" class="form-control" :class="{ 'is-invalid': errors.new }" :type="showNew ? 'text' : 'password'" autocomplete="new-password" />
          <div v-if="errors.new" class="invalid-feedback d-block">{{ errors.new }}</div>
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-semibold" for="confirm-password">{{ copy.confirmPassword }}</label>
          <div class="input-group">
            <input id="confirm-password" v-model="confirmation" class="form-control" :class="{ 'is-invalid': errors.confirmation }" :type="showNew ? 'text' : 'password'" autocomplete="new-password" />
            <button class="btn btn-outline-secondary" type="button" @click="showNew = !showNew"><i :class="showNew ? 'bi bi-eye-slash' : 'bi bi-eye'"></i><span class="visually-hidden">{{ copy.toggleVisibility }}</span></button>
          </div>
          <div v-if="errors.confirmation" class="invalid-feedback d-block">{{ errors.confirmation }}</div>
        </div>
        <div class="col-12 d-flex flex-wrap gap-2 align-items-center">
          <button class="btn btn-primary" type="submit" :disabled="saving">{{ saving ? copy.saving : copy.submit }}</button>
          <span class="small text-muted">{{ copy.sessionHint }}</span>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { changePassword } from '@/api/auth.api'
import { useLocaleStore } from '@/stores/locale.store'
import { notifyOperation } from '@/services/operation-notifications'

const localeStore = useLocaleStore()
const currentPassword = ref('')
const newPassword = ref('')
const confirmation = ref('')
const showCurrent = ref(false)
const showNew = ref(false)
const saving = ref(false)
const errors = reactive({ current: '', new: '', confirmation: '' })

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') return {
    kicker: 'Passwort', title: 'Passwort aendern', description: 'Aendern Sie Ihr Passwort direkt, ohne eine E-Mail zu benoetigen.', currentPassword: 'Aktuelles Passwort', newPassword: 'Neues Passwort', confirmPassword: 'Neues Passwort bestaetigen', toggleVisibility: 'Passwortsichtbarkeit umschalten', submit: 'Passwort aendern', saving: 'Speichern...', sessionHint: 'Andere aktive Sitzungen werden abgemeldet.', currentRequired: 'Geben Sie Ihr aktuelles Passwort ein.', newRequired: 'Das neue Passwort muss mindestens 8 Zeichen haben.', mismatch: 'Die neuen Passwoerter stimmen nicht ueberein.',
  }
  if (localeStore.currentLocale === 'en') return {
    kicker: 'Password', title: 'Change password', description: 'Change your password directly without needing an email.', currentPassword: 'Current password', newPassword: 'New password', confirmPassword: 'Confirm new password', toggleVisibility: 'Toggle password visibility', submit: 'Change password', saving: 'Saving...', sessionHint: 'Other active sessions will be signed out.', currentRequired: 'Enter your current password.', newRequired: 'The new password must contain at least 8 characters.', mismatch: 'The new passwords do not match.',
  }
  return {
    kicker: 'Mot de passe', title: 'Modifier le mot de passe', description: 'Modifiez directement votre mot de passe, sans avoir besoin d’e-mail.', currentPassword: 'Mot de passe actuel', newPassword: 'Nouveau mot de passe', confirmPassword: 'Confirmer le nouveau mot de passe', toggleVisibility: 'Afficher ou masquer le mot de passe', submit: 'Modifier le mot de passe', saving: 'Enregistrement…', sessionHint: 'Les autres sessions actives seront déconnectées.', currentRequired: 'Saisissez votre mot de passe actuel.', newRequired: 'Le nouveau mot de passe doit contenir au moins 8 caractères.', mismatch: 'Les nouveaux mots de passe ne correspondent pas.',
  }
})

function validate() {
  errors.current = currentPassword.value ? '' : copy.value.currentRequired
  errors.new = newPassword.value.length >= 8 ? '' : copy.value.newRequired
  errors.confirmation = confirmation.value === newPassword.value ? '' : copy.value.mismatch
  return !errors.current && !errors.new && !errors.confirmation
}

async function submit() {
  if (!validate()) {
    notifyOperation({ level: 'warning', messageKey: 'validation.correctHighlightedFields' })
    return
  }
  saving.value = true
  try {
    await changePassword({ current_password: currentPassword.value, new_password: newPassword.value })
    currentPassword.value = ''
    newPassword.value = ''
    confirmation.value = ''
    notifyOperation({ level: 'success', messageKey: 'identity.passwordChanged' })
  } catch (error: unknown) {
    notifyOperation({ level: 'error', messageKey: 'identity.passwordChangeFailed', detail: getErrorDetail(error) })
  } finally {
    saving.value = false
  }
}

function getErrorDetail(error: unknown) {
  return (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? ''
}
</script>
