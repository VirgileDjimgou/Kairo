<template>
  <Teleport to="body">
    <div v-if="member" class="recovery-backdrop" role="presentation">
      <section class="recovery-modal card shadow-lg border-0" role="dialog" aria-modal="true" :aria-label="copy.title">
        <div class="card-body p-4 p-md-5">
          <div class="d-flex justify-content-between align-items-start gap-3 mb-4">
            <div>
              <div class="text-uppercase small fw-semibold text-primary mb-2">{{ copy.kicker }}</div>
              <h2 class="h5 fw-bold mb-1">{{ copy.title }}</h2>
              <p class="text-muted small mb-0">{{ copy.description }}</p>
            </div>
            <button class="btn-close" type="button" :aria-label="copy.close" @click="close"></button>
          </div>

          <template v-if="!result">
            <div class="member-summary mb-4">
              <div class="fw-semibold">{{ member.display_name }}</div>
              <div class="small text-muted font-monospace">{{ member.member_code }} · {{ member.email || member.phone || '—' }}</div>
            </div>
            <label class="form-label small fw-semibold" for="access-recovery-reason">{{ copy.reason }}</label>
            <select id="access-recovery-reason" v-model="reason" class="form-select mb-3">
              <option value="forgotten_password">{{ copy.forgotten }}</option>
              <option value="lost_access">{{ copy.lost }}</option>
              <option value="security_reset">{{ copy.security }}</option>
            </select>
            <div class="alert alert-warning small border-0 mb-4"><i class="bi bi-shield-exclamation me-2"></i>{{ copy.warning }}</div>
            <div class="d-flex flex-wrap justify-content-end gap-2">
              <button class="btn btn-outline-secondary" type="button" :disabled="saving" @click="close">{{ copy.cancel }}</button>
              <button class="btn btn-primary" type="button" :disabled="saving" @click="issueTemporaryAccess"><i class="bi bi-key me-2"></i>{{ saving ? copy.issuing : copy.issue }}</button>
            </div>
          </template>

          <template v-else>
            <div class="alert alert-success border-0 small"><i class="bi bi-check-circle me-2"></i>{{ copy.success }}</div>
            <div class="temporary-password mb-3">
              <div class="small text-muted mb-1">{{ copy.temporaryPassword }}</div>
              <code>{{ result.temporary_password }}</code>
              <button class="btn btn-outline-primary btn-sm" type="button" @click="copyPassword"><i class="bi bi-copy me-1"></i>{{ copied ? copy.copied : copy.copy }}</button>
            </div>
            <dl class="row small mb-4">
              <dt class="col-5">{{ copy.expiry }}</dt><dd class="col-7">{{ formatDate(result.expires_at) }}</dd>
              <dt class="col-5">{{ copy.sessions }}</dt><dd class="col-7">{{ result.revoked_session_count }}</dd>
            </dl>
            <p class="small text-muted mb-4">{{ copy.oneTime }}</p>
            <div class="d-flex justify-content-end"><button class="btn btn-primary" type="button" @click="close">{{ copy.done }}</button></div>
          </template>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { recoverMemberAccess, type AssistedAccessRecoveryResponse } from '@/api/auth.api'
import type { MembershipProfileResponse } from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { notifyOperation } from '@/services/operation-notifications'

