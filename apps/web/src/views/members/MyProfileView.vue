<template>
  <div class="p-4 p-lg-5 member-self-service">
    <div class="hero-card rounded-4 p-4 p-lg-5 mb-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">
            {{ copy.kicker }}
          </div>
          <h1 class="h3 fw-bold mb-2">{{ copy.title }}</h1>
          <p class="text-muted mb-0 hero-copy">
            {{ copy.lead }}
          </p>
        </div>

        <div class="d-flex align-items-start">
          <button
            class="btn btn-primary"
            type="button"
            @click="handleDownloadPdf"
            :disabled="downloadingPdf || !statement"
          >
            <span
              v-if="downloadingPdf"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            <i v-else class="bi bi-file-earmark-pdf me-2"></i>
            {{ downloadingPdf ? copy.preparingPdf : copy.downloadStatement }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="alert alert-info border-0 shadow-sm" role="alert">
      <div class="d-flex gap-3">
        <div class="spinner-border spinner-border-sm mt-1" role="status" aria-hidden="true"></div>
        <div>
          <h6 class="alert-heading mb-1">{{ copy.loadingTitle }}</h6>
          <p class="mb-0 small">{{ copy.loadingBody }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-warning border-0 shadow-sm" role="alert">
      <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
        <div>
          <div class="fw-semibold mb-1">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ copy.couldNotLoad }}
          </div>
          <p class="mb-0 small">{{ error }}</p>
          <p class="mb-0 small text-muted mt-1">{{ copy.recoveryHint }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm flex-shrink-0" type="button" @click="retryLoad" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          {{ isRecovering ? copy.retrying : copy.retry }}
        </button>
      </div>
    </div>

    <template v-else-if="statement">
      <div class="row g-4 mb-4">
        <div class="col-xl-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="d-flex align-items-center gap-3 mb-3">
                <div class="icon-tile">
                  <i class="bi bi-person-badge fs-4"></i>
                </div>
                <div>
                  <div class="fw-semibold">{{ statement.profile.display_name }}</div>
                  <div class="small text-muted">{{ statement.profile.member_code }}</div>
                </div>
              </div>

              <hr />

              <dl class="row small mb-0 profile-grid">
                <dt class="col-sm-5 text-muted">{{ copy.firstName }}</dt>
                <dd class="col-sm-7">{{ statement.profile.first_name }}</dd>

                <dt class="col-sm-5 text-muted">{{ copy.lastName }}</dt>
                <dd class="col-sm-7">{{ statement.profile.last_name }}</dd>

                <dt class="col-sm-5 text-muted">{{ copy.email }}</dt>
                <dd class="col-sm-7">{{ statement.profile.email || '—' }}</dd>

                <dt class="col-sm-5 text-muted">{{ copy.phone }}</dt>
                <dd class="col-sm-7">{{ statement.profile.phone || '—' }}</dd>

                <dt class="col-sm-5 text-muted">{{ copy.status }}</dt>
                <dd class="col-sm-7">
                  <span class="badge rounded-pill text-bg-success" v-if="statement.profile.status === 'active'">
                    {{ copy.active }}
                  </span>
                  <span class="badge rounded-pill text-bg-secondary" v-else>
                    {{ formatStatus(statement.profile.status) }}
                  </span>
                </dd>

                <dt class="col-sm-5 text-muted">{{ copy.joined }}</dt>
                <dd class="col-sm-7">{{ formatDate(statement.profile.joined_at) }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="col-xl-8">
          <div class="row g-3">
            <div class="col-md-4">
              <div class="metric-card metric-neutral h-100">
                <div class="metric-label">{{ copy.expected }}</div>
                <div class="metric-value">{{ statement.summary.total_expected }}</div>
                <div class="metric-foot">EUR</div>
              </div>
            </div>

            <div class="col-md-4">
              <div class="metric-card metric-success h-100">
                <div class="metric-label">{{ copy.paid }}</div>
                <div class="metric-value">{{ statement.summary.total_paid }}</div>
                <div class="metric-foot">EUR</div>
              </div>
            </div>

            <div class="col-md-4">
              <div class="metric-card h-100" :class="balanceToneClass">
                <div class="metric-label">{{ copy.outstandingBalance }}</div>
                <div class="metric-value">{{ statement.summary.total_balance }}</div>
                <div class="metric-foot">
                  {{ statement.summary.contribution_count }} {{ copy.contributionRecord }}
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow-sm mt-4">
            <div class="card-body p-4">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
                <div>
                  <div class="text-uppercase small fw-semibold text-secondary mb-1">
                    {{ copy.contributionHistory }}
                  </div>
                  <h2 class="h6 fw-bold mb-0">{{ copy.personalRecordsOnly }}</h2>
                </div>
                <div class="small text-muted">
                  {{ copy.boundaryNote }}
                </div>
              </div>

              <div v-if="statement.contributions.length === 0" class="empty-state rounded-4 p-4 text-center">
                <i class="bi bi-journal-text fs-3 d-block mb-2 text-secondary"></i>
                <div class="fw-semibold mb-1">{{ copy.noContributionsTitle }}</div>
                <p class="text-muted small mb-0">
                  {{ copy.noContributionsText }}
                </p>
              </div>

              <div v-else class="table-responsive">
                <table class="table align-middle mb-0" :aria-label="copy.contributionHistory">
                  <thead>
                    <tr>
                      <th scope="col">{{ copy.year }}</th>
                      <th scope="col">{{ copy.expected }}</th>
                      <th scope="col">{{ copy.paid }}</th>
                      <th scope="col">{{ copy.balance }}</th>
                      <th scope="col">{{ copy.status }}</th>
                      <th scope="col">{{ copy.dueDate }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="contribution in statement.contributions" :key="contribution.id">
                      <td class="fw-semibold">{{ contribution.year }}</td>
                      <td>{{ contribution.expected_amount }} {{ contribution.currency }}</td>
                      <td class="text-success fw-medium">{{ contribution.paid_amount }} {{ contribution.currency }}</td>
                      <td :class="Number(contribution.balance) > 0 ? 'text-danger fw-semibold' : 'text-success fw-semibold'">
                        {{ contribution.balance }} {{ contribution.currency }}
                      </td>
                      <td>
                        <span class="badge rounded-pill" :class="statusBadgeClass(contribution.status)">
                          {{ formatStatus(contribution.status) }}
                        </span>
                      </td>
                      <td>{{ contribution.due_date ? formatDate(contribution.due_date) : '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  downloadMyStatementPdf,
  getMyStatement,
  type MemberStatementResponse,
} from '@/api/membership.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useRecoveryState } from '@/composables/useRecoveryState'

const localeStore = useLocaleStore()
const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
const downloadingPdf = ref(false)
const statement = ref<MemberStatementResponse | null>(null)

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      kicker: 'Mitgliederportal',
      title: 'Mein Profil und meine Beitragsübersicht',
      lead: 'Pruefen Sie Ihre persönlichen Daten, den aktuellen Saldo und laden Sie Ihre PDF-Bescheinigung herunter.',
      preparingPdf: 'PDF wird vorbereitet...',
      downloadStatement: 'Meine Bescheinigung herunterladen',
      loadingTitle: 'Mitgliederbereich wird geladen',
      loadingBody: 'Wir laden Ihr persönliches Profil und Ihre Beitragsgeschichte.',
      couldNotLoad: 'Bereich nicht verfügbar',
      retry: 'Erneut versuchen',
      retrying: 'Wird erneut geladen...',
      recoveryHint: 'Der Ladevorgang ist fehlgeschlagen. Ihr Bereich bleibt geschützt, Sie können es erneut versuchen.',
      firstName: 'Vorname',
      lastName: 'Nachname',
      email: 'E-Mail',
      phone: 'Telefon',
      status: 'Status',
      active: 'Aktiv',
      joined: 'Beigetreten',
      expected: 'Erwartet',
      paid: 'Bezahlt',
      outstandingBalance: 'Offener Saldo',
      contributionRecord: 'Beitragsdatensatz',
      contributionHistory: 'Beitragsverlauf',
      personalRecordsOnly: 'Nur Ihre persönlichen Einträge',
      boundaryNote: 'Dieser Bereich zeigt niemals die Finanzdaten anderer Mitglieder.',
      noContributionsTitle: 'Noch keine Beitragsdaten',
      noContributionsText: 'Ihre Organisation hat fuer Ihr Konto noch keine persönlichen Beitragsdaten veröffentlicht.',
      year: 'Jahr',
      balance: 'Saldo',
      dueDate: 'Fälligkeit',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      kicker: 'Member self-service',
      title: 'My profile and contribution statement',
      lead: 'Review your personal details, check your current balance, and download your own PDF statement.',
      preparingPdf: 'Preparing PDF...',
      downloadStatement: 'Download my statement',
      loadingTitle: 'Loading your member workspace',
      loadingBody: 'We are fetching your personal profile and contribution history.',
      couldNotLoad: 'Workspace unavailable',
      retry: 'Retry',
      retrying: 'Retrying...',
      recoveryHint: 'The last load failed. Your space stays protected and you can try again.',
      firstName: 'First name',
      lastName: 'Last name',
      email: 'Email',
      phone: 'Phone',
      status: 'Status',
      active: 'Active',
      joined: 'Joined',
      expected: 'Expected',
      paid: 'Paid',
      outstandingBalance: 'Outstanding balance',
      contributionRecord: 'contribution record',
      contributionHistory: 'Contribution history',
      personalRecordsOnly: 'Your personal records only',
      boundaryNote: "This area never exposes another member's financial data.",
      noContributionsTitle: 'No contribution records yet',
      noContributionsText: 'Your organization has not published personal contribution records for your account yet.',
      year: 'Year',
      balance: 'Balance',
      dueDate: 'Due date',
    }
  }
  return {
    kicker: 'Espace membre',
    title: 'Mon profil et mon relevé de cotisations',
    lead: 'Consultez vos informations personnelles, vérifiez votre solde actuel et téléchargez votre relevé PDF.',
    preparingPdf: 'Préparation du PDF...',
    downloadStatement: 'Télécharger mon relevé',
    loadingTitle: 'Chargement de votre espace membre',
    loadingBody: 'Nous récupérons votre profil personnel et votre historique de cotisations.',
    couldNotLoad: "Espace indisponible",
    retry: 'Réessayer',
    retrying: 'Nouvelle tentative...',
    recoveryHint: 'Le dernier chargement a échoué. Votre espace reste protégé et vous pouvez réessayer.',
    firstName: 'Prénom',
    lastName: 'Nom',
    email: 'E-mail',
    phone: 'Téléphone',
    status: 'Statut',
    active: 'Actif',
    joined: 'Inscrit le',
    expected: 'Attendu',
    paid: 'Payé',
    outstandingBalance: 'Solde restant',
    contributionRecord: 'dossier de cotisation',
    contributionHistory: 'Historique des cotisations',
    personalRecordsOnly: 'Uniquement vos dossiers personnels',
    boundaryNote: "Cet espace n'expose jamais les données financières d'un autre membre.",
    noContributionsTitle: 'Aucune cotisation pour le moment',
    noContributionsText: "Votre association n'a pas encore publié de cotisation personnelle pour votre compte.",
    year: 'Année',
    balance: 'Solde',
    dueDate: 'Échéance',
  }
})

