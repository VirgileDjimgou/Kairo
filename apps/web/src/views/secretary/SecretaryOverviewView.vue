<template>
  <div class="p-4 p-lg-5">
    <div class="secretary-hero rounded-4 p-4 p-lg-5 mb-4" data-testid="secretary-overview">
      <div class="d-flex flex-column flex-xl-row justify-content-between gap-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">
            {{ copy.kicker }}
          </div>
          <h1 class="h3 fw-bold mb-2">{{ copy.title }}</h1>
          <p class="text-muted mb-0 hero-copy">
            {{ copy.lead }}
          </p>
        </div>
        <div class="d-flex flex-wrap gap-2 align-items-start">
          <RouterLink to="/secretary/documents" class="btn btn-primary">{{ copy.openDocuments }}</RouterLink>
          <RouterLink to="/secretary/announcements" class="btn btn-outline-secondary">{{ copy.openAnnouncements }}</RouterLink>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <RouterLink to="/secretary/documents" class="card-link text-decoration-none">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="icon-tile mb-3"><i class="bi bi-file-earmark-text fs-4"></i></div>
              <h2 class="h6 fw-bold mb-2">{{ copy.documentsTitle }}</h2>
              <p class="text-muted small mb-0">
                {{ copy.documentsText }}
              </p>
            </div>
          </div>
        </RouterLink>
      </div>

      <div class="col-md-4">
        <RouterLink to="/secretary/policies" class="card-link text-decoration-none">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="icon-tile mb-3"><i class="bi bi-journal-text fs-4"></i></div>
              <h2 class="h6 fw-bold mb-2">{{ copy.policiesTitle }}</h2>
              <p class="text-muted small mb-0">
                {{ copy.policiesText }}
              </p>
            </div>
          </div>
        </RouterLink>
      </div>

      <div class="col-md-4">
        <RouterLink to="/secretary/announcements" class="card-link text-decoration-none">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="icon-tile mb-3"><i class="bi bi-megaphone fs-4"></i></div>
              <h2 class="h6 fw-bold mb-2">{{ copy.announcementsTitle }}</h2>
              <p class="text-muted small mb-0">
                {{ copy.announcementsText }}
              </p>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ copy.boundariesTitle }}
        </div>
        <div class="row g-3">
          <div class="col-md-6">
            <div class="boundary-card ok h-100">
              <div class="fw-semibold mb-2">{{ copy.includedTitle }}</div>
              <ul class="small text-muted mb-0">
                <li>{{ copy.includedItem1 }}</li>
                <li>{{ copy.includedItem2 }}</li>
                <li>{{ copy.includedItem3 }}</li>
              </ul>
            </div>
          </div>
          <div class="col-md-6">
            <div class="boundary-card blocked h-100" data-testid="secretary-boundaries">
              <div class="fw-semibold mb-2">{{ copy.excludedTitle }}</div>
              <ul class="small text-muted mb-0">
                <li>{{ copy.excludedItem1 }}</li>
                <li>{{ copy.excludedItem2 }}</li>
                <li>{{ copy.excludedItem3 }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      kicker: 'Generalsekretariat',
      title: 'Offizielle Dokumente und Kommunikationszentrale',
      lead: 'Verwalten Sie Dokumente, Regeln und Ankuendigungen fuer das formelle Vereinsleben, ohne in Finanzen oder Disziplin einzugreifen.',
      openDocuments: 'Dokumente oeffnen',
      openAnnouncements: 'Ankuendigungen oeffnen',
      documentsTitle: 'Dokumente',
      documentsText: 'Satzungen, Sitzungsprotokolle, interne Hinweise und Referenzmaterial hochladen.',
      policiesTitle: 'Regeln',
      policiesText: 'Governance-Regeln veröffentlichen und mit den offiziellen Dokumenten abstimmen.',
      announcementsTitle: 'Ankuendigungen',
      announcementsText: 'Offizielle Mitteilungen fuer Mitglieder vorbereiten und veroeffentlichen, ohne Finanzen oder Sanktionen zu beruehren.',
      boundariesTitle: 'Grenzen',
      includedTitle: 'In diesem Bereich enthalten',
      includedItem1: 'Offizielle Dokumente und Protokolle',
      includedItem2: 'Veroeffentlichung und Aktualisierung von Regeln',
      includedItem3: 'Mitgliederankuendigungen',
      excludedTitle: 'Ausdruecklich ausgeschlossen',
      excludedItem1: 'Beitrags- und Finanzvorgaenge',
      excludedItem2: 'Verwaltung disziplinarer Eintraege',
      excludedItem3: 'Tenant-weite Einstellungen und uneingeschraenkte Adminrechte',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      kicker: 'Secretary general',
      title: 'Official records and communication workspace',
      lead: 'Manage the documents, policies, and announcements that shape the formal life of the organization without entering finance or disciplinary operations.',
      openDocuments: 'Open documents',
      openAnnouncements: 'Open announcements',
      documentsTitle: 'Documents',
      documentsText: 'Upload statutes, meeting records, internal notices, and operational reference material.',
      policiesTitle: 'Policies',
      policiesText: 'Publish governance rules and keep policy references aligned with the official documents.',
      announcementsTitle: 'Announcements',
      announcementsText: 'Prepare and publish official notices for members without touching finance or sanctions data.',
      boundariesTitle: 'Boundaries',
      includedTitle: 'Included in this workspace',
      includedItem1: 'Official documents and protocols',
      includedItem2: 'Policy publication and updates',
      includedItem3: 'Member-facing announcements',
      excludedTitle: 'Explicitly excluded',
      excludedItem1: 'Contribution mutation and finance operations',
      excludedItem2: 'Disciplinary record administration',
      excludedItem3: 'Tenant-wide settings and unrestricted admin controls',
    }
  }
  return {
    kicker: 'Secrétaire général',
    title: 'Espace des documents et de la communication officielle',
    lead: "Gérez les documents, règlements et annonces qui structurent la vie formelle de l'association, sans toucher aux finances ni à la discipline.",
    openDocuments: 'Ouvrir les documents',
    openAnnouncements: 'Ouvrir les annonces',
    documentsTitle: 'Documents',
    documentsText: 'Téléverser les statuts, procès-verbaux, notes internes et documents de référence.',
    policiesTitle: 'Règlements',
    policiesText: 'Publier les règles de gouvernance et aligner les références avec les documents officiels.',
    announcementsTitle: 'Annonces',
    announcementsText: 'Préparer et publier les communications officielles aux membres sans toucher aux finances ou aux sanctions.',
    boundariesTitle: 'Périmètre',
    includedTitle: 'Inclus dans cet espace',
    includedItem1: 'Documents et protocoles officiels',
    includedItem2: 'Publication et mise à jour des règlements',
    includedItem3: 'Annonces à destination des membres',
    excludedTitle: 'Exclu explicitement',
    excludedItem1: 'Mouvements de cotisations et opérations financières',
    excludedItem2: 'Administration des sanctions',
    excludedItem3: 'Réglages globaux du tenant et droits admin sans limite',
  }
})
</script>

<style scoped>
.secretary-hero {
  background:
    radial-gradient(circle at top right, rgba(191, 219, 254, 0.4), transparent 30%),
    linear-gradient(135deg, #f7f4ee 0%, #ffffff 70%);
  border: 1px solid #e3ddd2;
}

.hero-copy {
  max-width: 42rem;
}

.icon-tile {
  width: 3rem;
  height: 3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.9rem;
  background: #eef3f8;
  color: #215d91;
}

.card-link {
  color: inherit;
}

.card-link .card:hover {
  transform: translateY(-2px);
  transition: transform 140ms ease;
}

.boundary-card {
  border-radius: 1rem;
  padding: 1rem;
  border: 1px solid #dde4ec;
}

.boundary-card.ok {
  background: #eef9f1;
}

.boundary-card.blocked {
  background: #fff7ed;
}
</style>
