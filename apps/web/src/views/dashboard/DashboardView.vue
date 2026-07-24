<template>
  <div class="p-3 p-md-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row align-items-lg-end justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ dashboardKicker }}
        </div>
        <h1 class="h4 fw-bold mb-1">{{ copy.welcomeBack }}, {{ authStore.user?.display_name }}</h1>
        <p class="text-muted mb-0">
          {{ dashboardLead }}
        </p>
      </div>
      <span
        class="badge px-3 py-2"
        :class="isSetupMode ? 'bg-warning-subtle text-warning border border-warning-subtle' : 'bg-success-subtle text-success border border-success-subtle'"
      >
        <i class="bi bi-circle-fill me-1" style="font-size: 0.5rem"></i>
        {{ isSetupMode ? copy.setupMode : copy.operational }}
      </span>
    </div>

    <div v-if="loading" class="alert alert-info border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex gap-3">
        <div class="spinner-border spinner-border-sm mt-1" role="status" aria-hidden="true"></div>
        <div>
          <h6 class="alert-heading mb-1">{{ copy.loadingTitle }}</h6>
          <p class="mb-0 small">
            {{ copy.loadingBody }}
          </p>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <div v-else class="card shadow-sm border-0 mb-4" data-testid="dashboard-workspace-focus">
      <div class="card-body p-4">
        <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
          <div>
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ workspaceFocus.kicker }}
            </div>
            <h2 class="h5 fw-bold mb-1">{{ workspaceFocus.title }}</h2>
            <p class="text-muted mb-0">
              {{ workspaceFocus.description }}
            </p>
          </div>
          <RouterLink :to="workspaceFocus.primary.to" class="btn btn-primary align-self-start">
            {{ workspaceFocus.primary.label }}
          </RouterLink>
        </div>

        <div class="d-flex flex-wrap gap-2 mt-3">
          <RouterLink
            v-for="action in workspaceFocus.links"
            :key="action.to + action.label"
            :to="action.to"
            class="btn btn-outline-secondary btn-sm"
          >
            {{ action.label }}
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card shadow-sm border-0 onboarding-card h-100" data-testid="tenant-onboarding">
          <div class="card-body p-3 p-md-4 p-lg-5">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-4">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  {{ copy.firstRunChecklist }}
                </div>
                <h2 class="h5 fw-bold mb-2">{{ statusTitle }}</h2>
                <p class="text-muted mb-0">
                  {{ statusMessage }}
                </p>
              </div>
              <div class="text-md-end">
                <div
                  class="display-6 fw-bold lh-1"
                  data-testid="tenant-onboarding-progress"
                >
                  {{ progressPercent }}%
                </div>
                <div class="small text-muted">{{ copy.complete }}</div>
              </div>
            </div>

            <div class="progress mb-4" style="height: 0.75rem">
              <div
                class="progress-bar"
                role="progressbar"
                :aria-valuenow="progressPercent"
                aria-valuemin="0"
                aria-valuemax="100"
                :style="{ width: `${progressPercent}%` }"
              ></div>
            </div>

            <div v-if="nextStep" class="alert alert-primary border-0 mb-4">
              <div class="d-flex align-items-start gap-3">
                <i class="bi bi-arrow-right-circle fs-4 flex-shrink-0"></i>
                <div>
                  <div class="fw-semibold mb-1">{{ copy.nextBestAction }}</div>
                  <p class="mb-2 small">
                    {{ nextStep.title }}: {{ nextStep.description }}
                  </p>
                  <RouterLink :to="nextStep.to" class="btn btn-sm btn-primary">
                    {{ nextStep.actionLabel }}
                  </RouterLink>
                </div>
              </div>
            </div>

            <div class="vstack gap-3">
              <article
                v-for="step in checklist"
                :key="step.id"
                class="checklist-item"
                :class="{ completed: step.completed }"
              >
                <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                  <div class="d-flex gap-3">
                    <div class="step-icon" :class="{ completed: step.completed }">
                      <i :class="step.completed ? 'bi bi-check2' : stepIcon(step.id)"></i>
                    </div>
                    <div>
                      <div class="fw-semibold mb-1">{{ step.title }}</div>
                      <p class="small text-muted mb-0">{{ step.description }}</p>
                    </div>
                  </div>

                  <div class="text-md-end">
                    <span
                      class="badge mb-2"
                      :class="step.completed ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-secondary-subtle text-secondary border border-secondary-subtle'"
                    >
                      {{ step.completed ? copy.completed : copy.pending }}
                    </span>
                    <div>
                      <RouterLink :to="step.to" class="btn btn-sm btn-outline-primary">
                        {{ step.actionLabel }}
                      </RouterLink>
                    </div>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-1">
                  {{ copy.tenantSnapshot }}
                </div>
                <h2 class="h6 fw-bold mb-0">{{ copy.liveUsageSignals }}</h2>
              </div>
              <button class="btn btn-outline-secondary btn-sm" type="button" @click="refresh" :disabled="loading">
                {{ copy.refresh }}
              </button>
            </div>

            <div class="row g-3">
              <div v-for="metric in summaryMetrics" :key="metric.label" class="col-6">
                <div class="metric-card h-100">
                  <div class="small text-muted">{{ metric.label }}</div>
                  <div class="fs-4 fw-bold lh-1 mb-1">{{ metric.value }}</div>
                  <div class="small text-secondary">{{ metric.hint }}</div>
                </div>
              </div>
            </div>

            <hr class="my-4" />

            <div class="small text-uppercase fw-semibold text-secondary mb-2">
              {{ copy.currentTenant }}
            </div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.tenant }}</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.role }}</span>
                <span class="fw-semibold text-end">
                  {{ authStore.user?.roles.join(', ') || '—' }}
                </span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.checklistComplete }}</span>
                <span class="fw-semibold text-end">
                  {{ completedCount }} / {{ checklist.length }}
                </span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.lastRefresh }}</span>
                <span class="fw-semibold text-end">
                  {{ lastRefreshedAt ? formatDateTime(lastRefreshedAt) : copy.justLoaded }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0" data-testid="dashboard-quick-actions">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.quickActions }}
            </div>
            <div class="vstack gap-2">
              <RouterLink
                v-for="action in filteredQuickActions"
                :key="action.to + action.label"
                :to="action.to"
                class="btn btn-outline-secondary text-start"
              >
                <i :class="action.icon" class="me-2"></i>{{ action.label }}
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'
import { useTenantOnboarding } from '@/composables/useTenantOnboarding'
import { useLocaleStore } from '@/stores/locale.store'

type WorkspaceFocusLink = {
  label: string
  to: string
}

type WorkspaceFocus = {
  kicker: string
  title: string
  description: string
  primary: WorkspaceFocusLink
  links: WorkspaceFocusLink[]
}

const authStore = useAuthStore()
const tenantStore = useTenantStore()
const localeStore = useLocaleStore()
const userRoles = computed(() => authStore.user?.roles ?? [])
const isAdmin = computed(() => userRoles.value.includes('admin'))
const isPrincipalAdmin = computed(() => userRoles.value.includes('principal_admin'))
const isTreasurer = computed(() => userRoles.value.includes('treasurer'))
const isMemberOnly = computed(() => userRoles.value.includes('member') && userRoles.value.length === 1)
const isSecretaryGeneral = computed(() => userRoles.value.includes('secretary_general'))
const isCensor = computed(() => userRoles.value.includes('censor'))
const isSportsManager = computed(() => userRoles.value.includes('sports_manager'))
const isPresidentRole = computed(() => userRoles.value.includes('president'))
const isVicePresidentRole = computed(() => userRoles.value.includes('vice_president'))
const isAuditor = computed(() => userRoles.value.includes('auditor'))
const isPresident = computed(() => userRoles.value.includes('president'))
const canOpenHealthCenter = computed(
  () =>
    isAuditor.value ||
    isPresidentRole.value ||
    isVicePresidentRole.value ||
    isSecretaryGeneral.value ||
    isTreasurer.value ||
    isCensor.value ||
    isSportsManager.value ||
    isPrincipalAdmin.value ||
    isAdmin.value,
)
const {
  loading,
  error,
  checklist,
  completedCount,
  progressPercent,
  statusTitle,
  statusMessage,
  summaryMetrics,
  nextStep,
  lastRefreshedAt,
  refresh,
} = useTenantOnboarding()

const workspaceFocus = computed<WorkspaceFocus>(() => {
  if (isPrincipalAdmin.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Principal admin control plane' : localeStore.currentLocale === 'de' ? 'Hauptadmin-Steuerzentrale' : "Pilotage administrateur principal",
      title: localeStore.currentLocale === 'en' ? 'Tenant operations, settings, and sensitive review' : localeStore.currentLocale === 'de' ? 'Tenant-Betrieb, Einstellungen und sensible Kontrolle' : 'Opérations du tenant, réglages et supervision sensible',
      description:
        localeStore.currentLocale === 'en' ? 'Use the control plane for tenant-wide administration while keeping isolation, review paths, and settings in one place.' : localeStore.currentLocale === 'de' ? 'Nutzen Sie diese Zentrale fuer die tenant-weite Administration bei isolationserhaltenden controles.' : "Utilisez cet espace pour l'administration globale du tenant sans casser l'isolation.",
      primary: { label: localeStore.currentLocale === 'en' ? 'Open principal admin control plane' : localeStore.currentLocale === 'de' ? 'Hauptadmin-Zentrale öffnen' : "Ouvrir l'espace administrateur principal", to: '/admin/settings' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Tenant operations' : localeStore.currentLocale === 'de' ? 'Tenant-Opérationen' : 'Opérations du tenant', to: '/admin/tenants' },
        { label: localeStore.currentLocale === 'en' ? 'Manage access' : localeStore.currentLocale === 'de' ? 'Zugänge verwalten' : 'Gérer les accès', to: '/admin/access' },
      ],
    }
  }

  if (isMemberOnly.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Read-only member portal' : localeStore.currentLocale === 'de' ? 'Mitgliederportal im Lesemodus' : 'Portail membre en lecture simple',
      title: localeStore.currentLocale === 'en' ? 'My profile, balance, and member updates' : localeStore.currentLocale === 'de' ? 'Mein Profil, mein Saldo und Vereinsinfos' : 'Mon profil, mon solde et mes informations membres',
      description:
        localeStore.currentLocale === 'en' ? 'Open the member portal for your own profile, contribution summary, and the latest association updates you are allowed to read.' : localeStore.currentLocale === 'de' ? 'Oeffnen Sie Ihr Portal fuer Profil, Beitragsuebersicht und freigegebene Vereinsinformationen.' : 'Ouvrez votre portail pour votre profil, votre résumé de cotisations et les informations autorisées.',
      primary: { label: localeStore.currentLocale === 'en' ? 'Open my profile' : localeStore.currentLocale === 'de' ? 'Mein Profil öffnen' : 'Ouvrir mon profil', to: '/members/profile' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Ask the assistant' : localeStore.currentLocale === 'de' ? 'Assistent fragen' : "Interroger l'assistant", to: '/chat' },
        { label: localeStore.currentLocale === 'en' ? 'Review events' : localeStore.currentLocale === 'de' ? 'Veranstaltungen ansehen' : 'Consulter les événements', to: '/events' },
      ],
    }
  }

  if (isTreasurer.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Treasury workspace' : localeStore.currentLocale === 'de' ? 'Finanzbereich' : 'Espace trésorerie',
      title: localeStore.currentLocale === 'en' ? 'Balances, contribution records, and payments' : localeStore.currentLocale === 'de' ? 'Salden, Beitragsakten und Zahlungen' : 'Soldes, cotisations et paiements',
      description:
        localeStore.currentLocale === 'en'
          ? 'Use the finance workspace to review balances, payment activity, and the member records needed for treasury follow-up.'
          : localeStore.currentLocale === 'de'
            ? 'Nutzen Sie den Finanzbereich, um Salden, Zahlungen und die fuer die Nachverfolgung noetigen Mitgliederdaten zu pruefen.'
            : "Utilisez l'espace finances pour suivre les soldes, les paiements et les dossiers membres utiles au trésorier.",
      primary: { label: localeStore.currentLocale === 'en' ? 'Go to finance workspace' : localeStore.currentLocale === 'de' ? 'Finanzbereich öffnen' : "Ouvrir l'espace finances", to: '/finance' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Review member profile' : localeStore.currentLocale === 'de' ? 'Mitgliedsprofil prüfen' : 'Consulter le profil membre', to: '/members/profile' },
        { label: localeStore.currentLocale === 'en' ? 'Open health center' : localeStore.currentLocale === 'de' ? 'Health Center öffnen' : 'Ouvrir le centre de santé', to: '/admin/health' },
      ],
    }
  }

  if (isSecretaryGeneral.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Secretary workspace' : localeStore.currentLocale === 'de' ? 'Sekretariatsbereich' : 'Espace secrétariat',
      title: localeStore.currentLocale === 'en' ? 'Documents, policies, and announcements' : localeStore.currentLocale === 'de' ? 'Dokumente, Regeln und Ankuendigungen' : 'Documents, règlements et annonces',
      description:
        localeStore.currentLocale === 'en'
          ? 'Stay inside the secretary workspace to update documents, maintain policies, and publish association announcements.'
          : localeStore.currentLocale === 'de'
            ? 'Bleiben Sie im Sekretariatsbereich, um Dokumente zu pflegen, Regeln zu aktualisieren und Vereinsankuendigungen zu veroeffentlichen.'
            : "Restez dans l'espace secrétariat pour mettre à jour les documents, maintenir les règlements et publier les annonces.",
      primary: { label: localeStore.currentLocale === 'en' ? 'Open secretary workspace' : localeStore.currentLocale === 'de' ? 'Sekretariatsbereich öffnen' : "Ouvrir l'espace secrétariat", to: '/secretary' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Review documents' : localeStore.currentLocale === 'de' ? 'Dokumente prüfen' : 'Consulter les documents', to: '/secretary/documents' },
        ...(tenantStore.isModuleEnabled('policies')
          ? [{ label: localeStore.currentLocale === 'en' ? 'Review policies' : localeStore.currentLocale === 'de' ? 'Regeln prüfen' : 'Consulter les règlements', to: '/secretary/policies' }]
          : []),
        ...(tenantStore.isModuleEnabled('announcements')
          ? [{ label: localeStore.currentLocale === 'en' ? 'Review announcements' : localeStore.currentLocale === 'de' ? 'Ankuendigungen prüfen' : 'Consulter les annonces', to: '/secretary/announcements' }]
          : []),
      ],
    }
  }

  if (isAuditor.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Finance audit' : localeStore.currentLocale === 'de' ? 'Finanzaudit' : 'Audit financier',
      title: localeStore.currentLocale === 'en' ? 'Read-only oversight and audit-ready records' : localeStore.currentLocale === 'de' ? 'Lecture seule et auditbereite Aufzeichnungen' : 'Supervision en lecture seule et dossiers prêts pour audit',
      description:
        localeStore.currentLocale === 'en'
          ? 'Inspect finance totals and audit-ready records without mutation controls or unnecessary workspace clutter.'
          : localeStore.currentLocale === 'de'
            ? 'Pruefen Sie Finanzsynthesen und auditbereite Aufzeichnungen ohne Schreibrechte oder unnoetige Komplexitaet.'
            : "Contrôlez les synthèses financières et les enregistrements prêts pour l'audit sans droits d'écriture.",
      primary: { label: localeStore.currentLocale === 'en' ? 'Open finance audit' : localeStore.currentLocale === 'de' ? 'Finanzaudit öffnen' : "Ouvrir l'audit financier", to: '/finance-audit' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Review policies' : localeStore.currentLocale === 'de' ? 'Regeln prüfen' : 'Consulter les règlements', to: '/policies' },
        { label: localeStore.currentLocale === 'en' ? 'Open health center' : localeStore.currentLocale === 'de' ? 'Health Center öffnen' : 'Ouvrir le centre de santé', to: '/admin/health' },
      ],
    }
  }

  if (isCensor.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Disciplinary console' : localeStore.currentLocale === 'de' ? 'Disziplinarkonsole' : 'Console disciplinaire',
      title: localeStore.currentLocale === 'en' ? 'Privacy-safe record review' : localeStore.currentLocale === 'de' ? 'Datenschutzsichere Aktenpruefung' : 'Revue sécurisée des dossiers',
      description:
        localeStore.currentLocale === 'en'
          ? 'Work inside the disciplinary console with strict privacy boundaries so only authorized records stay visible.'
          : localeStore.currentLocale === 'de'
            ? 'Arbeiten Sie in der Disziplinarkonsole mit strengen Datenschutzgrenzen, damit nur befugte Akten sichtbar bleiben.'
            : 'Travaillez dans la console disciplinaire avec des frontières de confidentialité strictes pour ne voir que les dossiers autorisés.',
      primary: { label: localeStore.currentLocale === 'en' ? 'Manage disciplinary records' : localeStore.currentLocale === 'de' ? 'Disziplinardossiers verwalten' : 'Gérer les dossiers disciplinaires', to: '/censor' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Review policies' : localeStore.currentLocale === 'de' ? 'Regeln prüfen' : 'Consulter les règlements', to: '/policies' },
        { label: localeStore.currentLocale === 'en' ? 'Ask the assistant' : localeStore.currentLocale === 'de' ? 'Assistent fragen' : "Interroger l'assistant", to: '/chat' },
      ],
    }
  }

  if (isSportsManager.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Sports workspace' : localeStore.currentLocale === 'de' ? 'Sportbereich' : 'Espace sport',
      title: localeStore.currentLocale === 'en' ? 'Training sessions, fixtures, and club activity' : localeStore.currentLocale === 'de' ? 'Trainings, Termine und Vereinsaktivitaet' : 'Entraînements, rencontres et activité du club',
      description:
        localeStore.currentLocale === 'en'
          ? 'Manage sports events from a focused workspace that keeps fixtures, updates, and community activity in one place.'
          : localeStore.currentLocale === 'de'
            ? 'Verwalten Sie Sportveranstaltungen in einem fokussierten Bereich, der Termine, Aktualisierungen und Gemeinschaftsaktivitaet zusammenhaelt.'
            : "Gérez les événements sportifs depuis un espace ciblé qui réunit calendrier, mises à jour et vie associative.",
      primary: { label: localeStore.currentLocale === 'en' ? 'Open sports workspace' : localeStore.currentLocale === 'de' ? 'Sportbereich öffnen' : "Ouvrir l'espace sport", to: '/sports' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Review events' : localeStore.currentLocale === 'de' ? 'Veranstaltungen ansehen' : 'Consulter les événements', to: '/events' },
        { label: localeStore.currentLocale === 'en' ? 'Ask the assistant' : localeStore.currentLocale === 'de' ? 'Assistent fragen' : "Interroger l'assistant", to: '/chat' },
      ],
    }
  }

  if (isPresidentRole.value || isVicePresidentRole.value) {
    return {
      kicker: localeStore.currentLocale === 'en' ? 'Executive oversight' : localeStore.currentLocale === 'de' ? 'Exekutive Aufsicht' : 'Supervision exécutive',
      title: localeStore.currentLocale === 'en' ? 'Governance, member visibility, and coordination' : localeStore.currentLocale === 'de' ? 'Governance, Mitgliederblick und Koordination' : 'Gouvernance, vision membres et coordination',
      description:
        localeStore.currentLocale === 'en'
          ? 'Use the governance cockpit for oversight, coordination, and a clean path to the association spaces that matter most.'
          : localeStore.currentLocale === 'de'
            ? 'Nutzen Sie das Governance-Cockpit fuer Aufsicht, Koordination und einen klaren Zugang zu den wichtigsten Vereinsbereichen.'
            : "Utilisez le cockpit de gouvernance pour la supervision, la coordination et un accès clair aux espaces clés de l'association.",
      primary: { label: localeStore.currentLocale === 'en' ? 'Open governance cockpit' : localeStore.currentLocale === 'de' ? 'Governance-Cockpit öffnen' : 'Ouvrir le cockpit de gouvernance', to: '/governance' },
      links: [
        { label: localeStore.currentLocale === 'en' ? 'Review finance audit' : localeStore.currentLocale === 'de' ? 'Finanzaudit prüfen' : "Consulter l'audit financier", to: '/finance-audit' },
        { label: localeStore.currentLocale === 'en' ? 'Read announcements' : localeStore.currentLocale === 'de' ? 'Ankuendigungen lesen' : 'Lire les annonces', to: '/announcements' },
      ],
    }
  }

  return {
    kicker: localeStore.currentLocale === 'en' ? 'Tenant overview' : localeStore.currentLocale === 'de' ? 'Tenant-Ueberblick' : 'Aperçu du tenant',
    title: localeStore.currentLocale === 'en' ? 'The next step that matters most' : localeStore.currentLocale === 'de' ? 'Der naechste wichtige Schritt' : "L'étape la plus utile maintenant",
    description:
      localeStore.currentLocale === 'en'
        ? 'Use the dashboard to jump into the next workspace that matters most for your role and the current tenant state.'
        : localeStore.currentLocale === 'de'
          ? 'Nutzen Sie das Dashboard, um direkt in den naechsten wichtigen Bereich fuer Ihre Rolle und den Tenant-Stand zu wechseln.'
          : "Utilisez ce tableau de bord pour rejoindre directement le prochain espace le plus utile selon votre rôle et l'état du tenant.",
    primary: { label: localeStore.currentLocale === 'en' ? 'Open dashboard' : localeStore.currentLocale === 'de' ? 'Dashboard öffnen' : 'Ouvrir le tableau de bord', to: '/dashboard' },
    links: [
      { label: localeStore.currentLocale === 'en' ? 'Admin settings' : localeStore.currentLocale === 'de' ? 'Admin-Einstellungen' : 'Paramètres administrateur', to: '/admin/settings' },
      { label: localeStore.currentLocale === 'en' ? 'Ask the assistant' : localeStore.currentLocale === 'de' ? 'Assistent fragen' : "Interroger l'assistant", to: '/chat' },
    ],
  }
})

