<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ copy.kicker }}
        </div>
        <h1 class="h4 fw-bold mb-1">{{ copy.title }}</h1>
        <p class="text-muted mb-0">
          {{ copy.subtitle }}
        </p>
      </div>
      <button class="btn om-primary-btn align-self-start" type="button" @click="refreshData" :disabled="loading">
        {{ loading ? copy.refreshing : copy.refreshChannels }}
      </button>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <div v-if="actionError" class="alert alert-danger border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ actionError }}
    </div>

    <div v-if="successMessage" class="alert alert-success border-0 shadow-sm mb-4" role="status">
      <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
    </div>

    <div class="row g-3 mb-4">
      <div v-for="channel in channels" :key="channel.channel" class="col-md-6 col-xl-4">
        <article class="card shadow-sm border-0 h-100 channel-card">
          <div class="card-body p-4">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-3">
              <div>
                <h2 class="h6 fw-bold mb-1">{{ channel.display_name }}</h2>
                <div class="small text-muted">{{ channel.channel }}</div>
              </div>
              <span
                class="badge"
                :class="
                  channel.configured
                    ? 'bg-success-subtle text-success border border-success-subtle'
                    : 'bg-secondary-subtle text-secondary border border-secondary-subtle'
                "
              >
                {{ channel.configured ? copy.configured : copy.placeholder }}
              </span>
            </div>

            <p class="text-muted small mb-3">{{ channel.description }}</p>

            <div class="small d-flex justify-content-between gap-2 mb-2">
              <span class="text-muted">{{ copy.targetHint }}</span>
              <span class="fw-medium text-end">{{ channel.target_hint }}</span>
            </div>
            <div class="small d-flex justify-content-between gap-2">
              <span class="text-muted">{{ copy.deliveryMode }}</span>
              <span class="fw-medium text-end">
                {{ channel.simulation_only ? copy.simulationOnly : copy.liveCapable }}
              </span>
            </div>
          </div>
        </article>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-7">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
              <div>
                <h2 class="h6 fw-bold mb-1">{{ copy.simulationTitle }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.simulationLead }}
                </p>
              </div>
              <span class="badge bg-warning-subtle text-warning border border-warning-subtle">
                {{ copy.noExternalDelivery }}
              </span>
            </div>

            <div v-if="loading" class="text-muted py-4 text-center">{{ copy.loadingChannels }}</div>

            <form v-else class="row g-3" @submit.prevent="handleSendTest">
              <div class="col-12">
                <label class="form-label fw-medium small">{{ copy.channelsLabel }}</label>
                <div class="d-flex flex-wrap gap-2">
                  <label v-for="channel in channels" :key="channel.channel" class="channel-toggle">
                    <input
                      :checked="selectedChannels.includes(channel.channel)"
                      type="checkbox"
                      @change="toggleChannel(channel.channel)"
                    />
                    <span>{{ channel.display_name }}</span>
                  </label>
                </div>
              </div>

              <div class="col-md-6">
                <label class="form-label fw-medium small">{{ copy.recipientLabel }}</label>
                <input v-model.trim="form.recipient" class="form-control" type="text" :placeholder="copy.recipientPlaceholder" />
              </div>

              <div class="col-md-6">
                <label class="form-label fw-medium small">{{ copy.subjectLabel }}</label>
                <input v-model.trim="form.subject" class="form-control" type="text" :placeholder="copy.subjectPlaceholder" />
              </div>

              <div class="col-12">
                <label class="form-label fw-medium small">{{ copy.bodyLabel }}</label>
                <textarea v-model.trim="form.body" class="form-control" rows="4" :placeholder="copy.simulationBodyPlaceholder" />
              </div>

              <div class="col-12 d-flex gap-2">
                <button class="btn btn-primary" type="submit" :disabled="sendingTest || selectedChannels.length === 0">
                  {{ sendingTest ? copy.sendingSimulation : copy.runSimulation }}
                </button>
                <button class="btn btn-outline-secondary" type="button" @click="resetForm">
                  {{ copy.reset }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-5">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
              <div>
                <h2 class="h6 fw-bold mb-1">{{ copy.liveDispatchTitle }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.liveDispatchLead }}
                </p>
              </div>
              <span
                class="badge"
                :class="
                  liveCapableChannels.length > 0
                    ? 'bg-success-subtle text-success border border-success-subtle'
                    : 'bg-secondary-subtle text-secondary border border-secondary-subtle'
                "
              >
                {{ liveCapableChannels.length > 0 ? copy.liveEnabled : copy.liveUnavailable }}
              </span>
            </div>

            <div v-if="liveCapableChannels.length === 0" class="alert alert-secondary border-0 mb-0">
              {{ copy.liveUnavailableHint }}
            </div>

            <form v-else class="row g-3" @submit.prevent="handleSendLiveDispatch">
              <div class="col-12">
                <label class="form-label fw-medium small">{{ copy.liveChannelLabel }}</label>
                <select v-model="selectedLiveChannel" class="form-select">
                  <option v-for="channel in liveCapableChannels" :key="channel.channel" :value="channel.channel">
                    {{ channel.display_name }}
                  </option>
                </select>
              </div>

              <div class="col-12 small text-muted">
                {{ copy.liveOnlyOneChannelHint }}
              </div>

              <div class="col-12">
                <button class="btn om-primary-btn" type="submit" :disabled="sendingLive || !selectedLiveChannel">
                  {{ sendingLive ? copy.sendingLive : copy.sendLive }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.historyTitle }}
            </div>

            <div v-if="history.length === 0" class="text-muted small">
              {{ copy.noResults }}
            </div>

            <div v-else class="vstack gap-3">
              <article v-for="entry in history" :key="entry.id" class="result-card">
                <div class="d-flex align-items-center justify-content-between gap-2 mb-2">
                  <div>
                    <div class="fw-semibold text-capitalize">{{ entry.channel }}</div>
                    <div class="small text-muted">{{ formatTimestamp(entry.created_at) }}</div>
                  </div>
                  <span class="badge" :class="statusBadgeClass(entry)">
                    {{ formatAction(entry.action) }}
                  </span>
                </div>
                <div class="small d-flex justify-content-between gap-2 mb-1">
                  <span class="text-muted">{{ copy.historyRecipient }}</span>
                  <span class="fw-medium text-end">{{ entry.recipient }}</span>
                </div>
                <div class="small d-flex justify-content-between gap-2 mb-1">
                  <span class="text-muted">{{ copy.historyDeliveryStage }}</span>
                  <span class="fw-medium text-end">{{ formatDeliveryStage(entry.delivery_stage) }}</span>
                </div>
                <div class="small d-flex justify-content-between gap-2 mb-2">
                  <span class="text-muted">{{ copy.historyReconciliation }}</span>
                  <span class="fw-medium text-end">{{ formatReconciliation(entry.reconciliation_status) }}</span>
                </div>
                <p class="small text-muted mb-2">{{ entry.message }}</p>
                <div class="small text-muted">
                  {{
                    entry.provider_reference
                      ? `${copy.historyProviderReference}: ${entry.provider_reference}`
                      : copy.noProviderReference
                  }}
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  listNotificationChannels,
  listNotificationHistory,
  sendNotificationDispatch,
  sendNotificationTest,
  type NotificationChannelResponse,
  type NotificationHistoryEntry,
} from '@/api/notifications.api'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const loading = ref(true)
const sendingTest = ref(false)
const sendingLive = ref(false)
const channels = ref<NotificationChannelResponse[]>([])
const history = ref<NotificationHistoryEntry[]>([])
const selectedChannels = ref<string[]>(['email'])
const selectedLiveChannel = ref('email')
const error = ref('')
const actionError = ref('')
const successMessage = ref('')
const form = ref({
  recipient: 'ops@example.org',
  subject: 'Kairo notification test',
  body: 'This message validates the notification delivery path for the active tenant.',
})

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      kicker: 'Benachrichtigungen',
      title: 'Benachrichtigungserweiterungen',
      subtitle: 'Pruefen Sie optionale Kanaele, erfassen Sie echte Zustellungsannahmen mit Audit-Spur und halten Sie die Rechte strikt im Backend.',
      refreshing: 'Aktualisierung...',
      refreshChannels: 'Kanaele aktualisieren',
      configured: 'Konfiguriert',
      placeholder: 'Platzhalter',
      targetHint: 'Zielhinweis',
      deliveryMode: 'Zustellmodus',
      simulationOnly: 'Nur Simulation',
      liveCapable: 'Live faehig',
      simulationTitle: 'Simulierten Versand ausfuehren',
      simulationLead: 'Dieser Dry-Run prueft die optionalen Kanaele, ohne externe Nachrichten fuer Platzhalterpfade zu senden.',
      noExternalDelivery: 'Keine externe Zustellung',
      loadingChannels: 'Kanaele werden geladen...',
      channelsLabel: 'Kanaele',
      recipientLabel: 'Empfaenger / Ziel',
      recipientPlaceholder: 'ops@example.org oder @kanal-id',
      subjectLabel: 'Betreff',
      subjectPlaceholder: 'Kairo Benachrichtigungstest',
      bodyLabel: 'Nachricht',
      simulationBodyPlaceholder: 'Diese Nachricht prueft die simulierte Benachrichtigungspipeline.',
      sendingSimulation: 'Simulation laeuft...',
      runSimulation: 'Simulierten Versand starten',
      reset: 'Zuruecksetzen',
      liveDispatchTitle: 'Live-Benachrichtigung senden',
      liveDispatchLead: 'Konfigurierte SMTP-, Telegram- oder WhatsApp-Kanaele liefern jetzt auch eine audit-faehige Annahme- und Reconciliation-Spur.',
      liveEnabled: 'Live aktiviert',
      liveUnavailable: 'Live nicht verfuegbar',
      liveUnavailableHint: 'Kein live-faehiger Kanal ist aktuell konfiguriert. Aktivieren Sie SMTP, Telegram oder WhatsApp fuer einen echten Zustellpfad.',
      liveChannelLabel: 'Live-Kanal',
      liveOnlyOneChannelHint: 'Der Live-Versand bleibt absichtlich auf einen einzelnen konfigurierten Kanal beschraenkt.',
      sendingLive: 'Live-Versand...',
      sendLive: 'Live-Benachrichtigung senden',
      historyTitle: 'Letzte Operator-Historie',
      historyRecipient: 'Ziel',
      historyDeliveryStage: 'Lieferphase',
      historyReconciliation: 'Reconciliation',
      historyProviderReference: 'Provider-Referenz',
      noProviderReference: 'Keine Provider-Referenz',
      noResults: 'Noch keine auditierte Benachrichtigungshistorie.',
      loadError: 'Die Benachrichtigungskanaele konnten nicht geladen werden.',
      simulationSuccess: 'Der simulierte Versand wurde abgeschlossen.',
      liveSuccess: 'Die Live-Benachrichtigung wurde an den ausgewaehlten Kanal uebergeben.',
      actionFallback: 'Die Benachrichtigungsaktion ist fehlgeschlagen.',
      actionDispatch: 'Live',
      actionTest: 'Test',
      stageAccepted: 'Akzeptiert',
      stageDelivered: 'Zugestellt',
      stageFailed: 'Fehlgeschlagen',
      stageSimulated: 'Simuliert',
      reconciliationDelivered: 'Zugestellt',
      reconciliationPending: 'Ausstehend',
      reconciliationFailed: 'Fehlgeschlagen',
      reconciliationNotApplicable: 'Nicht anwendbar',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      kicker: 'Notifications',
      title: 'Notification extensions',
      subtitle: 'Review optional channels, capture live delivery acceptance with audit evidence, and keep permissions backend-owned.',
      refreshing: 'Refreshing...',
      refreshChannels: 'Refresh channels',
      configured: 'Configured',
      placeholder: 'Placeholder',
      targetHint: 'Target hint',
      deliveryMode: 'Delivery mode',
      simulationOnly: 'Simulation only',
      liveCapable: 'Live capable',
      simulationTitle: 'Run simulated dispatch',
      simulationLead: 'This dry-run validates optional channels without sending external messages for placeholder-only paths.',
      noExternalDelivery: 'No external delivery',
      loadingChannels: 'Loading channels...',
      channelsLabel: 'Channels',
      recipientLabel: 'Recipient / target',
      recipientPlaceholder: 'ops@example.org or @channel-id',
      subjectLabel: 'Subject',
      subjectPlaceholder: 'Kairo notification test',
      bodyLabel: 'Body',
      simulationBodyPlaceholder: 'This message validates the simulated notification pipeline.',
      sendingSimulation: 'Running simulation...',
      runSimulation: 'Run simulated dispatch',
      reset: 'Reset',
      liveDispatchTitle: 'Send live notification',
      liveDispatchLead: 'Configured SMTP, Telegram, and WhatsApp channels now expose acceptance evidence and reconciliation seams in the operator audit trail.',
      liveEnabled: 'Live enabled',
      liveUnavailable: 'Live unavailable',
      liveUnavailableHint: 'No live-capable channel is configured right now. Enable SMTP, Telegram, or WhatsApp to validate a real delivery path.',
      liveChannelLabel: 'Live channel',
      liveOnlyOneChannelHint: 'Live delivery stays intentionally limited to one configured channel so operators confirm the target path explicitly.',
      sendingLive: 'Sending live...',
      sendLive: 'Send live notification',
      historyTitle: 'Recent operator history',
      historyRecipient: 'Target',
      historyDeliveryStage: 'Delivery stage',
      historyReconciliation: 'Reconciliation',
      historyProviderReference: 'Provider reference',
      noProviderReference: 'No provider reference',
      noResults: 'No audited notification history yet.',
      loadError: 'Could not load notification channels.',
      simulationSuccess: 'Simulated dispatch completed.',
      liveSuccess: 'Live notification accepted for the selected channel.',
      actionFallback: 'Notification action failed.',
      actionDispatch: 'Live',
      actionTest: 'Test',
      stageAccepted: 'Accepted',
      stageDelivered: 'Delivered',
      stageFailed: 'Failed',
      stageSimulated: 'Simulated',
      reconciliationDelivered: 'Delivered',
      reconciliationPending: 'Pending',
      reconciliationFailed: 'Failed',
      reconciliationNotApplicable: 'Not applicable',
    }
  }
  return {
    kicker: 'Notifications',
    title: 'Extensions de notification',
    subtitle: 'Consultez les canaux optionnels, capturez une preuve d’acceptation réelle avec audit, et gardez les permissions strictement côté backend.',
    refreshing: 'Actualisation...',
    refreshChannels: 'Actualiser les canaux',
    configured: 'Configuré',
    placeholder: 'Placeholder',
    targetHint: 'Cible attendue',
    deliveryMode: 'Mode de livraison',
    simulationOnly: 'Simulation uniquement',
    liveCapable: 'Capable en réel',
    simulationTitle: 'Lancer un dispatch simulé',
    simulationLead: 'Ce dry-run valide les canaux optionnels sans envoyer de messages externes pour les chemins encore limités à la simulation.',
    noExternalDelivery: 'Aucune livraison externe',
    loadingChannels: 'Chargement des canaux...',
    channelsLabel: 'Canaux',
    recipientLabel: 'Destinataire / cible',
    recipientPlaceholder: 'ops@example.org ou @canal-id',
    subjectLabel: 'Sujet',
    subjectPlaceholder: 'Test de notification Kairo',
    bodyLabel: 'Message',
    simulationBodyPlaceholder: 'Ce message valide le pipeline de notification simulé.',
    sendingSimulation: 'Simulation en cours...',
    runSimulation: 'Lancer le dispatch simulé',
    reset: 'Réinitialiser',
    liveDispatchTitle: 'Envoyer une notification réelle',
    liveDispatchLead: 'Les canaux SMTP, Telegram et WhatsApp configurés exposent maintenant une preuve d’acceptation et une couture de réconciliation dans la piste opérateur.',
    liveEnabled: 'Réel activé',
    liveUnavailable: 'Réel indisponible',
    liveUnavailableHint: "Aucun canal réellement exploitable n'est configuré pour le moment. Activez SMTP, Telegram ou WhatsApp pour valider un vrai chemin de livraison.",
    liveChannelLabel: 'Canal réel',
    liveOnlyOneChannelHint: 'La livraison réelle reste volontairement limitée à un seul canal configuré pour confirmer explicitement la route cible.',
    sendingLive: 'Envoi réel...',
    sendLive: 'Envoyer la notification réelle',
    historyTitle: 'Historique opérateur récent',
    historyRecipient: 'Cible',
    historyDeliveryStage: 'Étape de livraison',
    historyReconciliation: 'Réconciliation',
    historyProviderReference: 'Référence fournisseur',
    noProviderReference: 'Aucune référence fournisseur',
    noResults: 'Aucune notification auditée pour le moment.',
    loadError: 'Impossible de charger les canaux de notification.',
    simulationSuccess: 'Le dispatch simulé est terminé.',
    liveSuccess: 'La notification réelle a été acceptée pour le canal sélectionné.',
    actionFallback: "L'action de notification a échoué.",
    actionDispatch: 'Réel',
    actionTest: 'Test',
    stageAccepted: 'Acceptée',
    stageDelivered: 'Livrée',
    stageFailed: 'Échec',
    stageSimulated: 'Simulée',
    reconciliationDelivered: 'Livrée',
    reconciliationPending: 'En attente',
    reconciliationFailed: 'Échec',
    reconciliationNotApplicable: 'Sans objet',
  }
})

