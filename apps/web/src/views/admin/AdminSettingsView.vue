<template>
  <div class="p-4 p-lg-5">
    <div class="mb-4">
      <div class="text-uppercase small fw-semibold text-secondary-emphasis mb-2">
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

              <h6 class="fw-semibold text-muted mb-2">{{ copy.brandingIdentity }}</h6>
              <div class="row g-3">
                <div class="col-md-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-display-name">{{ copy.brandingDisplayName }}</label>
                  <input id="brand-display-name" v-model="form.branding.display_name" type="text" class="form-control" />
                </div>
                <div class="col-md-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-short-name">{{ copy.brandingShortName }}</label>
                  <input id="brand-short-name" v-model="form.branding.short_name" type="text" class="form-control" />
                </div>
                <div class="col-md-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-legal-name">{{ copy.brandingLegalName }}</label>
                  <input id="brand-legal-name" v-model="form.branding.legal_name" type="text" class="form-control" />
                </div>
                <div class="col-md-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-tagline">{{ copy.brandingTagline }}</label>
                  <input id="brand-tagline" v-model="form.branding.tagline" type="text" class="form-control" />
                </div>
              </div>

              <h6 class="fw-semibold text-muted mb-2 mt-4">{{ copy.brandingColors }}</h6>
              <div class="row g-3">
                <div class="col-sm-6 col-lg-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-primary-color">{{ copy.primaryColor }}</label>
                  <div class="d-flex align-items-center gap-2">
                    <input id="brand-primary-color" v-model="form.branding.primary_color" type="color" class="form-control form-control-color w-auto" />
                    <input v-model="form.branding.primary_color" type="text" class="form-control" :placeholder="copy.primaryColorPlaceholder" />
                  </div>
                </div>
                <div class="col-sm-6 col-lg-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-secondary-color">{{ copy.brandingSecondaryColor }}</label>
                  <div class="d-flex align-items-center gap-2">
                    <input id="brand-secondary-color" v-model="form.branding.secondary_color" type="color" class="form-control form-control-color w-auto" />
                    <input v-model="form.branding.secondary_color" type="text" class="form-control" />
                  </div>
                </div>
                <div class="col-sm-6 col-lg-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-background-color">{{ copy.brandingBackgroundColor }}</label>
                  <div class="d-flex align-items-center gap-2">
                    <input id="brand-background-color" v-model="form.branding.background_color" type="color" class="form-control form-control-color w-auto" />
                    <input v-model="form.branding.background_color" type="text" class="form-control" />
                  </div>
                </div>
                <div class="col-sm-6 col-lg-3">
                  <label class="form-label small fw-semibold text-muted" for="brand-theme-color">{{ copy.brandingThemeColor }}</label>
                  <div class="d-flex align-items-center gap-2">
                    <input id="brand-theme-color" v-model="form.branding.theme_color" type="color" class="form-control form-control-color w-auto" />
                    <input v-model="form.branding.theme_color" type="text" class="form-control" />
                  </div>
                </div>
              </div>

              <h6 class="fw-semibold text-muted mb-2 mt-4">{{ copy.brandingLogos }}</h6>
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-logo">{{ copy.logoUrl }}</label>
                  <input id="brand-logo" v-model="form.branding.logo_url" type="text" class="form-control" :placeholder="copy.logoUrlPlaceholder" />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-logo-dark">{{ copy.brandingLogoDarkUrl }}</label>
                  <input id="brand-logo-dark" v-model="form.branding.logo_dark_url" type="text" class="form-control" />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-favicon">{{ copy.brandingFaviconUrl }}</label>
                  <input id="brand-favicon" v-model="form.branding.favicon_url" type="text" class="form-control" placeholder="/favicon.svg" />
                </div>
              </div>

              <h6 class="fw-semibold text-muted mb-2 mt-4">{{ copy.brandingIcons }}</h6>
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-icon-192">{{ copy.brandingIcon192 }}</label>
                  <input id="brand-icon-192" v-model="form.branding.icon_192_url" type="text" class="form-control" placeholder="/pwa-192x192.png" />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-icon-512">{{ copy.brandingIcon512 }}</label>
                  <input id="brand-icon-512" v-model="form.branding.icon_512_url" type="text" class="form-control" placeholder="/pwa-512x512.png" />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-icon-maskable">{{ copy.brandingMaskable }}</label>
                  <input id="brand-icon-maskable" v-model="form.branding.maskable_icon_url" type="text" class="form-control" placeholder="/pwa-512x512.png" />
                </div>
              </div>
              <p class="small text-muted mb-0 mt-2">{{ copy.brandingIconsHint }}</p>

              <h6 class="fw-semibold text-muted mb-2 mt-4">{{ copy.brandingNotifications }}</h6>
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-notification-name">{{ copy.brandingNotificationName }}</label>
                  <input id="brand-notification-name" v-model="form.branding.notification_name" type="text" class="form-control" />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-support-name">{{ copy.brandingSupportName }}</label>
                  <input id="brand-support-name" v-model="form.branding.support_name" type="text" class="form-control" />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold text-muted" for="brand-support-email">{{ copy.brandingSupportEmail }}</label>
                  <input id="brand-support-email" v-model="form.branding.support_email" type="email" class="form-control" />
                </div>
              </div>

              <h6 class="fw-semibold text-muted mb-2 mt-4">{{ copy.brandingDomain }}</h6>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small fw-semibold text-muted" for="brand-custom-domain">{{ copy.brandingCustomDomain }}</label>
                  <input id="brand-custom-domain" v-model="form.branding.custom_domain" type="text" class="form-control" placeholder="app.association.example" />
                  <p class="small text-muted mb-0 mt-1">{{ copy.brandingCustomDomainHint }}</p>
                </div>
              </div>

              <div class="branding-preview mt-4 p-3" :style="{ backgroundColor: form.branding.background_color }">
                <strong class="d-block small text-muted text-uppercase mb-2">{{ copy.brandingPreview }}</strong>
                <div class="d-flex align-items-center gap-2">
                  <img v-if="form.branding.logo_url" :src="brandingAsset(form.branding.logo_url, '')" alt="" class="branding-preview__logo" />
                  <span v-else class="branding-preview__mark" :style="{ backgroundColor: form.branding.primary_color }" aria-hidden="true">
                    <i class="bi bi-diagram-3"></i>
                  </span>
                  <span>
                    <strong class="d-block" :style="{ color: form.branding.primary_color }">{{ form.branding.display_name }}</strong>
                    <small class="text-muted">{{ form.branding.short_name }}</small>
                  </span>
                </div>
                <div class="d-flex gap-2 mt-2">
                  <span class="branding-preview__swatch" :style="{ backgroundColor: form.branding.primary_color }"></span>
                  <span class="branding-preview__swatch" :style="{ backgroundColor: form.branding.secondary_color }"></span>
                  <span class="branding-preview__swatch" :style="{ backgroundColor: form.branding.theme_color }"></span>
                  <span class="branding-preview__swatch" :style="{ backgroundColor: form.branding.background_color }"></span>
                </div>
                <div class="d-flex align-items-end gap-3 mt-3">
                  <img :src="brandingAsset(form.branding.icon_192_url, '/pwa-192x192.png')" alt="" width="48" height="48" class="branding-preview__icon" />
                  <img :src="brandingAsset(form.branding.icon_512_url, '/pwa-512x512.png')" alt="" width="64" height="64" class="branding-preview__icon" />
                  <span class="small text-muted">{{ copy.brandingPreviewInstallIcon }}</span>
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
  type RecoveryEvidenceConfig,
} from "../../api/settings.api";
import { KAIRO_BRANDING_DEFAULTS, type TenantBranding } from "../../api/branding.types";
import { safeBrandingAsset } from "../../services/branding";

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
  branding: TenantBranding;
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
  branding: { ...KAIRO_BRANDING_DEFAULTS },
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
      brandingIdentity: "Identität",
      brandingDisplayName: "Anwendungsname",
      brandingShortName: "Kurzname (Symbol)",
      brandingLegalName: "Rechtlicher Name",
      brandingTagline: "Slogan",
      brandingColors: "Farben",
      brandingSecondaryColor: "Sekundärfarbe",
      brandingBackgroundColor: "Hintergrundfarbe",
      brandingThemeColor: "Themenfarbe",
      brandingLogos: "Logos und Favicon",
      brandingLogoDarkUrl: "Logo-URL (dunkel)",
      brandingFaviconUrl: "Favicon-URL",
      brandingIcons: "Installationssymbole",
      brandingIcon192: "Symbol 192×192",
      brandingIcon512: "Symbol 512×512",
      brandingMaskable: "Maskierbares Symbol",
      brandingIconsHint: "Diese Symbole erscheinen im Manifest des Mandanten und werden zum Symbol der installierten App auf Android und iOS.",
      brandingNotifications: "Benachrichtigungen und Support",
      brandingNotificationName: "Absendername der Benachrichtigungen",
      brandingSupportName: "Supportname",
      brandingSupportEmail: "Support-E-Mail",
      brandingDomain: "Eigene Domain",
      brandingCustomDomain: "Domain des Mandanten",
      brandingCustomDomainHint: "Exakter Hostname (z. B. app.verein.example). DNS und TLS werden vom Betreiber konfiguriert; die Domain wird serverseitig aufgelöst.",
      brandingPreview: "Vorschau",
      brandingPreviewInstallIcon: "Vorschau des Installationssymbols",
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
      brandingIdentity: "Identity",
      brandingDisplayName: "Application name",
      brandingShortName: "Short name (icon)",
      brandingLegalName: "Legal name",
      brandingTagline: "Tagline",
      brandingColors: "Colors",
      brandingSecondaryColor: "Secondary color",
      brandingBackgroundColor: "Background color",
      brandingThemeColor: "Theme color",
      brandingLogos: "Logos and favicon",
      brandingLogoDarkUrl: "Logo URL (dark)",
      brandingFaviconUrl: "Favicon URL",
      brandingIcons: "Install icons",
      brandingIcon192: "192×192 icon",
      brandingIcon512: "512×512 icon",
      brandingMaskable: "Maskable icon",
      brandingIconsHint: "These icons are exposed in the tenant manifest and become the installed application icon on Android and iOS.",
      brandingNotifications: "Notifications and support",
      brandingNotificationName: "Notification sender name",
      brandingSupportName: "Support name",
      brandingSupportEmail: "Support email",
      brandingDomain: "Custom domain",
      brandingCustomDomain: "Tenant domain",
      brandingCustomDomainHint: "Exact hostname (for example app.association.example). DNS and TLS stay operator-configured; the host resolves server-side.",
      brandingPreview: "Preview",
      brandingPreviewInstallIcon: "Install icon preview",
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
    brandingIdentity: "Identité",
    brandingDisplayName: "Nom de l'application",
    brandingShortName: "Nom court (icône)",
    brandingLegalName: "Nom légal",
    brandingTagline: "Slogan",
    brandingColors: "Couleurs",
    brandingSecondaryColor: "Couleur secondaire",
    brandingBackgroundColor: "Couleur de fond",
    brandingThemeColor: "Couleur de thème",
    brandingLogos: "Logos et favicon",
    brandingLogoDarkUrl: "URL du logo (sombre)",
    brandingFaviconUrl: "URL du favicon",
    brandingIcons: "Icônes d'installation",
    brandingIcon192: "Icône 192×192",
    brandingIcon512: "Icône 512×512",
    brandingMaskable: "Icône maskable",
    brandingIconsHint: "Ces icônes sont exposées dans le manifeste du tenant et deviennent l'icône de l'application installée sur Android et iOS.",
    brandingNotifications: "Notifications et support",
    brandingNotificationName: "Nom de l'expéditeur des notifications",
    brandingSupportName: "Nom du support",
    brandingSupportEmail: "E-mail du support",
    brandingDomain: "Domaine personnalisé",
    brandingCustomDomain: "Domaine du tenant",
    brandingCustomDomainHint: "Nom d'hôte exact (par exemple app.association.example). Le DNS et le TLS restent configurés par l'opérateur ; l'hôte est résolu côté serveur.",
    brandingPreview: "Aperçu",
    brandingPreviewInstallIcon: "Aperçu de l'icône d'installation",
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

function brandingAsset(value: string, fallback: string): string {
  return safeBrandingAsset(value, fallback);
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

<style scoped>
.branding-preview {
  border-radius: 0.9rem;
  border: 1px solid #e2e8f0;
}

.branding-preview__logo {
  width: 2.25rem;
  height: 2.25rem;
  object-fit: contain;
}

.branding-preview__mark {
  display: inline-flex;
  width: 2.25rem;
  height: 2.25rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.65rem;
  color: #fff;
}

.branding-preview__swatch {
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 0.45rem;
  border: 1px solid rgba(15, 33, 56, 0.12);
}

.branding-preview__icon {
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  object-fit: contain;
}
</style>