const quickActions = computed(() => {
  const actions: Array<{ label: string; to: string; icon: string }> = []

  if (isMemberOnly.value) {
    actions.push({ label: localeStore.currentLocale === 'en' ? 'Open my profile' : localeStore.currentLocale === 'de' ? 'Mein Profil öffnen' : 'Ouvrir mon profil', to: '/members/profile', icon: 'bi bi-person-badge' })
    if (tenantStore.isModuleEnabled('chat')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Ask the assistant' : localeStore.currentLocale === 'de' ? 'Assistent fragen' : "Interroger l'assistant", to: '/chat', icon: 'bi bi-chat-dots' })
    }
    if (tenantStore.isModuleEnabled('events')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Review events' : localeStore.currentLocale === 'de' ? 'Veranstaltungen ansehen' : 'Consulter les événements', to: '/events', icon: 'bi bi-calendar-event' })
    }
    if (tenantStore.isModuleEnabled('announcements')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Read announcements' : localeStore.currentLocale === 'de' ? 'Ankündigungen lesen' : 'Lire les annonces', to: '/announcements', icon: 'bi bi-megaphone' })
    }
  } else if (isAdmin.value || isPrincipalAdmin.value) {
    actions.push({
      label:
        isPrincipalAdmin.value
          ? (localeStore.currentLocale === 'en' ? 'Open principal admin control plane' : localeStore.currentLocale === 'de' ? 'Hauptadmin-Zentrale öffnen' : "Ouvrir l'espace administrateur principal")
          : (localeStore.currentLocale === 'en' ? 'Review tenant settings' : localeStore.currentLocale === 'de' ? 'Tenant-Einstellungen prüfen' : 'Consulter les paramètres du tenant'),
      to: '/admin/settings',
      icon: 'bi bi-sliders',
    })
    actions.push({ label: localeStore.currentLocale === 'en' ? 'Open onboarding wizard' : localeStore.currentLocale === 'de' ? 'Onboarding-Assistent öffnen' : "Ouvrir l'assistant de démarrage", to: '/admin/onboarding', icon: 'bi bi-stars' })
    actions.push({ label: localeStore.currentLocale === 'en' ? 'Upload documents' : localeStore.currentLocale === 'de' ? 'Dokumente importieren' : 'Importer des documents', to: '/admin/documents', icon: 'bi bi-file-earmark-text' })
    if (tenantStore.isModuleEnabled('membership')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Import members' : localeStore.currentLocale === 'de' ? 'Mitglieder importieren' : 'Importer des membres', to: '/admin/members', icon: 'bi bi-people' })
    }
  } else if (isTreasurer.value) {
    actions.push({ label: localeStore.currentLocale === 'en' ? 'Go to finance workspace' : localeStore.currentLocale === 'de' ? 'Finanzbereich öffnen' : "Ouvrir l'espace finances", to: '/finance', icon: 'bi bi-cash-coin' })
    if (tenantStore.isModuleEnabled('membership')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Review member profile' : localeStore.currentLocale === 'de' ? 'Mitgliedsprofil prüfen' : 'Consulter le profil membre', to: '/members/profile', icon: 'bi bi-person-badge' })
    }
  } else if (isSecretaryGeneral.value) {
    actions.push({ label: localeStore.currentLocale === 'en' ? 'Open secretary workspace' : localeStore.currentLocale === 'de' ? 'Sekretariatsbereich öffnen' : "Ouvrir l'espace secrétariat", to: '/secretary', icon: 'bi bi-journal-richtext' })
    actions.push({ label: localeStore.currentLocale === 'en' ? 'Review documents' : localeStore.currentLocale === 'de' ? 'Dokumente prüfen' : 'Consulter les documents', to: '/secretary/documents', icon: 'bi bi-file-earmark-text' })
    if (tenantStore.isModuleEnabled('policies')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Review policies' : localeStore.currentLocale === 'de' ? 'Regeln prüfen' : 'Consulter les règlements', to: '/secretary/policies', icon: 'bi bi-journal-text' })
    }
    if (tenantStore.isModuleEnabled('announcements')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Review announcements' : localeStore.currentLocale === 'de' ? 'Ankuendigungen prüfen' : 'Consulter les annonces', to: '/secretary/announcements', icon: 'bi bi-megaphone' })
    }
  } else if (isAuditor.value || isPresident.value) {
    actions.push({ label: localeStore.currentLocale === 'en' ? 'Open finance audit' : localeStore.currentLocale === 'de' ? 'Finanzaudit öffnen' : "Ouvrir l'audit financier", to: '/finance-audit', icon: 'bi bi-clipboard-data' })
    if (tenantStore.isModuleEnabled('policies')) {
      actions.push({ label: localeStore.currentLocale === 'en' ? 'Review policies' : localeStore.currentLocale === 'de' ? 'Regeln prüfen' : 'Consulter les règlements', to: '/policies', icon: 'bi bi-journal-text' })
    }
  }

  if (canOpenHealthCenter.value) {
    actions.push({
      label: localeStore.currentLocale === 'en' ? 'Open health center' : localeStore.currentLocale === 'de' ? 'Health Center öffnen' : 'Ouvrir le centre de santé',
      to: '/admin/health',
      icon: 'bi bi-heart-pulse',
    })
  }

  if (tenantStore.isModuleEnabled('disciplinary') && (isCensor.value || isPresident.value || isPrincipalAdmin.value || isAdmin.value)) {
    actions.push({
      label: isCensor.value
        ? (localeStore.currentLocale === 'en' ? 'Manage disciplinary records' : localeStore.currentLocale === 'de' ? 'Disziplinardossiers verwalten' : 'Gérer les dossiers disciplinaires')
        : (localeStore.currentLocale === 'en' ? 'Review disciplinary oversight' : localeStore.currentLocale === 'de' ? 'Disziplinaraufsicht prüfen' : 'Consulter la supervision disciplinaire'),
      to: '/censor',
      icon: 'bi bi-shield-lock',
    })
  }

  if (tenantStore.isModuleEnabled('announcements')) {
    actions.push({
      label: isAdmin.value || isPrincipalAdmin.value || isSecretaryGeneral.value ? (localeStore.currentLocale === 'en' ? 'Publish announcement' : localeStore.currentLocale === 'de' ? 'Ankündigung veröffentlichen' : 'Publier une annonce') : (localeStore.currentLocale === 'en' ? 'Review announcements' : localeStore.currentLocale === 'de' ? 'Ankündigungen ansehen' : 'Consulter les annonces'),
      to: isAdmin.value || isPrincipalAdmin.value ? '/admin/announcements' : isSecretaryGeneral.value ? '/secretary/announcements' : '/announcements',
      icon: 'bi bi-megaphone',
    })
  }

  if (tenantStore.isModuleEnabled('events')) {
    if (isSportsManager.value || isPrincipalAdmin.value || isAdmin.value) {
      actions.push({
        label: localeStore.currentLocale === 'en' ? 'Open sports workspace' : localeStore.currentLocale === 'de' ? 'Sportbereich öffnen' : "Ouvrir l'espace sport",
        to: '/sports',
        icon: 'bi bi-trophy',
      })
    }
    actions.push({
      label: isAdmin.value || isPrincipalAdmin.value ? (localeStore.currentLocale === 'en' ? 'Schedule event' : localeStore.currentLocale === 'de' ? 'Veranstaltung planen' : 'Planifier un événement') : (localeStore.currentLocale === 'en' ? 'Review events' : localeStore.currentLocale === 'de' ? 'Veranstaltungen ansehen' : 'Consulter les événements'),
      to: isAdmin.value || isPrincipalAdmin.value ? '/admin/events' : '/events',
      icon: 'bi bi-calendar-event',
    })
  }

  if (isPresidentRole.value || isVicePresidentRole.value || isPrincipalAdmin.value || isAdmin.value) {
    actions.push({
      label: localeStore.currentLocale === 'en' ? 'Open governance cockpit' : localeStore.currentLocale === 'de' ? 'Governance-Cockpit öffnen' : 'Ouvrir le cockpit de gouvernance',
      to: '/governance',
      icon: 'bi bi-diagram-3',
    })
  }

  return actions
})

