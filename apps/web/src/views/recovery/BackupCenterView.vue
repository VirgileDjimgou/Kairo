<template>
  <main class="recovery-page p-3 p-md-4 p-xl-5">
    <section class="recovery-hero mb-4">
      <div>
        <div class="eyebrow"><i class="bi bi-shield-lock me-2"></i>{{ copy.kicker }}</div>
        <h1 class="h3 fw-bold mb-2">{{ copy.title }}</h1>
        <p class="mb-0 text-secondary">{{ copy.lead }}</p>
      </div>
      <button class="btn btn-primary px-4" type="button" :disabled="requesting" @click="createBackup">
        <span v-if="requesting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-database-add me-2"></i>{{ copy.createBackup }}
      </button>
    </section>

    <div v-if="error" class="alert alert-danger border-0 shadow-sm d-flex justify-content-between gap-3" role="alert">
      <span><i class="bi bi-exclamation-octagon me-2"></i>{{ error }}</span>
      <button class="btn-close" type="button" @click="error = ''"></button>
    </div>
    <div v-if="success" class="alert alert-success border-0 shadow-sm d-flex justify-content-between gap-3" role="status">
      <span><i class="bi bi-check-circle me-2"></i>{{ success }}</span>
      <button class="btn-close" type="button" @click="success = ''"></button>
    </div>

    <section class="row g-3 mb-4">
      <div class="col-sm-6 col-xl-3" v-for="metric in metrics" :key="metric.label">
        <article class="metric-card h-100" :class="metric.tone">
          <i :class="['bi', metric.icon]"></i>
          <div class="small text-secondary">{{ metric.label }}</div>
          <strong>{{ metric.value }}</strong>
          <span>{{ metric.hint }}</span>
        </article>
      </div>
    </section>

    <section class="row g-4">
      <div class="col-xl-7">
        <article class="card border-0 shadow-sm h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-4">
              <div>
                <div class="eyebrow">{{ copy.historyKicker }}</div>
                <h2 class="h5 fw-bold mb-1">{{ copy.historyTitle }}</h2>
                <p class="small text-secondary mb-0">{{ copy.historyLead }}</p>
              </div>
              <button class="btn btn-outline-secondary btn-sm" type="button" :disabled="loading" @click="load"><i class="bi bi-arrow-clockwise me-1"></i>{{ copy.refresh }}</button>
            </div>
            <div v-if="loading" class="py-5 text-center text-muted"><span class="spinner-border spinner-border-sm me-2"></span>{{ copy.loading }}</div>
            <div v-else-if="!overview?.runs.length" class="empty-state text-center py-5"><i class="bi bi-safe2 fs-2 d-block mb-2"></i>{{ copy.noBackups }}</div>
            <div v-else class="vstack gap-2">
              <article v-for="run in overview.runs" :key="run.id" class="backup-row">
                <div class="backup-icon"><i class="bi bi-file-earmark-lock2"></i></div>
                <div class="flex-grow-1 min-w-0">
                  <div class="fw-semibold text-capitalize">{{ humanTrigger(run.trigger) }}</div>
                  <div class="small text-secondary text-truncate">{{ formatDate(run.completed_at || run.requested_at) }} · {{ formatSize(run.archive_size_bytes) }}</div>
                  <div v-if="run.archive_sha256" class="checksum">SHA-256 {{ run.archive_sha256.slice(0, 16) }}…</div>
                </div>
                <span class="badge" :class="statusClass(run.status)">{{ humanStatus(run.status) }}</span>
              </article>
            </div>
          </div>
        </article>
      </div>

      <div class="col-xl-5">
        <article class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="eyebrow">{{ copy.importKicker }}</div>
            <h2 class="h5 fw-bold mb-2">{{ copy.importTitle }}</h2>
            <p class="small text-secondary">{{ copy.importLead }}</p>
            <label class="form-label small fw-semibold" for="backup-archive">{{ copy.archive }}</label>
            <input id="backup-archive" class="form-control mb-3" type="file" accept=".enc" @change="archiveFile = pickFile($event)" />
            <label class="form-label small fw-semibold" for="backup-manifest">{{ copy.manifest }}</label>
            <input id="backup-manifest" class="form-control mb-3" type="file" accept=".json" @change="manifestFile = pickFile($event)" />
            <button class="btn btn-outline-primary w-100" type="button" :disabled="importing || !archiveFile || !manifestFile" @click="stageImport">
              <span v-if="importing" class="spinner-border spinner-border-sm me-2"></span><i v-else class="bi bi-file-earmark-arrow-up me-2"></i>{{ copy.verifyImport }}
            </button>
          </div>
        </article>
        <article class="restore-notice card border-0 shadow-sm">
          <div class="card-body p-4">
            <i class="bi bi-exclamation-diamond-fill"></i>
            <h2 class="h6 fw-bold mt-3">{{ copy.restoreTitle }}</h2>
            <p class="small mb-0">{{ copy.restoreLead }}</p>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getBackupOverview, importBackup, requestBackup, type BackupOverviewResponse } from '@/api/backup.api'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const overview = ref<BackupOverviewResponse | null>(null)
