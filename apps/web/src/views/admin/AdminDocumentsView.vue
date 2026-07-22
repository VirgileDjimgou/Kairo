<template>
  <div class="p-4 p-lg-5">
    <div
      class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4"
    >
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ workspaceLabel }}
        </div>
        <h1 class="h4 fw-bold mb-1">{{ workspaceTitle }}</h1>
        <p class="text-muted mb-0">
          {{ workspaceDescription }}
        </p>
      </div>
      <button
        class="btn om-primary-btn align-self-start"
        type="button"
        @click="refreshDocuments"
        :disabled="loading || isRecovering"
      >
        {{ loading ? copy.refreshing : copy.refreshList }}
      </button>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
        <div>
          <div class="fw-semibold">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ workspaceErrorTitle }}
          </div>
          <p class="small mb-0 mt-2">{{ error }}</p>
          <p class="mb-0 small text-muted mt-1">{{ t('common.recoveryHint') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm align-self-start" type="button" @click="retryRefreshDocuments" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ isRecovering ? t('common.loading') : t('common.retry') }}
        </button>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-5">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3">{{ copy.uploadDocumentTitle }}</h2>

            <form class="vstack gap-3" @submit.prevent="submitUpload">
              <div>
                <label class="form-label">{{ copy.titleLabel }}</label>
                <input
                  v-model.trim="title"
                  class="form-control"
                  type="text"
                  :placeholder="copy.titlePlaceholder"
                  required
                />
              </div>

              <div>
                <label class="form-label">{{ copy.descriptionLabel }}</label>
                <textarea
                  v-model.trim="description"
                  class="form-control"
                  rows="3"
                  :placeholder="copy.descriptionPlaceholder"
                />
              </div>

              <div>
                <label class="form-label">{{ copy.fileLabel }}</label>
                <input
                  class="form-control"
                  type="file"
                  accept=".pdf,.docx,.txt,.md,.csv,.png,.jpg,.jpeg,.webp"
                  @change="handleFileChange"
                  required
                />
                <div class="form-text">
                  {{ copy.allowedFileTypes }}
                </div>
              </div>

              <div>
                <label class="form-label">{{ copy.accessScopeLabel }}</label>
                <select v-model="accessScope" class="form-select">
                  <option value="tenant_public">{{ copy.accessTenantPublic }}</option>
                  <option value="members_only">{{ copy.accessMembersOnly }}</option>
                  <option value="role_restricted">{{ copy.accessRoleRestricted }}</option>
                  <option value="user_private">{{ copy.accessUserPrivate }}</option>
                  <option value="admin_only">{{ copy.accessAdminOnly }}</option>
                </select>
              </div>

              <div class="d-flex gap-2">
                <button
                  class="btn om-primary-btn"
                  type="submit"
                  :disabled="uploading || !selectedFile"
                >
                  {{ uploading ? copy.uploading : copy.uploadDocument }}
                </button>
                <button
                  class="btn btn-outline-secondary"
                  type="button"
                  @click="resetForm"
                >
                  {{ copy.reset }}
                </button>
              </div>

              <div v-if="statusMessage" class="alert alert-info mb-0">
                {{ statusMessage }}
              </div>
            </form>

            <hr class="my-4" />

            <h2 class="h6 fw-bold mb-3">{{ copy.bulkUploadTitle }}</h2>
            <form class="vstack gap-3" @submit.prevent="submitBulkUpload">
              <div>
                <label class="form-label">{{ copy.filesLabel }}</label>
                <input
                  class="form-control"
                  type="file"
                  accept=".pdf,.docx,.txt,.md,.csv,.png,.jpg,.jpeg,.webp"
                  multiple
                  @change="handleBulkFileChange"
                />
              </div>
              <div>
                <label class="form-label">{{ copy.titlePrefixLabel }}</label>
                <input
                  v-model.trim="bulkTitlePrefix"
                  class="form-control"
                  type="text"
                  :placeholder="copy.titlePrefixPlaceholder"
                />
              </div>
              <div class="d-flex gap-2">
                <button
                  class="btn btn-outline-primary"
                  type="submit"
                  :disabled="bulkUploading || bulkFiles.length === 0"
                >
                  {{ bulkUploading ? copy.uploading : copy.bulkUpload }}
                </button>
                <button
                  class="btn btn-outline-secondary"
                  type="button"
                  @click="clearBulkSelection"
                >
                  {{ copy.clear }}
                </button>
              </div>
              <div v-if="bulkStatusMessage" class="alert alert-info mb-0">
                {{ bulkStatusMessage }}
              </div>
            </form>
            <div v-if="bulkResults.length > 0" class="mt-3">
              <div class="small text-uppercase text-muted fw-semibold mb-2">
                {{ copy.bulkResult }}
              </div>
              <div class="vstack gap-2">
                <div
                  v-for="item in bulkResults"
                  :key="`${item.index}-${item.file_name}`"
                  class="border rounded-3 p-3"
                >
                  <div class="d-flex justify-content-between gap-2 flex-wrap">
                    <div class="fw-semibold">{{ item.file_name }}</div>
                    <span
                      :class="item.status === 'uploaded' ? 'badge text-bg-success-subtle text-success border border-success-subtle' : 'badge text-bg-danger-subtle text-danger border border-danger-subtle'"
                    >
                      {{ item.status }}
                    </span>
                  </div>
                  <div v-if="item.error" class="small text-danger mt-2">
                    {{ item.error }}
                  </div>
                  <div v-else-if="item.document" class="small text-muted mt-2">
                    {{ copy.documentQueuedAs.replace("{title}", item.document.title).replace("{jobId}", String(item.document.ingestion_job_id)) }}
                    <span v-if="item.document.duplicate_of_document_id">
                      · {{ copy.duplicateOf.replace("{documentId}", String(item.document.duplicate_of_document_id)) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">{{ copy.latestDocuments }}</h2>
              <span class="badge bg-light text-dark"
                >{{ documents.length }} {{ copy.items }}</span
              >
            </div>

            <div v-if="loading" class="text-muted py-5 text-center">
              {{ copy.loadingDocuments }}
            </div>

            <div v-else-if="documents.length === 0" class="empty-state">
              <i class="bi bi-file-earmark-text display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">{{ copy.noDocumentsYet }}</p>
              <p class="text-muted mb-3">
                {{ copy.noDocumentsHint }}
              </p>
              <div class="d-flex flex-wrap justify-content-center gap-2">
                <RouterLink :to="emptyStatePrimaryLink.to" class="btn btn-outline-secondary btn-sm">
                  {{ emptyStatePrimaryLink.label }}
                </RouterLink>
                <RouterLink :to="emptyStateSecondaryLink.to" class="btn btn-outline-secondary btn-sm">
                  {{ emptyStateSecondaryLink.label }}
                </RouterLink>
              </div>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>{{ copy.titleLabel }}</th>
                    <th>{{ copy.statusLabel }}</th>
                    <th>{{ copy.accessLabel }}</th>
                    <th>{{ copy.ingestionLabel }}</th>
                    <th>{{ copy.fileLabel }}</th>
                    <th>{{ copy.sizeLabel }}</th>
                    <th>{{ copy.actionsLabel }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="document in documents" :key="document.id">
                    <td>
                      <div class="fw-semibold">{{ document.title }}</div>
                      <div class="small text-muted">
                        {{ document.description || copy.noDescription }}
                      </div>
                    </td>
                    <td>
                      <span
                        class="badge text-bg-success-subtle text-success border border-success-subtle"
                      >
                        {{ formatStatusToken(document.status) }}
                      </span>
                    </td>
                    <td>
                      <div class="vstack gap-2">
                        <select
                          v-model="draftAccessScopeByDocument[document.id]"
                          class="form-select form-select-sm"
                        >
                          <option value="tenant_public">{{ copy.accessTenantPublic }}</option>
                          <option value="members_only">{{ copy.accessMembersOnly }}</option>
                          <option value="role_restricted">
                            {{ copy.accessRoleRestricted }}
                          </option>
                          <option value="user_private">{{ copy.accessUserPrivate }}</option>
                          <option value="admin_only">{{ copy.accessAdminOnly }}</option>
                        </select>
                        <input
                          v-model="draftAllowedRolesByDocument[document.id]"
                          class="form-control form-control-sm"
                          type="text"
                          :placeholder="copy.allowedRolesPlaceholder"
                          :disabled="
                            draftAccessScopeByDocument[document.id] !==
                            'role_restricted'
                          "
                        />
                        <div class="small text-muted">
                          {{
                            formatAllowedRoles(
                              document.allowed_role_ids,
                              document.id
                            )
                          }}
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="badge text-bg-light text-dark border">
                        {{ formatIngestionStatus(document.id) }}
                      </span>
                    </td>
                    <td>
                      <div class="fw-semibold">
                        {{ document.current_version?.file_name || copy.notAvailable }}
                      </div>
                      <div class="small text-muted">
                        {{
                          document.current_version?.mime_type || copy.unknownType
                        }}
                      </div>
                    </td>
                    <td>
                      {{
                        formatBytes(
                          document.current_version?.file_size_bytes ?? 0
                        )
                      }}
                    </td>
                    <td>
                      <div class="d-flex flex-column gap-2">
                        <button
                          class="btn btn-sm btn-outline-primary"
                          type="button"
                          @click="saveAccess(document.id)"
                          :disabled="busyDocumentId === document.id"
                        >
                          {{ copy.saveAccess }}
                        </button>
                        <button
                          class="btn btn-sm btn-outline-secondary"
                          type="button"
                          @click="queueReindex(document.id)"
                          :disabled="busyDocumentId === document.id || document.status === 'archived'"
                        >
                          {{ copy.reindex }}
                        </button>
                        <button
                          v-if="document.status !== 'archived'"
                          class="btn btn-sm btn-outline-warning"
                          type="button"
                          @click="archive(document.id)"
                          :disabled="busyDocumentId === document.id"
                        >
                          {{ copy.archive }}
                        </button>
                        <button
                          v-else
                          class="btn btn-sm btn-outline-success"
                          type="button"
                          @click="unarchive(document.id)"
                          :disabled="busyDocumentId === document.id"
                        >
                          {{ copy.restore }}
                        </button>
                        <button
                          v-if="formatIngestionStatus(document.id) === 'failed'"
                          class="btn btn-sm btn-outline-danger"
                          type="button"
                          @click="retryJob(document.id)"
                          :disabled="busyDocumentId === document.id"
                        >
                          {{ copy.retryJob }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  archiveDocument,
  bulkUploadDocuments,
  getIngestionJob,
  listDocuments,
  reindexDocument,
  retryIngestionJob,
  unarchiveDocument,
  updateDocumentAccess,
  uploadDocument,
  type DocumentListItemResponse,
  type UploadDocumentResponse,
} from "../../api/documents.api";
import { useRecoveryState } from "@/composables/useRecoveryState";
import { useLocaleStore } from "@/stores/locale.store";

const route = useRoute();
const localeStore = useLocaleStore();
const t = (key: string) => localeStore.t(key);
const isSecretaryWorkspace = computed(() => route.path.startsWith("/secretary"));
const copy = computed(() => {
  if (localeStore.currentLocale === "de") {
    return {
      secretaryDocuments: "Sekretariatsdokumente",
      documents: "Dokumente",
      officialDocumentGovernance: "Offizielle Dokumentenverwaltung",
      documentIntake: "Dokumentenaufnahme",
      secretaryWorkspaceDescription: "Laden Sie Statuten, Protokolle, Mitteilungen und andere offizielle Vereinsdokumente hoch und verwalten Sie sie.",
      adminWorkspaceDescription: "Laden Sie Tenant-Dokumente in den Speicher und pruefen Sie die neuesten Versionsmetadaten.",
      documentsWorkspaceErrorTitle: "Dokumentenbereich nicht verfügbar",
      secretaryWorkspaceErrorTitle: "Dokumentenbereich des Sekretariats nicht verfügbar",
      reviewPolicies: "Regelwerke prüfen",
      reviewSettings: "Einstellungen prüfen",
      prepareAnnouncements: "Ankündigungen vorbereiten",
      addMembersFirst: "Zuerst Mitglieder anlegen",
      refreshing: "Aktualisierung...",
      refreshList: "Liste aktualisieren",
      uploadDocumentTitle: "Dokument hochladen",
      titleLabel: "Titel",
      titlePlaceholder: "Mandantenrichtlinie",
      descriptionLabel: "Beschreibung",
      descriptionPlaceholder: "Optionaler Kontext für Prüfer",
      fileLabel: "Datei",
      allowedFileTypes: "Erlaubt: PDF, DOCX, TXT, MD, CSV, PNG, JPG, JPEG, WEBP.",
      accessScopeLabel: "Zugriffsbereich",
      accessTenantPublic: "Tenant-weit sichtbar",
      accessMembersOnly: "Nur Mitglieder",
      accessRoleRestricted: "Auf Rollen beschränkt",
      accessUserPrivate: "Benutzerprivat",
      accessAdminOnly: "Nur Admin",
      uploading: "Hochladen...",
      uploadDocument: "Dokument hochladen",
      reset: "Zurücksetzen",
      bulkUploadTitle: "Mehrfach-Upload",
      filesLabel: "Dateien",
      titlePrefixLabel: "Titelpräfix",
      titlePrefixPlaceholder: "Migration",
      bulkUpload: "Mehrfach hochladen",
      clear: "Leeren",
      bulkResult: "Mehrfachergebnis",
      documentQueuedAs: "Dokument {title} wurde als {jobId} eingereiht",
      duplicateOf: "Duplikat von {documentId}",
      latestDocuments: "Neueste Dokumente",
      items: "Einträge",
      loadingDocuments: "Dokumente werden geladen...",
      noDocumentsYet: "Noch keine Dokumente",
      noDocumentsHint: "Beginnen Sie mit einem Begrüßungsleitfaden, einer Richtlinie oder einem Betriebsdokument. Sobald die erste Datei hochgeladen ist, wirkt der Tenant realer.",
      statusLabel: "Status",
      accessLabel: "Zugriff",
      ingestionLabel: "Ingestion",
      sizeLabel: "Größe",
      actionsLabel: "Aktionen",
      noDescription: "Keine Beschreibung",
      allowedRolesPlaceholder: "principal_admin, member",
      notAvailable: "Nicht verfügbar",
      unknownType: "unbekannter Typ",
      saveAccess: "Zugriff speichern",
      reindex: "Neu indexieren",
      archive: "Archivieren",
      restore: "Wiederherstellen",
      retryJob: "Job erneut starten",
      draftRoles: "Entwurfsrollen: {roles}",
      noRolesSelectedYet: "Noch keine Rollen ausgewählt",
      noRoleRestriction: "Keine Rollenbeschränkung",
      allowedRoles: "Erlaubte Rollen: {roles}",
      statusUnknown: "unbekannt",
      statusPending: "ausstehend",
      statusProcessing: "in Bearbeitung",
      statusCompleted: "abgeschlossen",
      statusUploaded: "hochgeladen",
      statusReady: "bereit",
      statusArchived: "archiviert",
      statusFailedLong: "fehlgeschlagen",
      indexedSuffix: "indiziert",
      accessUpdated: "Zugriff für {title} aktualisiert.",
      reindexQueued: "Neuindexierung für Dokument {documentId} eingereiht.",
      archivedMessage: "{title} archiviert.",
      restoredMessage: "{title} wiederhergestellt.",
      noJobFound: "Kein Job für dieses Dokument gefunden.",
      retriedJob: "Ingestion-Job {jobId} erneut gestartet.",
      chooseFileBeforeUpload: "Wählen Sie vor dem Hochladen eine Datei aus.",
      uploadQueued: "Dokument hochgeladen. Ingestion-Job {jobId} eingereiht.",
      uploadFailed: "Upload fehlgeschlagen. Prüfen Sie Dateityp und Größe.",
      selectAtLeastOneFile: "Wählen Sie mindestens eine Datei aus.",
      bulkSummary: "{success} hochgeladen, {failure} fehlgeschlagen.",
    };
  }
  if (localeStore.currentLocale === "en") {
    return {
      secretaryDocuments: "Secretary documents",
      documents: "Documents",
      officialDocumentGovernance: "Official document governance",
      documentIntake: "Document intake",
      secretaryWorkspaceDescription: "Upload and govern statutes, protocols, notices, and other official organization records.",
      adminWorkspaceDescription: "Upload tenant documents into object storage and review the latest version metadata.",
      documentsWorkspaceErrorTitle: "Document workspace unavailable",
      secretaryWorkspaceErrorTitle: "Secretary document workspace unavailable",
      reviewPolicies: "Review policies",
      reviewSettings: "Review settings",
      prepareAnnouncements: "Prepare announcements",
      addMembersFirst: "Add members first",
      refreshing: "Refreshing...",
      refreshList: "Refresh list",
      uploadDocumentTitle: "Upload a document",
      titleLabel: "Title",
      titlePlaceholder: "Tenant policy",
      descriptionLabel: "Description",
      descriptionPlaceholder: "Optional context for reviewers",
      fileLabel: "File",
      allowedFileTypes: "Allowed: PDF, DOCX, TXT, MD, CSV, PNG, JPG, JPEG, WEBP.",
      accessScopeLabel: "Access scope",
      accessTenantPublic: "Tenant public",
      accessMembersOnly: "Members only",
      accessRoleRestricted: "Role restricted",
      accessUserPrivate: "User private",
      accessAdminOnly: "Admin only",
      uploading: "Uploading...",
      uploadDocument: "Upload document",
      reset: "Reset",
      bulkUploadTitle: "Bulk upload",
      filesLabel: "Files",
      titlePrefixLabel: "Title prefix",
      titlePrefixPlaceholder: "Migration",
      bulkUpload: "Bulk upload",
      clear: "Clear",
      bulkResult: "Bulk result",
      documentQueuedAs: "Document {title} queued as {jobId}",
      duplicateOf: "duplicate of {documentId}",
      latestDocuments: "Latest documents",
      items: "items",
      loadingDocuments: "Loading documents...",
      noDocumentsYet: "No documents yet",
      noDocumentsHint: "Start with a welcome guide, policy, or operating document. Once the first file is uploaded, the tenant begins to feel real.",
      statusLabel: "Status",
      accessLabel: "Access",
      ingestionLabel: "Ingestion",
      sizeLabel: "Size",
      actionsLabel: "Actions",
      noDescription: "No description",
      allowedRolesPlaceholder: "principal_admin, member",
      notAvailable: "N/A",
      unknownType: "unknown type",
      saveAccess: "Save access",
      reindex: "Reindex",
      archive: "Archive",
      restore: "Restore",
      retryJob: "Retry job",
      draftRoles: "Draft roles: {roles}",
      noRolesSelectedYet: "No roles selected yet",
      noRoleRestriction: "No role restriction",
      allowedRoles: "Allowed roles: {roles}",
      statusUnknown: "unknown",
      statusPending: "pending",
      statusProcessing: "processing",
      statusCompleted: "completed",
      statusUploaded: "uploaded",
      statusReady: "ready",
      statusArchived: "archived",
      statusFailedLong: "failed",
      indexedSuffix: "indexed",
      accessUpdated: "Updated access for {title}.",
      reindexQueued: "Reindex queued for document {documentId}.",
      archivedMessage: "Archived {title}.",
      restoredMessage: "Restored {title}.",
      noJobFound: "No job found for this document.",
      retriedJob: "Retried ingestion job {jobId}.",
      chooseFileBeforeUpload: "Choose a file before uploading.",
      uploadQueued: "Document uploaded. Ingestion job {jobId} queued.",
      uploadFailed: "Upload failed. Check the file type and size.",
      selectAtLeastOneFile: "Select at least one file.",
      bulkSummary: "{success} uploaded, {failure} failed.",
    };
  }
  return {
    secretaryDocuments: "Documents du secrétariat",
    documents: "Documents",
    officialDocumentGovernance: "Gouvernance documentaire officielle",
    documentIntake: "Réception documentaire",
    secretaryWorkspaceDescription: "Importez et gouvernez les statuts, procès-verbaux, annonces et autres documents officiels de l'association.",
    adminWorkspaceDescription: "Importez les documents du tenant dans le stockage et consultez les métadonnées de la dernière version.",
    documentsWorkspaceErrorTitle: "L'espace documentaire est indisponible",
    secretaryWorkspaceErrorTitle: "L'espace documentaire du secrétariat est indisponible",
    reviewPolicies: "Consulter les règlements",
    reviewSettings: "Consulter les réglages",
    prepareAnnouncements: "Préparer les annonces",
    addMembersFirst: "Ajouter d'abord les membres",
    refreshing: "Actualisation...",
    refreshList: "Actualiser la liste",
    uploadDocumentTitle: "Importer un document",
    titleLabel: "Titre",
    titlePlaceholder: "Règlement du tenant",
    descriptionLabel: "Description",
    descriptionPlaceholder: "Contexte optionnel pour les relecteurs",
    fileLabel: "Fichier",
    allowedFileTypes: "Autorisés : PDF, DOCX, TXT, MD, CSV, PNG, JPG, JPEG, WEBP.",
    accessScopeLabel: "Portée d'accès",
    accessTenantPublic: "Public au tenant",
    accessMembersOnly: "Membres uniquement",
    accessRoleRestricted: "Restreint à certains rôles",
    accessUserPrivate: "Privé à l'utilisateur",
    accessAdminOnly: "Admin uniquement",
    uploading: "Import en cours...",
    uploadDocument: "Importer le document",
    reset: "Réinitialiser",
    bulkUploadTitle: "Import multiple",
    filesLabel: "Fichiers",
    titlePrefixLabel: "Préfixe du titre",
    titlePrefixPlaceholder: "Migration",
    bulkUpload: "Importer en lot",
    clear: "Effacer",
    bulkResult: "Résultat du lot",
    documentQueuedAs: "Le document {title} a été mis en file sous {jobId}",
    duplicateOf: "doublon de {documentId}",
    latestDocuments: "Derniers documents",
    items: "éléments",
    loadingDocuments: "Chargement des documents...",
    noDocumentsYet: "Aucun document pour le moment",
    noDocumentsHint: "Commencez par un guide d'accueil, un règlement ou un document d'exploitation. Dès que le premier fichier est importé, le tenant devient plus concret.",
    statusLabel: "Statut",
    accessLabel: "Accès",
    ingestionLabel: "Ingestion",
    sizeLabel: "Taille",
    actionsLabel: "Actions",
    noDescription: "Aucune description",
    allowedRolesPlaceholder: "principal_admin, member",
    notAvailable: "N/D",
    unknownType: "type inconnu",
    saveAccess: "Enregistrer l'accès",
    reindex: "Réindexer",
    archive: "Archiver",
    restore: "Restaurer",
    retryJob: "Relancer le job",
    draftRoles: "Rôles en brouillon : {roles}",
    noRolesSelectedYet: "Aucun rôle sélectionné pour le moment",
    noRoleRestriction: "Aucune restriction de rôle",
    allowedRoles: "Rôles autorisés : {roles}",
    statusUnknown: "inconnu",
    statusPending: "en attente",
    statusProcessing: "en traitement",
    statusCompleted: "terminé",
    statusUploaded: "importé",
    statusReady: "prêt",
    statusArchived: "archivé",
    statusFailedLong: "échoué",
    indexedSuffix: "indexés",
    accessUpdated: "Accès mis à jour pour {title}.",
    reindexQueued: "Réindexation mise en file pour le document {documentId}.",
    archivedMessage: "{title} a été archivé.",
    restoredMessage: "{title} a été restauré.",
    noJobFound: "Aucun job trouvé pour ce document.",
    retriedJob: "Job d'ingestion {jobId} relancé.",
    chooseFileBeforeUpload: "Choisissez un fichier avant l'import.",
    uploadQueued: "Document importé. Job d'ingestion {jobId} mis en file.",
    uploadFailed: "Échec de l'import. Vérifiez le type et la taille du fichier.",
    selectAtLeastOneFile: "Sélectionnez au moins un fichier.",
    bulkSummary: "{success} importés, {failure} en échec.",
  };
});
const workspaceLabel = computed(() =>
  isSecretaryWorkspace.value ? copy.value.secretaryDocuments : copy.value.documents
);
const workspaceTitle = computed(() =>
  isSecretaryWorkspace.value ? copy.value.officialDocumentGovernance : copy.value.documentIntake
);
const workspaceDescription = computed(() =>
  isSecretaryWorkspace.value
    ? copy.value.secretaryWorkspaceDescription
    : copy.value.adminWorkspaceDescription
);
const emptyStatePrimaryLink = computed(() =>
  isSecretaryWorkspace.value
    ? { to: "/secretary/policies", label: copy.value.reviewPolicies }
    : { to: "/admin/settings", label: copy.value.reviewSettings }
);
const emptyStateSecondaryLink = computed(() =>
  isSecretaryWorkspace.value
    ? { to: "/secretary/announcements", label: copy.value.prepareAnnouncements }
    : { to: "/admin/members", label: copy.value.addMembersFirst }
);
const workspaceErrorTitle = computed(() =>
  isSecretaryWorkspace.value
    ? copy.value.secretaryWorkspaceErrorTitle
    : copy.value.documentsWorkspaceErrorTitle
);

const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState();
const documents = ref<DocumentListItemResponse[]>([]);
const uploading = ref(false);
const title = ref("");
const description = ref("");
const accessScope = ref("tenant_public");
const selectedFile = ref<File | null>(null);
const statusMessage = ref("");
const bulkStatusMessage = ref("");
const busyDocumentId = ref<string | null>(null);
const bulkUploading = ref(false);
const bulkTitlePrefix = ref("");
const bulkFiles = ref<File[]>([]);
const bulkResults = ref<
  { index: number; file_name: string; status: string; document: UploadDocumentResponse | null; error: string | null }[]
>([]);
const ingestionStatusByDocument = ref<Record<string, string>>({});
const ingestionJobByDocument = ref<Record<string, string>>({});
const draftAccessScopeByDocument = ref<Record<string, string>>({});
const draftAllowedRolesByDocument = ref<Record<string, string>>({});

function formatIngestionStatus(documentId: string): string {
  const status = ingestionStatusByDocument.value[documentId];
  const detail = ingestionDetailByDocument.value[documentId];
  if (!status) {
    return copy.value.statusUnknown;
  }
  if (detail && status === "completed") {
    return `${copy.value.statusCompleted} (${detail.indexed}/${detail.chunks} ${copy.value.indexedSuffix})`;
  }
  return formatStatusToken(status);
}

const ingestionDetailByDocument = ref<
  Record<string, { chunks: number; indexed: number }>
>({});

async function refreshDocuments() {
  clearError();
  await run(async () => {
    documents.value = await listDocuments();
    syncDocumentDrafts();
    await refreshIngestionStatuses();
  });
}

async function retryRefreshDocuments() {
  await retry(async () => {
    documents.value = await listDocuments();
    syncDocumentDrafts();
    await refreshIngestionStatuses();
  });
}

function syncDocumentDrafts() {
  const nextScopes: Record<string, string> = {};
  const nextRoles: Record<string, string> = {};

  for (const document of documents.value) {
    nextScopes[document.id] = document.access_scope;
    nextRoles[document.id] = (document.allowed_role_ids ?? []).join(", ");
  }

  draftAccessScopeByDocument.value = nextScopes;
  draftAllowedRolesByDocument.value = nextRoles;
}

async function refreshIngestionStatuses() {
  const nextStatuses: Record<string, string> = {};
  const nextDetails: Record<string, { chunks: number; indexed: number }> = {};

  await Promise.all(
    Object.entries(ingestionJobByDocument.value).map(
      async ([documentId, jobId]) => {
        if (!documents.value.some((doc) => doc.id === documentId)) {
          return;
        }
        try {
          const job = await getIngestionJob(jobId);
          nextStatuses[documentId] = job.status;
          nextDetails[documentId] = {
            chunks: job.chunk_count,
            indexed: job.indexed_chunk_count,
          };
        } catch {
          nextStatuses[documentId] = "unknown";
        }
      }
    )
  );

  ingestionStatusByDocument.value = nextStatuses;
  ingestionDetailByDocument.value = nextDetails;
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  selectedFile.value = input.files?.[0] ?? null;
}

function handleBulkFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  bulkFiles.value = Array.from(input.files ?? []);
}

function formatAllowedRoles(roles: string[] | null, documentId: string): string {
  const draftScope = draftAccessScopeByDocument.value[documentId];
  const draftRoles = draftAllowedRolesByDocument.value[documentId]?.trim();

  if (draftScope === "role_restricted") {
    return draftRoles
      ? copy.value.draftRoles.replace("{roles}", draftRoles)
      : copy.value.noRolesSelectedYet;
  }

  if (!roles || roles.length === 0) {
    return copy.value.noRoleRestriction;
  }

  return copy.value.allowedRoles.replace("{roles}", roles.join(", "));
}

function formatStatusToken(status: string): string {
  switch (status) {
    case "unknown":
      return copy.value.statusUnknown;
    case "pending":
      return copy.value.statusPending;
    case "processing":
      return copy.value.statusProcessing;
    case "completed":
      return copy.value.statusCompleted;
    case "uploaded":
      return copy.value.statusUploaded;
    case "ready":
      return copy.value.statusReady;
    case "archived":
      return copy.value.statusArchived;
    case "failed":
      return copy.value.statusFailedLong;
    default:
      return status;
  }
}

function parseAllowedRoles(documentId: string): string[] {
  const draftRoles = draftAllowedRolesByDocument.value[documentId] ?? "";
  return draftRoles
    .split(",")
    .map((role) => role.trim())
    .filter(Boolean);
}

async function saveAccess(documentId: string) {
  busyDocumentId.value = documentId;
  try {
    const updated = await updateDocumentAccess(documentId, {
      access_scope: draftAccessScopeByDocument.value[documentId] ?? "tenant_public",
      allowed_role_ids:
        draftAccessScopeByDocument.value[documentId] === "role_restricted"
          ? parseAllowedRoles(documentId)
          : null,
    });
    documents.value = documents.value.map((doc) =>
      doc.id === documentId ? updated : doc
    );
    syncDocumentDrafts();
    statusMessage.value = copy.value.accessUpdated.replace("{title}", updated.title);
  } finally {
    busyDocumentId.value = null;
  }
}

async function queueReindex(documentId: string) {
  busyDocumentId.value = documentId;
  try {
    const job = await reindexDocument(documentId);
    ingestionJobByDocument.value[documentId] = job.id;
    ingestionStatusByDocument.value[documentId] = job.status;
    statusMessage.value = copy.value.reindexQueued.replace("{documentId}", documentId);
    await refreshDocuments();
  } finally {
    busyDocumentId.value = null;
  }
}

async function archive(documentId: string) {
  busyDocumentId.value = documentId;
  try {
    const updated = await archiveDocument(documentId);
    documents.value = documents.value.map((doc) =>
      doc.id === documentId ? updated : doc
    );
    statusMessage.value = copy.value.archivedMessage.replace("{title}", updated.title);
  } finally {
    busyDocumentId.value = null;
  }
}

async function unarchive(documentId: string) {
  busyDocumentId.value = documentId;
  try {
    const updated = await unarchiveDocument(documentId);
    documents.value = documents.value.map((doc) =>
      doc.id === documentId ? updated : doc
    );
    statusMessage.value = copy.value.restoredMessage.replace("{title}", updated.title);
  } finally {
    busyDocumentId.value = null;
  }
}

async function retryJob(documentId: string) {
  const jobId = ingestionJobByDocument.value[documentId];
  if (!jobId) {
    statusMessage.value = copy.value.noJobFound;
    return;
  }
  busyDocumentId.value = documentId;
  try {
    const result = await retryIngestionJob(jobId);
    ingestionStatusByDocument.value[documentId] = result.job.status;
    statusMessage.value = copy.value.retriedJob.replace("{jobId}", jobId);
    await refreshDocuments();
  } finally {
    busyDocumentId.value = null;
  }
}

async function submitUpload() {
  if (!selectedFile.value) {
    statusMessage.value = copy.value.chooseFileBeforeUpload;
    return;
  }

  uploading.value = true;
  statusMessage.value = "";

  try {
    const uploaded = await uploadDocument({
      file: selectedFile.value,
      title: title.value,
      access_scope: accessScope.value,
      ...(description.value ? { description: description.value } : {}),
    });
    ingestionJobByDocument.value[uploaded.id] = uploaded.ingestion_job_id;
    ingestionStatusByDocument.value[uploaded.id] = "pending";
    statusMessage.value = copy.value.uploadQueued.replace("{jobId}", String(uploaded.ingestion_job_id));
    resetForm();
    await refreshDocuments();
  } catch (error) {
    statusMessage.value = copy.value.uploadFailed;
    throw error;
  } finally {
    uploading.value = false;
  }
}

async function submitBulkUpload() {
  if (bulkFiles.value.length === 0) {
    bulkStatusMessage.value = copy.value.selectAtLeastOneFile;
    return;
  }

  bulkUploading.value = true;
  bulkStatusMessage.value = "";
  try {
    const result = await bulkUploadDocuments({
      files: bulkFiles.value,
      title_prefix: bulkTitlePrefix.value,
      access_scope: accessScope.value,
    });
    bulkResults.value = result.items.map((item) => ({
      index: item.index,
      file_name: item.file_name,
      status: item.status,
      document: item.document,
      error: item.error,
    }));
    bulkStatusMessage.value = copy.value.bulkSummary
      .replace("{success}", String(result.success_count))
      .replace("{failure}", String(result.failure_count));
    await refreshDocuments();
  } finally {
    bulkUploading.value = false;
  }
}

function clearBulkSelection() {
  bulkFiles.value = [];
  bulkResults.value = [];
  bulkStatusMessage.value = "";
}

function resetForm() {
  title.value = "";
  description.value = "";
  accessScope.value = "tenant_public";
  selectedFile.value = null;
}

function formatBytes(value: number): string {
  if (value === 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const unitIndex = Math.min(
    Math.floor(Math.log(value) / Math.log(1024)),
    units.length - 1
  );
  const scaled = value / 1024 ** unitIndex;
  return `${scaled.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

onMounted(async () => {
  await refreshDocuments();
});
</script>