const balanceToneClass = computed(() => {
  if (!statement.value) {
    return 'metric-neutral'
  }
  return Number(statement.value.summary.total_balance) > 0 ? 'metric-warning' : 'metric-success'
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(localeStore.currentLocale === 'fr' ? 'fr-FR' : localeStore.currentLocale === 'de' ? 'de-DE' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatStatus(status: string): string {
  const labels: Record<string, string> = {
    active: copy.value.active,
    inactive: localeStore.currentLocale === 'de' ? 'Inaktiv' : localeStore.currentLocale === 'en' ? 'Inactive' : 'Inactif',
    pending: localeStore.currentLocale === 'de' ? 'Ausstehend' : localeStore.currentLocale === 'en' ? 'Pending' : 'En attente',
    overdue: localeStore.currentLocale === 'de' ? 'Überfällig' : localeStore.currentLocale === 'en' ? 'Overdue' : 'En retard',
    paid: localeStore.currentLocale === 'de' ? 'Bezahlt' : localeStore.currentLocale === 'en' ? 'Paid' : 'Payé',
    partial: localeStore.currentLocale === 'de' ? 'Teilweise' : localeStore.currentLocale === 'en' ? 'Partial' : 'Partiel',
    waived: localeStore.currentLocale === 'de' ? 'Erlassen' : localeStore.currentLocale === 'en' ? 'Waived' : 'Annulé',
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    paid: 'bg-success-subtle text-success border border-success-subtle',
    partial: 'bg-warning-subtle text-warning border border-warning-subtle',
    overdue: 'bg-danger-subtle text-danger border border-danger-subtle',
    waived: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
    pending: 'bg-light text-dark border',
  }

  return classes[status] || 'bg-light text-dark border'
}

async function loadStatement() {
  await run(async () => {
    statement.value = await getMyStatement()
  })
}

async function retryLoad() {
  await retry(async () => {
    statement.value = await getMyStatement()
  })
}

async function handleDownloadPdf() {
  if (!statement.value || downloadingPdf.value) {
    return
  }

  downloadingPdf.value = true

  try {
    const pdfBlob = await downloadMyStatementPdf()
    const url = window.URL.createObjectURL(pdfBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `kairo-statement-${statement.value.profile.member_code}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    error.value = err?.response?.data?.detail || (localeStore.currentLocale === 'en' ? 'Could not download your PDF statement' : localeStore.currentLocale === 'de' ? 'Ihr PDF-Relevanz konnte nicht heruntergeladen werden' : 'Impossible de télécharger votre relevé PDF')
  } finally {
    downloadingPdf.value = false
  }
}

onMounted(loadStatement)
</script>

<style scoped>
.member-self-service {
  max-width: 1180px;
}

.hero-card {
  background:
    radial-gradient(circle at top right, rgba(185, 212, 255, 0.45), transparent 30%),
    linear-gradient(135deg, #f7f4ee 0%, #ffffff 65%);
  border: 1px solid #e2ddd3;
}

.hero-copy {
  max-width: 42rem;
}

.icon-tile {
  width: 3.25rem;
  height: 3.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  background: #eef3f8;
  color: #215d91;
}

.metric-card {
  border-radius: 1.25rem;
  padding: 1.25rem;
  border: 1px solid #dde5ec;
  background: #fff;
}

.metric-neutral {
  background: #f8fafc;
}

.metric-success {
  background: #eef9f1;
}

.metric-warning {
  background: #fff4e8;
}

.metric-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #667085;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.9rem;
  font-weight: 700;
  line-height: 1.05;
  margin-bottom: 0.35rem;
}

.metric-foot {
  font-size: 0.875rem;
  color: #667085;
}

.empty-state {
  background: #f8fafc;
  border: 1px dashed #c8d2dc;
}

.profile-grid dt,
.profile-grid dd {
  margin-bottom: 0.65rem;
}
</style>
