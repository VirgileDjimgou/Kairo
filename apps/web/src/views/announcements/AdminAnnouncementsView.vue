<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">{{ copy.title }}</h1>
        <p class="text-muted small mb-0">{{ copy.subtitle }}</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-secondary btn-sm" @click="exportAnnouncements" :disabled="exporting">
          <i v-if="exporting" class="spinner-border spinner-border-sm me-1"></i>
          <i v-else class="bi bi-download me-1"></i>{{ copy.exportCsv }}
        </button>
        <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#createModal">
          <i class="bi bi-plus-circle me-1"></i>{{ copy.addAnnouncement }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-3" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ copy.loading }}</span>
      </div>
    </div>

    <div v-else-if="announcements.length > 0" class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle" :aria-label="copy.title">
          <thead class="table-light">
            <tr>
              <th class="ps-4" scope="col">{{ copy.titleColumn }}</th>
              <th scope="col">{{ copy.publishedColumn }}</th>
              <th scope="col">{{ copy.expiresColumn }}</th>
              <th scope="col">{{ copy.visibilityColumn }}</th>
              <th class="text-end pe-4" scope="col">{{ copy.actionsColumn }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in announcements" :key="a.id">
              <td class="ps-4 fw-medium">{{ a.title }}</td>
              <td class="small">{{ a.published_at ? formatDate(a.published_at) : '—' }}</td>
              <td class="small">{{ a.expires_at ? formatDate(a.expires_at) : '—' }}</td>
              <td>
                <span class="badge bg-info-subtle text-info border border-info-subtle">{{ visibilityLabel(a.visibility_scope) }}</span>
              </td>
              <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-secondary me-1" :aria-label="copy.editAnnouncement" @click="editItem(a)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" :aria-label="copy.deleteAnnouncement" @click="confirmDelete(a)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="empty-state">
      <i class="bi bi-megaphone display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">{{ copy.emptyTitle }}</p>
      <p class="text-muted mb-0">{{ copy.emptyText }}</p>
    </div>

    <ConfirmModal
      v-if="showDeleteModal && deletingItem"
      :title="copy.deleteAnnouncement"
      :message="`${copy.deleteAnnouncement} &quot;${deletingItem.title}&quot;?`"
      @confirm="handleDelete"
      @cancel="showDeleteModal = false; deletingItem = null"
    />

    <div class="modal fade" id="createModal" tabindex="-1" aria-labelledby="createModalLabel">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="createModalLabel">{{ editingId ? copy.edit : copy.add }} {{ copy.announcement }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ copy.titleLabel }}</label>
              <input v-model="form.title" class="form-control form-control-sm" required />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ copy.bodyLabel }}</label>
              <textarea v-model="form.body" class="form-control form-control-sm" rows="4" required></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ copy.visibilityLabel }}</label>
              <select v-model="form.visibility_scope" class="form-select form-select-sm">
                <option value="members_only">{{ copy.visibilityMembers }}</option>
                <option value="tenant_public">{{ copy.visibilityTenant }}</option>
                <option value="admin_only">{{ copy.visibilityAdmin }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">{{ copy.expiresAtLabel }}</label>
              <input v-model="form.expires_at" type="datetime-local" class="form-control form-control-sm" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">{{ copy.cancel }}</button>
            <button type="button" class="btn btn-sm btn-primary" @click="handleSave" :disabled="saving">
              {{ saving ? copy.saving : copy.save }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import * as bootstrap from 'bootstrap'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { listAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement, exportAnnouncementsCsv, type AnnouncementResponse } from '@/api/announcements.api'
import { useCsvExport } from '@/composables/useCsvExport'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const announcements = ref<AnnouncementResponse[]>([])
const editingId = ref<string | null>(null)
const showDeleteModal = ref(false)
const deletingItem = ref<AnnouncementResponse | null>(null)

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      title: 'Ankuendigungen',
      subtitle: 'Verwalten Sie die offiziellen Mitteilungen Ihrer Organisation',
      exportCsv: 'CSV exportieren',
      addAnnouncement: 'Ankuendigung hinzufuegen',
      loading: 'Wird geladen...',
      titleColumn: 'Titel',
      publishedColumn: 'Veröffentlicht',
      expiresColumn: 'Läuft ab',
      visibilityColumn: 'Sichtbarkeit',
      actionsColumn: 'Aktionen',
      editAnnouncement: 'Ankuendigung bearbeiten',
      deleteAnnouncement: 'Ankuendigung löschen',
      emptyTitle: 'Noch keine Ankuendigungen',
      emptyText: 'Erstellen Sie Ankuendigungen, um Mitglieder zu informieren.',
      edit: 'Bearbeiten',
      add: 'Hinzufuegen',
      announcement: 'Ankuendigung',
      titleLabel: 'Titel',
      bodyLabel: 'Inhalt',
      visibilityLabel: 'Sichtbarkeit',
      visibilityMembers: 'Nur Mitglieder',
      visibilityTenant: 'Tenant-oeffentlich',
      visibilityAdmin: 'Nur Admin',
      expiresAtLabel: 'Läuft ab am (optional)',
      cancel: 'Abbrechen',
      saving: 'Speichern...',
      save: 'Speichern',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      title: 'Announcements',
      subtitle: 'Manage organization announcements',
      exportCsv: 'Export CSV',
      addAnnouncement: 'Add announcement',
      loading: 'Loading...',
      titleColumn: 'Title',
      publishedColumn: 'Published',
      expiresColumn: 'Expires',
      visibilityColumn: 'Visibility',
      actionsColumn: 'Actions',
      editAnnouncement: 'Edit announcement',
      deleteAnnouncement: 'Delete announcement',
      emptyTitle: 'No announcements yet',
      emptyText: 'Create announcements to inform your organization members.',
      edit: 'Edit',
      add: 'Add',
      announcement: 'announcement',
      titleLabel: 'Title',
      bodyLabel: 'Body',
      visibilityLabel: 'Visibility',
      visibilityMembers: 'Members only',
      visibilityTenant: 'Tenant public',
      visibilityAdmin: 'Admin only',
      expiresAtLabel: 'Expires at (optional)',
      cancel: 'Cancel',
      saving: 'Saving...',
      save: 'Save',
    }
  }
  return {
    title: 'Annonces',
    subtitle: "Gérez les annonces officielles de l'organisation",
    exportCsv: 'Exporter CSV',
    addAnnouncement: 'Ajouter une annonce',
    loading: 'Chargement...',
    titleColumn: 'Titre',
    publishedColumn: 'Publié',
    expiresColumn: 'Expire',
    visibilityColumn: 'Visibilité',
    actionsColumn: 'Actions',
    editAnnouncement: 'Modifier l’annonce',
    deleteAnnouncement: 'Supprimer l’annonce',
    emptyTitle: 'Aucune annonce pour le moment',
    emptyText: 'Créez des annonces pour informer les membres de votre organisation.',
    edit: 'Modifier',
    add: 'Ajouter',
    announcement: 'annonce',
    titleLabel: 'Titre',
    bodyLabel: 'Contenu',
    visibilityLabel: 'Visibilité',
    visibilityMembers: 'Membres uniquement',
    visibilityTenant: 'Public au tenant',
    visibilityAdmin: 'Admin uniquement',
    expiresAtLabel: "Expire le (optionnel)",
    cancel: 'Annuler',
    saving: 'Enregistrement...',
    save: 'Enregistrer',
  }
})

