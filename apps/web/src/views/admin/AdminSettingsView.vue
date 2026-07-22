<template>
  <div class="p-4 p-lg-5">
    <div class="mb-4">
      <div class="text-uppercase small fw-semibold text-secondary mb-2">
        {{ copy.administration }}
      </div>
      <h1 class="h4 fw-bold mb-1">{{ copy.title }}</h1>
      <p class="text-muted mb-0">
        {{ copy.subtitle }}
      </p>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
        <div>
          <div class="fw-semibold">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ copy.workspaceErrorTitle }}
          </div>
          <p class="small mb-0 mt-2">{{ error }}</p>
          <p class="mb-0 small text-muted mt-1">{{ localeStore.t('common.recoveryHint') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm align-self-start" type="button" @click="retryLoadSettings" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ isRecovering ? localeStore.t('common.loading') : localeStore.t('common.retry') }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-muted py-5 text-center">
      {{ copy.loading }}
    </div>

    <div v-else-if="actionError" class="alert alert-danger">{{ actionError }}</div>

    <template v-else-if="settings">
      <div class="row g-4">
        <div class="col-lg-7">
          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">{{ copy.organization }}</h5>
              <div class="row g-3">
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.name }}</label>
                  <input v-model="form.name" type="text" class="form-control" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.slug }}</label>
                  <input :value="settings.slug" type="text" class="form-control" disabled />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.language }}</label>
                  <select v-model="form.default_language" class="form-select">
                    <option value="fr">{{ copy.languageFrench }}</option>
                    <option value="en">{{ copy.languageEnglish }}</option>
                    <option value="de">{{ copy.languageGerman }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">{{ copy.branding }}</h5>
              <div class="row g-3">
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.primaryColor }}</label>
                  <div class="d-flex align-items-center gap-2">
                    <input v-model="form.branding.primary_color" type="color" class="form-control form-control-color w-auto" />
                    <input v-model="form.branding.primary_color" type="text" class="form-control" :placeholder="copy.primaryColorPlaceholder" />
                  </div>
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.logoUrl }}</label>
                  <input v-model="form.branding.logo_url" type="text" class="form-control" :placeholder="copy.logoUrlPlaceholder" />
                </div>
              </div>
            </div>
          </div>

          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">{{ copy.modules }}</h5>
              <p class="small text-muted mb-3">
                {{ copy.modulesHint }}
              </p>
              <div class="row g-2">
                <div v-for="(enabled, key) in form.modules" :key="key" class="col-sm-6">
                  <div class="form-check">
                    <input
                      :id="'module-' + key"
                      v-model="form.modules[key]"
                      type="checkbox"
                      class="form-check-input"
                    />
                    <label :for="'module-' + key" class="form-check-label text-capitalize">
                      {{ moduleLabel(key) }}
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-2 mb-3">
                <div>
                  <h5 class="fw-semibold mb-1">{{ copy.recoveryEvidence }}</h5>
                  <p class="small text-muted mb-0">
                    {{ copy.recoveryHint }}
                  </p>
                </div>
                <span class="badge text-bg-light border align-self-start text-capitalize">
                  {{ statusLabel(settings?.operations.overall_status || 'unknown') }}
                </span>
              </div>

              <div v-if="settings?.operations.status_message" class="alert" :class="recoveryAlertClass(settings.operations.overall_status)">
                {{ settings.operations.status_message }}
              </div>

              <div class="row g-3">
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.lastBackupAt }}</label>
                  <input v-model="form.operations.last_backup_at" type="datetime-local" class="form-control" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.backupStatus }}</label>
                  <select v-model="form.operations.last_backup_status" class="form-select">
                    <option value="unknown">{{ copy.statusUnknown }}</option>
                    <option value="scheduled">{{ copy.statusScheduled }}</option>
                    <option value="completed">{{ copy.statusCompleted }}</option>
                    <option value="failed">{{ copy.statusFailed }}</option>
                  </select>
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.backupReference }}</label>
                  <input v-model="form.operations.last_backup_reference" type="text" class="form-control" :placeholder="copy.backupReferencePlaceholder" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.retentionDays }}</label>
                  <input v-model.number="form.operations.backup_retention_days" type="number" min="1" class="form-control" :placeholder="copy.retentionDaysPlaceholder" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.lastRestoreDrillAt }}</label>
                  <input v-model="form.operations.last_restore_drill_at" type="datetime-local" class="form-control" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.restoreDrillStatus }}</label>
                  <select v-model="form.operations.last_restore_drill_status" class="form-select">
                    <option value="unknown">{{ copy.statusUnknown }}</option>
                    <option value="not_run">{{ copy.statusNotRun }}</option>
                    <option value="passed">{{ copy.statusPassed }}</option>
                    <option value="failed">{{ copy.statusFailed }}</option>
                  </select>
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">{{ copy.alertPosture }}</label>
                  <select v-model="form.operations.alert_posture" class="form-select">
                    <option value="unknown">{{ copy.statusUnknown }}</option>
                    <option value="healthy">{{ copy.statusHealthy }}</option>
                    <option value="warning">{{ copy.statusWarning }}</option>
                    <option value="critical">{{ copy.statusCritical }}</option>
                  </select>
                </div>
                <div class="col-sm-6 d-flex align-items-end">
                  <div class="form-check mt-4">
                    <input
                      id="alert-contacts-configured"
                      v-model="form.operations.alert_contacts_configured"
                      type="checkbox"
                      class="form-check-input"
                    />
                    <label class="form-check-label" for="alert-contacts-configured">
                      {{ copy.alertContactsConfigured }}
                    </label>
                  </div>
                </div>
                <div class="col-12">
                  <label class="form-label small fw-semibold text-muted">{{ copy.notes }}</label>
                  <textarea v-model="form.operations.notes" rows="3" class="form-control" :placeholder="copy.notesPlaceholder"></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-5">
          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">{{ copy.summary }}</h5>
              <div class="vstack gap-2 small">
                <div class="d-flex justify-content-between">
                  <span class="text-muted">{{ copy.status }}</span>
                  <span class="badge text-bg-success">{{ copy.active }}</span>
                </div>
                <div class="d-flex justify-content-between">
                  <span class="text-muted">{{ copy.modulesEnabled }}</span>
                  <span class="fw-semibold">{{ enabledCount }} / {{ totalModules }}</span>
                </div>
                <div class="d-flex justify-content-between">
                  <span class="text-muted">{{ copy.language }}</span>
                  <span>{{ form.default_language.toUpperCase() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn om-primary-btn" :disabled="saving || loading" @click="saveSettings">
          {{ saving ? copy.saving : copy.saveSettings }}
        </button>
        <div v-if="saved" class="text-success small d-flex align-items-center">
          <i class="bi bi-check-circle me-1"></i> {{ copy.settingsSaved }}
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth.store";
import { useLocaleStore } from "@/stores/locale.store";
import { useRecoveryState } from "@/composables/useRecoveryState";
import {
  getTenantSettings,
  updateTenantSettings,
  checkModuleHasData,
  type TenantSettingsResponse,
  type ModuleToggles,
  type BrandingConfig,
  type RecoveryEvidenceConfig,
} from "../../api/settings.api";

const auth = useAuthStore();
const localeStore = useLocaleStore();
const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState();
const saving = ref(false);
const saved = ref(false);
const actionError = ref("");

const settings = ref<TenantSettingsResponse | null>(null);

const form = reactive<{
  name: string;
  default_language: string;
  branding: BrandingConfig;
  modules: ModuleToggles;
  operations: {
    last_backup_at: string;
    last_backup_status: string;
    last_backup_reference: string;
    last_restore_drill_at: string;
    last_restore_drill_status: string;
    alert_posture: string;
    alert_contacts_configured: boolean;
    backup_retention_days: number | null;
    notes: string;
  };
}>({
  name: "",
  default_language: "fr",
  branding: { primary_color: "#1f4f8f", logo_url: "" },
  modules: {
    membership: true,
    contributions: true,
    policies: true,
    disciplinary: true,
    events: true,
    announcements: true,
    chat: true,
    notifications: true,
  },
  operations: {
    last_backup_at: "",
    last_backup_status: "unknown",
    last_backup_reference: "",
    last_restore_drill_at: "",
    last_restore_drill_status: "unknown",
    alert_posture: "unknown",
    alert_contacts_configured: false,
    backup_retention_days: null,
    notes: "",
  },
});

const enabledCount = computed(() => {
  return Object.values(form.modules).filter(Boolean).length;
});

const totalModules = computed(() => {
  return Object.keys(form.modules).length;
});

const copy = computed(() => {
  if (localeStore.currentLocale === "de") {
    return {
      administration: "Administration",
      title: "Mandanteneinstellungen",
      subtitle: "Konfigurieren Sie Organisationsname, Erscheinungsbild und aktivierte Module.",
      loading: "Einstellungen werden geladen...",
      organization: "Organisation",
      name: "Name",
      slug: "Slug",
      language: "Sprache",
      languageFrench: "Französisch",
      languageEnglish: "Englisch",
      languageGerman: "Deutsch",
      branding: "Erscheinungsbild",
      primaryColor: "Primärfarbe",
      primaryColorPlaceholder: "#1f4f8f",
      logoUrl: "Logo-URL",
      logoUrlPlaceholder: "https://example.com/logo.png",
      modules: "Module",
      modulesHint: "Aktivieren oder deaktivieren Sie Produktmodule für diesen Mandanten. Deaktivierte Module werden für Nutzer ausgeblendet.",
      recoveryEvidence: "Nachweis zur Wiederherstellung",
      recoveryHint: "Dokumentieren Sie die letzten Sicherungs- und Wiederherstellungsnachweise, damit Betreiber die Aktualität der Wiederherstellungsfähigkeit sehen.",
      lastBackupAt: "Letzte Sicherung am",
      backupStatus: "Sicherungsstatus",
      backupReference: "Sicherungsreferenz",
      backupReferencePlaceholder: "kairo-backup-20260704_030000.tar.gz",
      retentionDays: "Aufbewahrungstage",
      retentionDaysPlaceholder: "30",
      lastRestoreDrillAt: "Letzter Restore-Test am",
      restoreDrillStatus: "Status des Restore-Tests",
      alertPosture: "Alarmstatus",
      alertContactsConfigured: "Alarmkontakte konfiguriert",
      notes: "Notizen",
      notesPlaceholder: "Kurze Notiz zum letzten Restore-Test oder Sicherungsübergang hinzufügen.",
      summary: "Zusammenfassung",
      status: "Status",
      active: "Aktiv",
      modulesEnabled: "Aktivierte Module",
      saveSettings: "Einstellungen speichern",
      saving: "Speichern...",
      settingsSaved: "Einstellungen gespeichert",
      statusUnknown: "Unbekannt",
      statusScheduled: "Geplant",
      statusCompleted: "Abgeschlossen",
      statusFailed: "Fehlgeschlagen",
      statusNotRun: "Nicht ausgeführt",
      statusPassed: "Bestanden",
      statusHealthy: "Stabil",
      statusWarning: "Warnung",
      statusCritical: "Kritisch",
      loadError: "Die Einstellungen konnten nicht geladen werden. Stellen Sie sicher, dass Sie als Administrator angemeldet sind.",
      saveError: "Die Einstellungen konnten nicht gespeichert werden. Prüfen Sie Ihre Berechtigungen.",
      disableConfirm: "\"{module}\" enthält bereits Daten. Beim Deaktivieren werden diese für Nutzer ausgeblendet. Möchten Sie fortfahren?",
      workspaceErrorTitle: "Die Tenant-Einstellungen sind nicht verfügbar",
    };
  }
  if (localeStore.currentLocale === "en") {
    return {
      administration: "Administration",
      title: "Tenant settings",
      subtitle: "Configure your organization name, branding, and enabled modules.",
      loading: "Loading settings...",
      organization: "Organization",
      name: "Name",
      slug: "Slug",
      language: "Language",
      languageFrench: "French",
      languageEnglish: "English",
      languageGerman: "German",
      branding: "Branding",
      primaryColor: "Primary color",
      primaryColorPlaceholder: "#1f4f8f",
      logoUrl: "Logo URL",
      logoUrlPlaceholder: "https://example.com/logo.png",
      modules: "Modules",
      modulesHint: "Enable or disable product modules for this tenant. Disabled modules are hidden from users.",
      recoveryEvidence: "Recovery evidence",
      recoveryHint: "Record the latest backup and restore drill evidence so operators can see whether recovery posture is fresh.",
      lastBackupAt: "Last backup at",
      backupStatus: "Backup status",
      backupReference: "Backup reference",
      backupReferencePlaceholder: "kairo-backup-20260704_030000.tar.gz",
      retentionDays: "Retention days",
      retentionDaysPlaceholder: "30",
      lastRestoreDrillAt: "Last restore drill at",
      restoreDrillStatus: "Restore drill status",
      alertPosture: "Alert posture",
      alertContactsConfigured: "Alert contacts configured",
      notes: "Notes",
      notesPlaceholder: "Add a short note about the latest recovery drill or backup handoff.",
      summary: "Summary",
      status: "Status",
      active: "Active",
      modulesEnabled: "Modules enabled",
      saveSettings: "Save settings",
      saving: "Saving...",
      settingsSaved: "Settings saved",
      statusUnknown: "Unknown",
      statusScheduled: "Scheduled",
      statusCompleted: "Completed",
      statusFailed: "Failed",
      statusNotRun: "Not run",
      statusPassed: "Passed",
      statusHealthy: "Healthy",
      statusWarning: "Warning",
      statusCritical: "Critical",
      loadError: "Failed to load settings. Make sure you are logged in as admin.",
      saveError: "Failed to save settings. Check your permissions.",
      disableConfirm: "\"{module}\" has existing data. Disabling it will hide that data from users. Are you sure?",
      workspaceErrorTitle: "Tenant settings unavailable",
    };
  }
  return {
    administration: "Administration",
    title: "Réglages du tenant",
    subtitle: "Configurez le nom de votre organisation, son identité visuelle et les modules activés.",
    loading: "Chargement des réglages...",
    organization: "Organisation",
    name: "Nom",
    slug: "Slug",
    language: "Langue",
    languageFrench: "Français",
    languageEnglish: "Anglais",
    languageGerman: "Allemand",
    branding: "Identité visuelle",
    primaryColor: "Couleur principale",
    primaryColorPlaceholder: "#1f4f8f",
    logoUrl: "URL du logo",
    logoUrlPlaceholder: "https://example.com/logo.png",
    modules: "Modules",
    modulesHint: "Activez ou désactivez les modules du produit pour ce tenant. Les modules désactivés sont masqués pour les utilisateurs.",
    recoveryEvidence: "Preuves de reprise",
    recoveryHint: "Consignez les derniers éléments de sauvegarde et de test de restauration afin que les opérateurs puissent voir si la posture de reprise est à jour.",
    lastBackupAt: "Dernière sauvegarde le",
    backupStatus: "Statut de sauvegarde",
    backupReference: "Référence de sauvegarde",
    backupReferencePlaceholder: "kairo-backup-20260704_030000.tar.gz",
    retentionDays: "Jours de rétention",
    retentionDaysPlaceholder: "30",
    lastRestoreDrillAt: "Dernier test de restauration le",
    restoreDrillStatus: "Statut du test de restauration",
    alertPosture: "Posture d'alerte",
    alertContactsConfigured: "Contacts d'alerte configurés",
    notes: "Notes",
    notesPlaceholder: "Ajoutez une courte note sur le dernier test de restauration ou le dernier transfert de sauvegarde.",
    summary: "Résumé",
    status: "Statut",
    active: "Actif",
    modulesEnabled: "Modules activés",
    saveSettings: "Enregistrer les réglages",
    saving: "Enregistrement...",
    settingsSaved: "Réglages enregistrés",
    statusUnknown: "Inconnu",
    statusScheduled: "Planifié",
    statusCompleted: "Terminé",
    statusFailed: "Échoué",
    statusNotRun: "Non exécuté",
    statusPassed: "Réussi",
    statusHealthy: "Sain",
    statusWarning: "Avertissement",
    statusCritical: "Critique",
    loadError: "Impossible de charger les réglages. Assurez-vous d'être connecté en tant qu'administrateur.",
    saveError: "Impossible d'enregistrer les réglages. Vérifiez vos permissions.",
    disableConfirm: "\"{module}\" contient déjà des données. Le désactiver masquera ces données aux utilisateurs. Voulez-vous continuer ?",
    workspaceErrorTitle: "Les réglages du tenant sont indisponibles",
  };
});

function moduleLabel(key: string): string {
  const labels: Record<string, string> = {
    membership: localeStore.currentLocale === "de" ? "Mitglieder" : localeStore.currentLocale === "en" ? "Membership" : "Membres",
    contributions: localeStore.currentLocale === "de" ? "Beiträge" : localeStore.currentLocale === "en" ? "Contributions" : "Cotisations",
    policies: localeStore.currentLocale === "de" ? "Richtlinien" : localeStore.currentLocale === "en" ? "Policies" : "Règlements",
    disciplinary: localeStore.currentLocale === "de" ? "Disziplin" : localeStore.currentLocale === "en" ? "Disciplinary" : "Discipline",
    events: localeStore.currentLocale === "de" ? "Veranstaltungen" : localeStore.currentLocale === "en" ? "Events" : "Événements",
    announcements: localeStore.currentLocale === "de" ? "Mitteilungen" : localeStore.currentLocale === "en" ? "Announcements" : "Annonces",
    chat: localeStore.currentLocale === "de" ? "KI-Chat" : localeStore.currentLocale === "en" ? "AI Chat" : "Chat IA",
    notifications: localeStore.currentLocale === "de" ? "Benachrichtigungen" : localeStore.currentLocale === "en" ? "Notifications" : "Notifications",
  };
  return labels[key] || key;
}

function applySettings(value: TenantSettingsResponse) {
  settings.value = value;
  form.name = value.name;
  form.default_language = value.default_language;
  form.branding = { ...value.branding };
  form.modules = { ...value.modules };
  form.operations = {
    last_backup_at: toDateTimeLocal(value.operations.last_backup_at),
    last_backup_status: value.operations.last_backup_status || "unknown",
    last_backup_reference: value.operations.last_backup_reference || "",
    last_restore_drill_at: toDateTimeLocal(value.operations.last_restore_drill_at),
    last_restore_drill_status: value.operations.last_restore_drill_status || "unknown",
    alert_posture: value.operations.alert_posture || "unknown",
    alert_contacts_configured: value.operations.alert_contacts_configured,
    backup_retention_days: value.operations.backup_retention_days,
    notes: value.operations.notes || "",
  };
}

async function loadSettings() {
  if (!auth.user?.tenant_id) {
    throw new Error(copy.value.loadError);
  }
  applySettings(await getTenantSettings(auth.user.tenant_id));
}

async function refreshLoadSettings() {
  clearError();
  await run(loadSettings);
}

async function retryLoadSettings() {
  await retry(loadSettings);
}

async function saveSettings() {
  if (!auth.user?.tenant_id) return;

  // Warn if disabling a module that has existing data
  const disabledModules = Object.keys(form.modules).filter(
    (key) => !form.modules[key as keyof ModuleToggles]
  );
  for (const module of disabledModules) {
    const hasData = await checkModuleHasData(auth.user.tenant_id, module);
    if (hasData) {
      const confirmed = confirm(
        copy.value.disableConfirm.replace("{module}", moduleLabel(module))
      );
      if (!confirmed) return;
      break;
    }
  }

  saving.value = true;
  saved.value = false;
  actionError.value = "";
  try {
    const result = await updateTenantSettings(auth.user.tenant_id, {
      ...(form.name !== settings.value?.name ? { name: form.name } : {}),
      ...(form.default_language !== settings.value?.default_language
        ? { default_language: form.default_language }
        : {}),
      branding: form.branding,
      modules: form.modules,
      operations: buildOperationsPayload(),
    });
    applySettings(result);
    saved.value = true;
    setTimeout(() => { saved.value = false; }, 3000);
  } catch (err: unknown) {
    actionError.value = copy.value.saveError;
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  refreshLoadSettings();
});

function toDateTimeLocal(value: string | null): string {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toIsoOrNull(value: string): string | null {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function buildOperationsPayload(): Partial<RecoveryEvidenceConfig> {
  return {
    last_backup_at: toIsoOrNull(form.operations.last_backup_at),
    last_backup_status: form.operations.last_backup_status,
    last_backup_reference: form.operations.last_backup_reference,
    last_restore_drill_at: toIsoOrNull(form.operations.last_restore_drill_at),
    last_restore_drill_status: form.operations.last_restore_drill_status,
    alert_posture: form.operations.alert_posture,
    alert_contacts_configured: form.operations.alert_contacts_configured,
    backup_retention_days: form.operations.backup_retention_days ?? null,
    notes: form.operations.notes,
  };
}

function recoveryAlertClass(status: string): string {
  if (status === "healthy") return "alert-success";
  if (status === "critical") return "alert-danger";
  return "alert-warning";
}

function statusLabel(status: string): string {
  switch (status) {
    case "scheduled":
      return copy.value.statusScheduled;
    case "completed":
      return copy.value.statusCompleted;
    case "failed":
      return copy.value.statusFailed;
    case "not_run":
      return copy.value.statusNotRun;
    case "passed":
      return copy.value.statusPassed;
    case "healthy":
      return copy.value.statusHealthy;
    case "warning":
      return copy.value.statusWarning;
    case "critical":
      return copy.value.statusCritical;
    default:
      return copy.value.statusUnknown;
  }
}
</script>