const filteredQuickActions = computed(() =>
  quickActions.value.filter((action, index, source) => source.findIndex((item) => item.to === action.to) === index),
)

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      welcomeBack: 'Willkommen zurück',
      setupMode: 'Einrichtungsmodus',
      operational: 'Betriebsbereit',
      loadingTitle: 'Tenant-Startleitfaden wird geladen',
      loadingBody: 'Dokumente, Mitglieder, Ankuendigungen und Veranstaltungen werden geprueft, damit die Checkliste den echten Tenant-Stand widerspiegelt.',
      firstRunChecklist: 'Erststart-Checkliste',
      complete: 'abgeschlossen',
      nextBestAction: 'Beste naechste Aktion',
      completed: 'Abgeschlossen',
      pending: 'Offen',
      tenantSnapshot: 'Tenant-Ueberblick',
      liveUsageSignals: 'Live-Nutzungssignale',
      refresh: 'Aktualisieren',
      currentTenant: 'Aktueller Tenant',
      tenant: 'Tenant',
      role: 'Rolle',
      checklistComplete: 'Checkliste abgeschlossen',
      lastRefresh: 'Letzte Aktualisierung',
      justLoaded: 'Gerade geladen',
      quickActions: 'Schnellaktionen',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      welcomeBack: 'Welcome back',
      setupMode: 'Setup mode',
      operational: 'Operational',
      loadingTitle: 'Loading tenant onboarding guidance',
      loadingBody: 'We are checking documents, members, announcements, and events so the checklist reflects the live tenant state.',
      firstRunChecklist: 'First-run checklist',
      complete: 'complete',
      nextBestAction: 'Next best action',
      completed: 'Completed',
      pending: 'Pending',
      tenantSnapshot: 'Tenant snapshot',
      liveUsageSignals: 'Live usage signals',
      refresh: 'Refresh',
      currentTenant: 'Current tenant',
      tenant: 'Tenant',
      role: 'Role',
      checklistComplete: 'Checklist complete',
      lastRefresh: 'Last refresh',
      justLoaded: 'Just loaded',
      quickActions: 'Quick actions',
    }
  }
  return {
    welcomeBack: 'Bon retour',
    setupMode: 'Mode initialisation',
    operational: 'Opérationnel',
    loadingTitle: 'Chargement du guide de démarrage du tenant',
    loadingBody: "Nous vérifions les documents, membres, annonces et événements pour refléter l'état réel du tenant.",
    firstRunChecklist: 'Checklist de premier démarrage',
    complete: 'terminé',
    nextBestAction: 'Prochaine meilleure action',
    completed: 'Terminé',
    pending: 'En attente',
    tenantSnapshot: 'Aperçu du tenant',
    liveUsageSignals: "Signaux d'usage en direct",
    refresh: 'Actualiser',
    currentTenant: 'Tenant actuel',
    tenant: 'Tenant',
    role: 'Rôle',
    checklistComplete: 'Checklist terminée',
    lastRefresh: 'Dernière actualisation',
    justLoaded: 'À l’instant',
    quickActions: 'Actions rapides',
  }
})