const { exportCsv, exporting } = useCsvExport()
const form = ref({ title: '', body: '', visibility_scope: 'members_only', expires_at: '' })

function setError(err: unknown) {
  error.value = (err as any)?.response?.data?.detail || (err as any)?.message || (localeStore.currentLocale === 'en' ? 'An unexpected error occurred' : localeStore.currentLocale === 'de' ? 'Ein unerwarteter Fehler ist aufgetreten' : "Une erreur inattendue s'est produite")
}

function visibilityLabel(value: string): string {
  const labels: Record<string, string> = {
    members_only: copy.value.visibilityMembers,
    tenant_public: copy.value.visibilityTenant,
    admin_only: copy.value.visibilityAdmin,
  }
  return labels[value] || value
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(localeStore.currentLocale === 'fr' ? 'fr-FR' : localeStore.currentLocale === 'de' ? 'de-DE' : 'en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function load() {
  try {
    announcements.value = await listAnnouncements()
  } catch (err) {
    setError(err)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const payload: any = { ...form.value }
    payload.expires_at = payload.expires_at ? new Date(payload.expires_at).toISOString() : null
    if (editingId.value) {
      await updateAnnouncement(editingId.value, payload)
    } else {
      await createAnnouncement(payload)
    }
    await load()
    const modal = bootstrap.Modal.getInstance(document.getElementById('createModal')!)
    modal?.hide()
    form.value = { title: '', body: '', visibility_scope: 'members_only', expires_at: '' }
    editingId.value = null
  } catch (err) {
    setError(err)
  } finally {
    saving.value = false
  }
}

function editItem(a: AnnouncementResponse) {
  editingId.value = a.id
  form.value = {
    title: a.title,
    body: a.body,
    visibility_scope: a.visibility_scope,
    expires_at: a.expires_at ? a.expires_at.slice(0, 16) : '',
  }
  nextTick(() => new bootstrap.Modal(document.getElementById('createModal')!).show())
}

function confirmDelete(a: AnnouncementResponse) {
  deletingItem.value = a
  showDeleteModal.value = true
}

async function handleDelete() {
  if (!deletingItem.value) return
  try {
    await deleteAnnouncement(deletingItem.value.id)
    await load()
  } catch (err) {
    setError(err)
  } finally {
    showDeleteModal.value = false
    deletingItem.value = null
  }
}

async function exportAnnouncements() {
  try {
    await exportCsv(exportAnnouncementsCsv, 'announcements.csv')
  } catch (err) {
    setError(err)
  }
}

onMounted(load)
</script>