const loading = ref(true)
const requesting = ref(false)
const importing = ref(false)
const error = ref('')
const success = ref('')
const archiveFile = ref<File | null>(null)
const manifestFile = ref<File | null>(null)

const copy = computed(() => ({
  fr: { kicker: 'continuité de l’association', title: 'Centre de sauvegarde et récupération', lead: 'Archives chiffrées, vérifiées et protégées. Les données ne sont jamais téléchargées dans le navigateur.', createBackup: 'Créer une sauvegarde', historyKicker: 'archives protégées', historyTitle: 'Historique de récupération', historyLead: 'Chaque archive possède un manifeste signé et une empreinte SHA-256.', refresh: 'Actualiser', loading: 'Chargement des sauvegardes…', noBackups: 'Aucune sauvegarde disponible pour le moment.', importKicker: 'restauration contrôlée', importTitle: 'Vérifier une archive importée', importLead: 'Importez l’archive chiffrée et son manifeste. La restauration reste une opération de maintenance confirmée.', archive: 'Archive chiffrée (.enc)', manifest: 'Manifeste signé (.json)', verifyImport: 'Vérifier et préparer', restoreTitle: 'Restauration protégée', restoreLead: 'Une archive validée est seulement préparée ici. Le remplacement réel des données exige une confirmation sur le serveur afin d’éviter toute perte accidentelle.', automatic: 'Sauvegarde quotidienne', retention: 'Conservation', external: 'Copie externe', pitr: 'Retour dans le temps', configured: 'configurée', missing: 'à configurer', enabled: 'activé', disabled: 'désactivé', requested: 'La sauvegarde a été demandée ; actualisez dans quelques instants pour voir son contrôle d’intégrité.', imported: 'Archive vérifiée et préparée pour une restauration sécurisée.' },
  en: { kicker: 'association continuity', title: 'Backup and recovery center', lead: 'Encrypted, verified and protected archives. Data is never downloaded to the browser.', createBackup: 'Create backup', historyKicker: 'protected archives', historyTitle: 'Recovery history', historyLead: 'Every archive has a signed manifest and SHA-256 fingerprint.', refresh: 'Refresh', loading: 'Loading backups…', noBackups: 'No backup is available yet.', importKicker: 'controlled restoration', importTitle: 'Verify an imported archive', importLead: 'Upload the encrypted archive and its manifest. Restoration remains a confirmed maintenance operation.', archive: 'Encrypted archive (.enc)', manifest: 'Signed manifest (.json)', verifyImport: 'Verify and stage', restoreTitle: 'Protected restoration', restoreLead: 'A validated archive is only staged here. Actual replacement of data requires a server-side confirmation to prevent accidental loss.', automatic: 'Daily backup', retention: 'Retention', external: 'External copy', pitr: 'Point in time', configured: 'configured', missing: 'to configure', enabled: 'enabled', disabled: 'disabled', requested: 'Backup requested; refresh shortly to see its integrity check.', imported: 'Archive verified and staged for secure recovery.' },
  de: { kicker: 'vereinskontinuität', title: 'Sicherungs- und Wiederherstellungszentrum', lead: 'Verschlüsselte, geprüfte und geschützte Archive. Daten werden nie in den Browser heruntergeladen.', createBackup: 'Sicherung erstellen', historyKicker: 'geschützte Archive', historyTitle: 'Wiederherstellungsverlauf', historyLead: 'Jedes Archiv besitzt ein signiertes Manifest und einen SHA-256-Fingerabdruck.', refresh: 'Aktualisieren', loading: 'Sicherungen werden geladen…', noBackups: 'Noch keine Sicherung verfügbar.', importKicker: 'kontrollierte Wiederherstellung', importTitle: 'Importiertes Archiv prüfen', importLead: 'Laden Sie das verschlüsselte Archiv und sein Manifest hoch. Die Wiederherstellung bleibt eine bestätigte Wartungsaktion.', archive: 'Verschlüsseltes Archiv (.enc)', manifest: 'Signiertes Manifest (.json)', verifyImport: 'Prüfen und vorbereiten', restoreTitle: 'Geschützte Wiederherstellung', restoreLead: 'Ein geprüftes Archiv wird hier nur vorbereitet. Der echte Datenersatz verlangt eine Bestätigung auf dem Server.', automatic: 'Tägliche Sicherung', retention: 'Aufbewahrung', external: 'Externe Kopie', pitr: 'Zeitpunktwiederherstellung', configured: 'konfiguriert', missing: 'zu konfigurieren', enabled: 'aktiviert', disabled: 'deaktiviert', requested: 'Sicherung angefordert; bitte in Kürze aktualisieren, um die Integritätsprüfung zu sehen.', imported: 'Archiv geprüft und für sichere Wiederherstellung vorbereitet.' },
}[localeStore.currentLocale]))