const isSetupMode = computed(() => {
  return progressPercent.value < 100 && completedCount.value === 0
})

const dashboardKicker = computed(() => {
  if (localeStore.currentLocale === 'en') {
    if (isPrincipalAdmin.value) return 'Principal admin control plane'
    if (isMemberOnly.value) return 'Member portal'
    if (isTreasurer.value) return 'Finance workspace'
    if (isSecretaryGeneral.value) return 'Secretary workspace'
    if (isAuditor.value) return 'Finance audit'
    if (isCensor.value) return 'Disciplinary console'
    if (isSportsManager.value) return 'Sports workspace'
    if (isPresidentRole.value || isVicePresidentRole.value) return 'Governance cockpit'
    return 'Tenant overview'
  }
  if (localeStore.currentLocale === 'de') {
    if (isPrincipalAdmin.value) return 'Hauptadmin-Zentrale'
    if (isMemberOnly.value) return 'Mitgliederportal'
    if (isTreasurer.value) return 'Finanzbereich'
    if (isSecretaryGeneral.value) return 'Sekretariatsbereich'
    if (isAuditor.value) return 'Finanzaudit'
    if (isCensor.value) return 'Disziplinarkonsole'
    if (isSportsManager.value) return 'Sportbereich'
    if (isPresidentRole.value || isVicePresidentRole.value) return 'Governance-Cockpit'
    return 'Tenant-Ueberblick'
  }
  if (isPrincipalAdmin.value) return 'Espace administrateur principal'
  if (isMemberOnly.value) return 'Portail membre'
  if (isTreasurer.value) return 'Espace finances'
  if (isSecretaryGeneral.value) return 'Espace secrétariat'
  if (isAuditor.value) return 'Audit finances'
  if (isCensor.value) return 'Console disciplinaire'
  if (isSportsManager.value) return 'Espace sport'
  if (isPresidentRole.value || isVicePresidentRole.value) return 'Cockpit de gouvernance'
  return 'Aperçu du tenant'
})

