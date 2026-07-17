<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2" data-testid="admin-onboarding-kicker">
          {{ copy.kicker }}
        </div>
        <h1 class="h4 fw-bold mb-1" data-testid="admin-onboarding-title">{{ copy.title }}</h1>
        <p class="text-muted mb-0">
          {{ introCopy }}
        </p>
      </div>
      <div class="d-flex gap-2 align-self-start">
        <RouterLink to="/admin/health" class="btn btn-outline-secondary" data-testid="admin-onboarding-health-button">
          <i class="bi bi-heart-pulse me-1"></i>{{ copy.healthCenter }}
        </RouterLink>
        <button class="btn om-primary-btn" type="button" :disabled="loading || isRecovering" @click="refresh">
          {{ loading ? copy.refreshing : copy.refreshSetupState }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
        <div>
          <div class="fw-semibold">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ copy.workspaceErrorTitle }}
          </div>
          <p class="small mb-0 mt-2">{{ error }}</p>
          <p class="mb-0 small text-muted mt-1">{{ t('common.recoveryHint') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm align-self-start" type="button" @click="retryRefresh" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ isRecovering ? t('common.loading') : t('common.retry') }}
        </button>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <div class="card shadow-sm border-0 onboarding-card h-100" data-testid="admin-onboarding-checklist">
          <div class="card-body p-4 p-xl-5">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-4">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  {{ copy.launchChecklist }}
                </div>
                <h2 class="h5 fw-bold mb-2">{{ statusTitle }}</h2>
                <p class="text-muted mb-0">
                  {{ statusMessage }}
                </p>
              </div>
              <div class="text-md-end">
                <div class="display-6 fw-bold lh-1" data-testid="admin-onboarding-progress">
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

            <div v-if="nextStep" class="alert alert-primary border-0 mb-4" data-testid="admin-onboarding-next-step">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                <div>
                  <div class="fw-semibold mb-1">{{ copy.nextBestAction }}</div>
                  <p class="small mb-0">
                    {{ nextStep.title }}: {{ nextStep.description }}
                  </p>
                </div>
                <RouterLink :to="nextStep.to" class="btn btn-sm btn-primary align-self-start">
                  {{ nextStep.actionLabel }}
                </RouterLink>
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

      <div class="col-xl-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.firstActions }}
            </div>
            <h2 class="h6 fw-bold mb-3">{{ copy.whatToDoFirst }}</h2>
            <ol class="setup-list mb-0">
              <li>{{ copy.firstAction1 }}</li>
              <li>{{ copy.firstAction2 }}</li>
              <li>{{ copy.firstAction3 }}</li>
              <li>{{ copy.firstAction4 }}</li>
              <li>{{ copy.firstAction5 }}</li>
            </ol>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.demoSeed }}
            </div>
            <h2 class="h6 fw-bold mb-3">{{ copy.demoSeedTitle }}</h2>
            <p class="small text-muted mb-3">
              {{ copy.demoSeedText }}
            </p>

            <div class="seed-block mb-3" data-testid="admin-onboarding-seed-bash">
              <div class="small text-muted mb-2">{{ copy.macosLinux }}</div>
              <code>./seed/seed-multi-tenant.sh</code>
            </div>

            <div class="seed-block" data-testid="admin-onboarding-seed-powershell">
              <div class="small text-muted mb-2">{{ copy.windowsPowerShell }}</div>
              <code>.\seed\seed-multi-tenant.ps1</code>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.guidedLinks }}
            </div>
            <div class="vstack gap-2" data-testid="admin-onboarding-links">
              <RouterLink
                v-for="link in guidedLinks"
                :key="link.to"
                :to="link.to"
                class="wizard-link"
              >
                <div class="fw-semibold">{{ link.label }}</div>
                <div class="small text-muted">{{ link.description }}</div>
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.successCriteria }}
            </div>
            <h2 class="h6 fw-bold mb-3">{{ copy.firstWeekReady }}</h2>
            <ul class="success-list mb-0">
              <li>{{ copy.success1 }}</li>
              <li>{{ copy.success2 }}</li>
              <li>{{ copy.success3 }}</li>
              <li>{{ copy.success4 }}</li>
              <li>{{ copy.success5 }}</li>
            </ul>
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
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantOnboarding } from '@/composables/useTenantOnboarding'

