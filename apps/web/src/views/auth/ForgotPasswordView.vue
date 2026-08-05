<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center om-min-viewport-height om-safe-bottom">
    <div class="auth-card card shadow-sm border-0 p-4 p-md-5 w-100" style="max-width: 440px">
      <div class="text-center mb-4">
        <div class="brand-icon mb-3">
          <i class="bi bi-key fs-1 text-primary"></i>
        </div>
        <h1 class="h4 fw-bold mb-1">{{ copy.title }}</h1>
        <p class="text-muted small mb-0">
          {{ copy.subtitle }}
        </p>
      </div>

      <div class="recovery-guidance">
        <div class="guidance-icon"><i class="bi bi-person-lock"></i></div>
        <h2 class="h6 fw-bold">{{ copy.heading }}</h2>
        <p class="text-muted small mb-3">{{ copy.body }}</p>
        <ol class="small text-start mb-0">
          <li>{{ copy.stepOne }}</li>
          <li>{{ copy.stepTwo }}</li>
          <li>{{ copy.stepThree }}</li>
        </ol>
      </div>

      <div class="text-center mt-3">
        <router-link to="/login" class="small text-muted">
          {{ copy.back }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const copy = computed(() => {
  if (localeStore.currentLocale === 'de') return { title: 'Zugang wiederherstellen', subtitle: 'Ein autorisiertes Vorstandsmitglied kann einen sicheren temporären Zugang ausstellen.', heading: 'Kein E-Mail-Schritt erforderlich', body: 'Die Anmelde-E-Mail kann bei Kairo ein technischer Zugang sein. Deshalb wird der verlorene Zugang direkt durch den Verein wiederhergestellt.', stepOne: 'Wenden Sie sich an den Praesidenten, Vizepraesidenten oder Generalsekretaer.', stepTwo: 'Diese Person erstellt in Mitglieder einen zeitlich begrenzten Zugang.', stepThree: 'Melden Sie sich an und waehlen Sie sofort Ihr persoenliches neues Passwort.', back: 'Zurueck zur Anmeldung' }
  if (localeStore.currentLocale === 'en') return { title: 'Recover access', subtitle: 'An authorized office member can issue secure temporary access.', heading: 'No email step is required', body: 'At Kairo, the sign-in email can be a technical credential. Lost access is therefore recovered directly by the association.', stepOne: 'Contact the president, vice president, or secretary general.', stepTwo: 'They issue a time-limited access credential from Members.', stepThree: 'Sign in and choose your own new password immediately.', back: 'Back to sign in' }
  return { title: 'Récupérer l’accès', subtitle: 'Un membre du bureau autorisé peut créer un accès temporaire sécurisé.', heading: 'Aucun e-mail n’est nécessaire', body: 'Dans Kairo, l’adresse de connexion peut être un identifiant technique. L’accès perdu est donc rétabli directement par l’association.', stepOne: 'Contactez le président, le vice-président ou le secrétaire général.', stepTwo: 'La personne autorisée crée un accès limité dans le temps depuis Membres.', stepThree: 'Connectez-vous puis choisissez immédiatement votre nouveau mot de passe personnel.', back: 'Retour à la connexion' }
})
</script>

<style scoped>
.auth-wrapper {
  background-color: var(--om-bg, #f5f7fb);
}
.auth-card {
  background-color: var(--om-card-bg, #ffffff);
  border-radius: 1rem !important;
}
.brand-icon {
  width: 64px;
  height: 64px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(31, 79, 143, 0.08);
  border-radius: 1rem;
}
.recovery-guidance { border: 1px solid #d8e4f0; border-radius: 1rem; background: #f8fbff; padding: 1.25rem; text-align: center; }
.guidance-icon { display: inline-grid; place-items: center; width: 3rem; height: 3rem; margin-bottom: .75rem; border-radius: .9rem; color: #1f4f8f; background: rgba(31, 79, 143, .1); font-size: 1.4rem; }
</style>