const props = defineProps<{ member: MembershipProfileResponse | null }>()
const emit = defineEmits<{ close: [] }>()
const localeStore = useLocaleStore()
const reason = ref('forgotten_password')
const saving = ref(false)
const copied = ref(false)
const result = ref<AssistedAccessRecoveryResponse | null>(null)

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') return { kicker: 'Unterstuetzter Zugriff', title: 'Zeitweiligen Zugang ausstellen', description: 'Der Nutzer muss dieses einmal angezeigte Passwort bei der ersten Anmeldung ersetzen.', close: 'Schliessen', reason: 'Grund', forgotten: 'Passwort vergessen', lost: 'Zugang verloren', security: 'Sicherheitsreset', warning: 'Alle aktuellen Sitzungen des Mitglieds werden sofort beendet. Das Passwort gilt 48 Stunden.', cancel: 'Abbrechen', issue: 'Temporären Zugang ausstellen', issuing: 'Wird ausgestellt...', success: 'Temporärer Zugang wurde erstellt.', temporaryPassword: 'Einmaliges temporäres Passwort', copy: 'Kopieren', copied: 'Kopiert', expiry: 'Gueltig bis', sessions: 'Beendete Sitzungen', oneTime: 'Teilen Sie dieses Passwort sicher mit. Es wird nach dem Schliessen nicht erneut angezeigt.', done: 'Fertig' }
  if (localeStore.currentLocale === 'en') return { kicker: 'Assisted access', title: 'Issue temporary access', description: 'The member must replace this one-time password at their first sign-in.', close: 'Close', reason: 'Reason', forgotten: 'Forgot password', lost: 'Lost access', security: 'Security reset', warning: 'All current sessions for this member will end immediately. The password is valid for 48 hours.', cancel: 'Cancel', issue: 'Issue temporary access', issuing: 'Issuing...', success: 'Temporary access has been created.', temporaryPassword: 'One-time temporary password', copy: 'Copy', copied: 'Copied', expiry: 'Valid until', sessions: 'Sessions ended', oneTime: 'Share this password securely. It is not shown again after closing this dialog.', done: 'Done' }
  return { kicker: 'Accès assisté', title: 'Créer un accès temporaire', description: 'Le membre devra remplacer ce mot de passe affiché une seule fois, dès sa première connexion.', close: 'Fermer', reason: 'Motif', forgotten: 'Mot de passe oublié', lost: 'Accès perdu', security: 'Réinitialisation de sécurité', warning: 'Toutes les sessions actives de ce membre seront immédiatement fermées. Le mot de passe est valable 48 heures.', cancel: 'Annuler', issue: 'Créer l’accès temporaire', issuing: 'Création…', success: 'L’accès temporaire a été créé.', temporaryPassword: 'Mot de passe provisoire à usage unique', copy: 'Copier', copied: 'Copié', expiry: 'Valable jusqu’au', sessions: 'Sessions fermées', oneTime: 'Transmettez ce mot de passe par un canal sûr. Il ne sera plus affiché après la fermeture de cette fenêtre.', done: 'Terminer' }
})

watch(() => props.member?.id, () => { reason.value = 'forgotten_password'; result.value = null; copied.value = false })

async function issueTemporaryAccess() {
  if (!props.member?.user_id) return
  saving.value = true
  try {
    result.value = await recoverMemberAccess(props.member.user_id, { reason: reason.value })
    notifyOperation({ level: 'success', messageKey: 'identity.accessRecoveryIssued' })
  } catch (error: unknown) {
    notifyOperation({ level: 'error', messageKey: 'identity.accessRecoveryFailed', detail: getErrorDetail(error) })
  } finally { saving.value = false }
}

async function copyPassword() {
  if (!result.value) return
  try { await navigator.clipboard.writeText(result.value.temporary_password); copied.value = true } catch { copied.value = false }
}

function close() { result.value = null; emit('close') }
function formatDate(value: string) { return new Date(value).toLocaleString(localeStore.currentLocale) }
function getErrorDetail(error: unknown) { return (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? '' }
</script>

<style scoped>
.recovery-backdrop { position: fixed; inset: 0; z-index: 1080; display: grid; place-items: center; padding: 1rem; background: rgba(15, 23, 42, .58); }
.recovery-modal { width: min(100%, 37rem); max-height: min(90vh, 48rem); overflow: auto; }
.member-summary { border-left: .25rem solid #1f4f8f; border-radius: .5rem; background: #f4f8fc; padding: .85rem 1rem; }
.temporary-password { display: grid; grid-template-columns: 1fr auto; gap: .65rem; align-items: center; border: 1px solid #b9d8c2; border-radius: .75rem; background: #f2fbf4; padding: 1rem; }
.temporary-password > div { grid-column: 1 / -1; }
.temporary-password code { overflow-wrap: anywhere; color: #14532d; font-size: .95rem; }
@media (max-width: 575.98px) { .recovery-backdrop { align-items: end; padding: 0; } .recovery-modal { width: 100%; border-radius: 1.25rem 1.25rem 0 0; } }
</style>