const authStore = useAuthStore()
const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const isPrincipalAdmin = computed(() => authStore.user?.roles.includes('principal_admin') ?? false)
const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      kicker: 'Ersteinrichtung',
      title: 'Onboarding-Assistent',
      healthCenter: 'Health Center',
      refreshing: 'Aktualisierung...',
      refreshSetupState: 'Einrichtungsstatus aktualisieren',
      workspaceErrorTitle: 'Onboarding-Assistent nicht verfügbar',
      introPrincipal:
        'Nutzen Sie diese Steuerungsansicht, um von einem leeren Tenant zu einer arbeitsfaehigen Startkonfiguration zu gelangen, ohne Demo-Hinweise mit echten Produktionsentscheidungen zu vermischen.',
      introAdmin:
        'Nutzen Sie diese Einrichtungsansicht, um mit einer klaren Reihenfolge und einem verlässlichen Demo-Pfad von einem leeren Tenant zu einer arbeitsfaehigen Startkonfiguration zu gelangen.',
      launchChecklist: 'Start-Checkliste',
      complete: 'abgeschlossen',
      nextBestAction: 'Naechste sinnvolle Aktion',
      completed: 'Abgeschlossen',
      pending: 'Ausstehend',
      firstActions: 'Erste Schritte',
      whatToDoFirst: 'Womit Sie beginnen sollten',
      firstAction1: 'Tenant-Branding und Modulschalter bestaetigen.',
      firstAction2: 'Das erste vertrauenswuerdige Dokument hochladen.',
      firstAction3: 'Mitglieder hinzufuegen oder importieren und Zugriffe pruefen.',
      firstAction4: 'Die erste Mitteilung oder Veranstaltung veroeffentlichen.',
      firstAction5: 'Health Center und Wiederherstellungsnachweise pruefen.',
      demoSeed: 'Demo-Seed',
      demoSeedTitle: 'Einen zweiten Tenant fuer Browser-Demos befuellen',
      demoSeedText:
        'Nutzen Sie den Multi-Tenant-Helfer fuer einen wiederholbaren Demo-Stack. Produktionsdaten bleiben getrennt und Kundendaten werden explizit importiert.',
      macosLinux: 'macOS / Linux',
      windowsPowerShell: 'Windows PowerShell',
      guidedLinks: 'Gefuehrte Links',
      successCriteria: 'Erfolgskriterien',
      firstWeekReady: 'Bereit fuer die erste Woche',
      success1: 'Die Administration kann sich anmelden und den Tenant-Zustand sofort verstehen.',
      success2: 'Das erste Dokument ist sichtbar und wird korrekt verarbeitet.',
      success3: 'Mitglieder koennen ohne Unklarheiten hinzugefuegt oder importiert werden.',
      success4: 'Mitteilungen und Veranstaltungen haben einen klaren Platz im Startbetrieb.',
      success5: 'Wiederherstellungsnachweise sind im Health Center und in den Einstellungen sichtbar.',
      settings: 'Tenant-Einstellungen',
      settingsText: 'Branding, Module und Wiederherstellungsnachweise',
      documents: 'Dokumente',
      documentsText: 'Die erste vertrauenswuerdige Quelle hochladen',
      members: 'Mitglieder',
      membersText: 'Das erste Mitgliederverzeichnis importieren oder erstellen',
      access: 'Zugaenge',
      accessText: 'Kolleginnen und Kollegen einladen und das Onboarding verfolgen',
      announcements: 'Ankuendigungen',
      announcementsText: 'Die erste Kommunikation veroeffentlichen',
      events: 'Veranstaltungen',
      eventsText: 'Die erste Aktivitaet planen',
      tenantOperations: 'Tenant-Operationen',
      tenantOperationsText: 'Mitgliedschaften pruefen und Kontext explizit wechseln',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      kicker: 'First-run setup',
      title: 'Onboarding wizard',
      healthCenter: 'Health center',
      refreshing: 'Refreshing...',
      refreshSetupState: 'Refresh setup state',
      workspaceErrorTitle: 'Onboarding wizard unavailable',
      introPrincipal:
        'Use this control-plane view to move from a blank tenant into a working launch configuration without mixing demo guidance with live production decisions.',
      introAdmin:
        'Use this setup view to move from a blank tenant into a working launch configuration with a clear sequence and a predictable demo seed path.',
      launchChecklist: 'Launch checklist',
      complete: 'complete',
      nextBestAction: 'Next best action',
      completed: 'Completed',
      pending: 'Pending',
      firstActions: 'First actions',
      whatToDoFirst: 'What to do first',
      firstAction1: 'Confirm tenant branding and module toggles.',
      firstAction2: 'Upload the first trusted document.',
      firstAction3: 'Add or import members and review access.',
      firstAction4: 'Publish the first announcement or event.',
      firstAction5: 'Verify the health center and recovery evidence.',
      demoSeed: 'Demo seed',
      demoSeedTitle: 'Populate a second tenant for browser demos',
      demoSeedText:
        'Use the multi-tenant helper when you want a repeatable demo stack. Keep production data separate and import customer data explicitly.',
      macosLinux: 'macOS / Linux',
      windowsPowerShell: 'Windows PowerShell',
      guidedLinks: 'Guided links',
      successCriteria: 'Success criteria',
      firstWeekReady: 'First week ready',
      success1: 'The admin can sign in and understand the tenant state immediately.',
      success2: 'The first document is visible and ingesting correctly.',
      success3: 'Members can be added or imported without confusion.',
      success4: 'Launch communications and events have a clear place to live.',
      success5: 'Recovery evidence is visible in the health center and settings.',
      settings: 'Tenant settings',
      settingsText: 'Branding, modules, and recovery evidence',
      documents: 'Documents',
      documentsText: 'Upload the first trusted source',
      members: 'Members',
      membersText: 'Import or create the first directory entries',
      access: 'Access',
      accessText: 'Invite teammates and monitor onboarding',
      announcements: 'Announcements',
      announcementsText: 'Publish the first communication',
      events: 'Events',
      eventsText: 'Schedule the first activity',
      tenantOperations: 'Tenant operations',
      tenantOperationsText: 'Inspect memberships and switch context explicitly',
    }
  }
  return {
    kicker: 'Initialisation',
    title: 'Assistant de démarrage',
    healthCenter: 'Centre de santé',
    refreshing: 'Actualisation...',
    refreshSetupState: "Actualiser l'état de préparation",
    workspaceErrorTitle: "L'assistant de démarrage est indisponible",
    introPrincipal:
      'Utilisez cette vue de pilotage pour passer d’un tenant vide à une configuration exploitable sans mélanger les repères de démonstration et les décisions de production.',
    introAdmin:
      'Utilisez cette vue de préparation pour passer d’un tenant vide à une configuration exploitable avec une séquence claire et un chemin de démonstration prévisible.',
    launchChecklist: 'Checklist de lancement',
    complete: 'terminé',
    nextBestAction: 'Prochaine meilleure action',
    completed: 'Terminé',
    pending: 'En attente',
    firstActions: 'Premières actions',
    whatToDoFirst: 'Par quoi commencer',
    firstAction1: 'Confirmer le branding du tenant et les modules activés.',
    firstAction2: 'Importer le premier document de confiance.',
    firstAction3: 'Ajouter ou importer des membres et vérifier les accès.',
    firstAction4: 'Publier la première annonce ou le premier événement.',
    firstAction5: 'Vérifier le centre de santé et les preuves de reprise.',
    demoSeed: 'Seed de démo',
    demoSeedTitle: 'Peupler un second tenant pour les démonstrations navigateur',
    demoSeedText:
      'Utilisez le helper multi-tenant quand vous voulez une pile de démo reproductible. Gardez les données de production séparées et importez explicitement les données client.',
    macosLinux: 'macOS / Linux',
    windowsPowerShell: 'Windows PowerShell',
    guidedLinks: 'Liens guidés',
    successCriteria: 'Critères de réussite',
    firstWeekReady: 'Prêt pour la première semaine',
    success1: 'L’administration peut se connecter et comprendre immédiatement l’état du tenant.',
    success2: 'Le premier document est visible et correctement ingéré.',
    success3: 'Les membres peuvent être ajoutés ou importés sans confusion.',
    success4: 'Les communications et événements de lancement ont un espace clair.',
    success5: 'Les preuves de reprise sont visibles dans le centre de santé et les réglages.',
    settings: 'Réglages du tenant',
    settingsText: 'Branding, modules et preuves de reprise',
    documents: 'Documents',
    documentsText: 'Importer la première source de confiance',
    members: 'Membres',
    membersText: 'Importer ou créer les premières entrées du répertoire',
    access: 'Accès',
    accessText: "Inviter des collègues et suivre l'onboarding",
    announcements: 'Annonces',
    announcementsText: 'Publier la première communication',
    events: 'Événements',
    eventsText: 'Planifier la première activité',
    tenantOperations: 'Opérations tenant',
    tenantOperationsText: 'Inspecter les appartenances et changer explicitement de contexte',
  }
})
const introCopy = computed(() =>
  isPrincipalAdmin.value ? copy.value.introPrincipal : copy.value.introAdmin,
)