const liveCapableChannels = computed(() =>
  channels.value.filter((channel) => channel.configured && !channel.simulation_only),
)

function setActionError(err: unknown) {
  actionError.value =
    (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail ||
    (err as { message?: string })?.message ||
    copy.value.actionFallback
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat(localeStore.currentLocale, {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatAction(action: string) {
  return action === 'notification_dispatch' ? copy.value.actionDispatch : copy.value.actionTest
}

function formatDeliveryStage(stage: string) {
  if (stage === 'accepted') return copy.value.stageAccepted
  if (stage === 'delivered') return copy.value.stageDelivered
  if (stage === 'failed') return copy.value.stageFailed
  return copy.value.stageSimulated
}

function formatReconciliation(status: string) {
  if (status === 'delivered') return copy.value.reconciliationDelivered
  if (status === 'pending') return copy.value.reconciliationPending
  if (status === 'failed') return copy.value.reconciliationFailed
  return copy.value.reconciliationNotApplicable
}

function statusBadgeClass(entry: NotificationHistoryEntry) {
  if (entry.action === 'notification_test') {
    return 'bg-warning-subtle text-warning border border-warning-subtle'
  }
  if (entry.delivery_stage === 'accepted' || entry.delivery_stage === 'delivered') {
    return 'bg-success-subtle text-success border border-success-subtle'
  }
  return 'bg-danger-subtle text-danger border border-danger-subtle'
}

async function refreshData() {
  loading.value = true
  error.value = ''
  actionError.value = ''
  successMessage.value = ''
  try {
    const [channelRows, historyRows] = await Promise.all([
      listNotificationChannels(),
      listNotificationHistory(),
    ])
    channels.value = channelRows
    history.value = historyRows
    if (!liveCapableChannels.value.find((channel) => channel.channel === selectedLiveChannel.value)) {
      selectedLiveChannel.value = liveCapableChannels.value[0]?.channel ?? ''
    }
  } catch (err) {
    error.value =
      (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail ||
      (err as { message?: string })?.message ||
      copy.value.loadError
  } finally {
    loading.value = false
  }
}

function toggleChannel(channel: string) {
  selectedChannels.value = selectedChannels.value.includes(channel)
    ? selectedChannels.value.filter((item) => item !== channel)
    : [...selectedChannels.value, channel]
}

function resetForm() {
  selectedChannels.value = ['email']
  selectedLiveChannel.value = liveCapableChannels.value[0]?.channel ?? 'email'
  form.value = {
    recipient: 'ops@example.org',
    subject: 'Kairo notification test',
    body: 'This message validates the notification delivery path for the active tenant.',
  }
  actionError.value = ''
  successMessage.value = ''
}

async function handleSendTest() {
  if (selectedChannels.value.length === 0) return

  sendingTest.value = true
  actionError.value = ''
  successMessage.value = ''
  try {
    await sendNotificationTest({
      channels: selectedChannels.value,
      recipient: form.value.recipient,
      subject: form.value.subject || null,
      body: form.value.body,
    })
    await refreshData()
    successMessage.value = copy.value.simulationSuccess
  } catch (err) {
    setActionError(err)
  } finally {
    sendingTest.value = false
  }
}

async function handleSendLiveDispatch() {
  if (!selectedLiveChannel.value) return

  sendingLive.value = true
  actionError.value = ''
  successMessage.value = ''
  try {
    await sendNotificationDispatch({
      channel: selectedLiveChannel.value,
      recipient: form.value.recipient,
      subject: form.value.subject || null,
      body: form.value.body,
    })
    await refreshData()
    successMessage.value = copy.value.liveSuccess
  } catch (err) {
    setActionError(err)
  } finally {
    sendingLive.value = false
  }
}

onMounted(refreshData)
</script>

<style scoped>
.channel-card {
  border-radius: 1rem;
}

.channel-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 999px;
  background: #fff;
  font-size: 0.875rem;
}

.result-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}
</style>