const dashboardLead = computed(() => {
  const tenantName = tenantStore.currentTenantName
  if (localeStore.currentLocale === 'fr') {
    if (isPrincipalAdmin.value) {
      return `Votre tenant actuel est ${tenantName}. Utilisez cet espace pour l'administration globale sans compromettre l'isolation.`
    }
    if (isMemberOnly.value) {
      return `Votre tenant actuel est ${tenantName}. Consultez votre profil, vos cotisations et les informations associatives autorisées.`
    }
    if (isTreasurer.value) {
      return `Votre tenant actuel est ${tenantName}. Suivez les finances, les soldes membres et les paiements depuis l'espace dédié.`
    }
    if (isSecretaryGeneral.value) {
      return `Votre tenant actuel est ${tenantName}. Gardez les documents, règlements et annonces bien organisés depuis l'espace secrétariat.`
    }
    if (isAuditor.value) {
      return `Votre tenant actuel est ${tenantName}. Contrôlez les totaux financiers et les enregistrements prêts pour l'audit.`
    }
    if (isCensor.value) {
      return `Votre tenant actuel est ${tenantName}. Travaillez dans la console disciplinaire avec les frontières de confidentialité préservées.`
    }
    if (isSportsManager.value) {
      return `Votre tenant actuel est ${tenantName}. Gérez les activités sportives depuis un espace ciblé et sans surcharge.`
    }
    if (isPresidentRole.value || isVicePresidentRole.value) {
      return `Votre tenant actuel est ${tenantName}. Utilisez le cockpit de gouvernance pour une supervision claire de l'association.`
    }
    return `Votre tenant actuel est ${tenantName}. Le tableau de bord met en avant les prochaines actions les plus utiles.`
  }
  if (localeStore.currentLocale === 'de') {
    if (isPrincipalAdmin.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Nutzen Sie diese Zentrale fuer die tenant-weite Administration, ohne die Isolation zu gefaehrden.`
    }
    if (isMemberOnly.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Sehen Sie Ihr Profil, Ihre Beitraege und die fuer Sie freigegebenen Vereinsinformationen ein.`
    }
    if (isTreasurer.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Verfolgen Sie Finanzen, Mitgliedersalden und Zahlungen im dafuer vorgesehenen Bereich.`
    }
    if (isSecretaryGeneral.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Halten Sie Dokumente, Regeln und Ankuendigungen im Sekretariatsbereich ordentlich.`
    }
    if (isAuditor.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Kontrollieren Sie Finanzsummen und auditbereite Aufzeichnungen in sicherem Lesemodus.`
    }
    if (isCensor.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Arbeiten Sie in der Disziplinarkonsole bei gewahrter Vertraulichkeit.`
    }
    if (isSportsManager.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Verwalten Sie Sportaktivitaeten in einem fokussierten und klaren Bereich.`
    }
    if (isPresidentRole.value || isVicePresidentRole.value) {
      return `Ihr aktueller Tenant ist ${tenantName}. Nutzen Sie das Governance-Cockpit fuer eine klare Aufsicht ueber den Verein.`
    }
    return `Ihr aktueller Tenant ist ${tenantName}. Das Dashboard zeigt Ihnen die naechsten sinnvollen Schritte.`
  }
  if (isPrincipalAdmin.value) {
    return `Your current tenant is ${tenantName}. Use the control plane for tenant-wide administration without breaking isolation.`
  }
  if (isMemberOnly.value) {
    return `Your current tenant is ${tenantName}. Review your personal profile, contribution statement, and read-only association updates.`
  }
  if (isTreasurer.value) {
    return `Your current tenant is ${tenantName}. Review finance tasks, member balances, and payment activity from the dedicated workspace.`
  }
  if (isSecretaryGeneral.value) {
    return `Your current tenant is ${tenantName}. Keep documents, policies, and announcements tidy from the secretary workspace.`
  }
  if (isAuditor.value) {
    return `Your current tenant is ${tenantName}. Inspect finance totals and audit-ready records without mutation controls.`
  }
  if (isCensor.value) {
    return `Your current tenant is ${tenantName}. Work inside the disciplinary console with privacy boundaries preserved.`
  }
  if (isSportsManager.value) {
    return `Your current tenant is ${tenantName}. Manage sports events in a focused workspace with no extra noise.`
  }
  if (isPresidentRole.value || isVicePresidentRole.value) {
    return `Your current tenant is ${tenantName}. Use the governance cockpit for focused oversight across the association.`
  }
  return `Your current tenant is ${tenantName}. The dashboard highlights the next steps that matter most.`
})

function stepIcon(stepId: string): string {
  const map: Record<string, string> = {
    branding: 'bi bi-palette',
    documents: 'bi bi-file-earmark-text',
    members: 'bi bi-people',
    announcements: 'bi bi-megaphone',
    events: 'bi bi-calendar-event',
  }

  return map[stepId] || 'bi bi-arrow-right'
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

onMounted(refresh)
</script>

<style scoped>
.onboarding-card {
  border-radius: 1.25rem;
}

.checklist-item {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}

.checklist-item.completed {
  background: linear-gradient(180deg, rgba(25, 135, 84, 0.03), rgba(25, 135, 84, 0.01));
}

.step-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(31, 79, 143, 0.08);
  color: var(--om-primary, #1f4f8f);
  flex-shrink: 0;
}

.step-icon.completed {
  background: rgba(25, 135, 84, 0.12);
  color: #198754;
}

.metric-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  padding: 0.9rem;
  background: #fff;
}
</style>