const {
  loading,
  error,
  isRecovering,
  checklist,
  progressPercent,
  statusTitle,
  statusMessage,
  nextStep,
  refresh,
  retryRefresh,
} = useTenantOnboarding()

const guidedLinks = computed(() => [
  {
    label: copy.value.settings,
    description: copy.value.settingsText,
    to: '/admin/settings',
  },
  {
    label: copy.value.documents,
    description: copy.value.documentsText,
    to: '/admin/documents',
  },
  {
    label: copy.value.members,
    description: copy.value.membersText,
    to: '/admin/members',
  },
  {
    label: copy.value.access,
    description: copy.value.accessText,
    to: '/admin/access',
  },
  {
    label: copy.value.announcements,
    description: copy.value.announcementsText,
    to: '/admin/announcements',
  },
  {
    label: copy.value.events,
    description: copy.value.eventsText,
    to: '/admin/events',
  },
  {
    label: copy.value.tenantOperations,
    description: copy.value.tenantOperationsText,
    to: '/admin/tenants',
  },
])

function stepIcon(stepId: string): string {
  const icons: Record<string, string> = {
    branding: 'bi bi-palette',
    documents: 'bi bi-file-earmark-text',
    finance: 'bi bi-cash-coin',
    members: 'bi bi-people',
    announcements: 'bi bi-megaphone',
    events: 'bi bi-calendar-event',
  }

  return icons[stepId] || 'bi bi-arrow-right'
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

.wizard-link {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  padding: 0.85rem 1rem;
  text-decoration: none;
  color: inherit;
  background: #fff;
}

.wizard-link:hover {
  border-color: var(--om-primary, #1f4f8f);
  box-shadow: 0 0.5rem 1rem rgba(31, 79, 143, 0.08);
}

.seed-block {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  padding: 0.85rem 1rem;
  background: #fff;
}

.setup-list,
.success-list {
  padding-left: 1.15rem;
}
</style>