const metrics = computed(() => [
  { label: copy.value.automatic, value: overview.value?.automatic_enabled ? copy.value.enabled : copy.value.disabled, hint: overview.value?.last_successful_backup_at ? formatDate(overview.value.last_successful_backup_at) : '—', icon: 'bi-clock-history', tone: 'blue' },
  { label: copy.value.retention, value: `${overview.value?.retention_days ?? '—'} ${localeStore.currentLocale === 'de' ? 'Tage' : localeStore.currentLocale === 'en' ? 'days' : 'jours'}`, hint: copy.value.historyLead, icon: 'bi-calendar-range', tone: 'gold' },
  { label: copy.value.external, value: overview.value?.external_storage_configured ? copy.value.configured : copy.value.missing, hint: copy.value.lead, icon: 'bi-cloud-check', tone: 'green' },
  { label: copy.value.pitr, value: overview.value?.point_in_time_recovery_enabled ? copy.value.enabled : copy.value.disabled, hint: 'PostgreSQL WAL', icon: 'bi-arrow-counterclockwise', tone: 'purple' },
])

async function load() { loading.value = true; error.value = ''; try { overview.value = await getBackupOverview() } catch (caught) { error.value = message(caught) } finally { loading.value = false } }
async function createBackup() { requesting.value = true; error.value = ''; try { await requestBackup(); success.value = copy.value.requested; await load() } catch (caught) { error.value = message(caught) } finally { requesting.value = false } }
async function stageImport() { if (!archiveFile.value || !manifestFile.value) return; importing.value = true; error.value = ''; try { await importBackup(archiveFile.value, manifestFile.value); success.value = copy.value.imported; archiveFile.value = null; manifestFile.value = null; await load() } catch (caught) { error.value = message(caught) } finally { importing.value = false } }
function pickFile(event: Event) { return (event.target as HTMLInputElement).files?.[0] || null }
function message(caught: unknown) { return (caught as { response?: { data?: { detail?: string } } }).response?.data?.detail || (caught instanceof Error ? caught.message : 'Operation failed') }
function formatDate(value: string | null) { return value ? new Intl.DateTimeFormat(localeStore.currentLocale, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : '—' }
function formatSize(value: number | null) { return value ? new Intl.NumberFormat(localeStore.currentLocale, { style: 'unit', unit: 'megabyte', maximumFractionDigits: 1 }).format(value / 1024 / 1024) : '—' }
function humanTrigger(value: string) { return value.replace('_', ' ') }
function humanStatus(value: string) { return value.replaceAll('_', ' ') }
function statusClass(value: string) { return value === 'available' || value === 'restore_drill_passed' ? 'text-bg-success' : value === 'failed' ? 'text-bg-danger' : value === 'staged' ? 'text-bg-primary' : 'text-bg-warning' }
onMounted(load)
</script>

<style scoped>
.recovery-page { max-width: 1440px; margin: 0 auto; }
.recovery-hero { background: linear-gradient(120deg, #102a52, #1d5aa6); color: white; border-radius: 1.25rem; padding: clamp(1.35rem, 3vw, 2.5rem); display: flex; align-items: center; justify-content: space-between; gap: 1.25rem; box-shadow: 0 16px 40px rgba(16,42,82,.18); }
.recovery-hero .text-secondary { color: rgba(255,255,255,.78) !important; max-width: 700px; }
.eyebrow { font-size: .74rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #61738b; margin-bottom: .4rem; }.recovery-hero .eyebrow { color: #bed8ff; }
.metric-card { border: 1px solid #e2e9f1; border-radius: 1rem; padding: 1.15rem; background: #fff; display:grid; gap:.26rem; box-shadow: 0 8px 24px rgba(23,51,84,.05); }.metric-card i { font-size:1.2rem; }.metric-card strong { font-size: 1.15rem; color:#102a52; }.metric-card span { font-size:.76rem; color:#718096; }.metric-card.blue i{color:#1769c2}.metric-card.gold i{color:#b7791f}.metric-card.green i{color:#14845d}.metric-card.purple i{color:#7655b8}
.backup-row { display:flex; align-items:center; gap:.8rem; padding:.85rem; border:1px solid #e5eaf0; border-radius:.85rem; }.backup-icon { width:2.45rem;height:2.45rem;border-radius:.7rem;display:grid;place-items:center;background:#e9f2ff;color:#1d5aa6; }.checksum { font-family: ui-monospace, monospace; font-size:.68rem; color:#708198; margin-top:.2rem; }.min-w-0 { min-width:0; }.restore-notice { background:#fff7e3; color:#6b4c09; }.restore-notice i { font-size:1.6rem; color:#d29116; }
@media (max-width: 575.98px) { .recovery-hero { align-items:stretch; flex-direction:column; }.recovery-hero .btn { width:100%; }.backup-row { align-items:flex-start; flex-wrap:wrap; }.backup-row .badge { margin-left:auto; } }
</style>
