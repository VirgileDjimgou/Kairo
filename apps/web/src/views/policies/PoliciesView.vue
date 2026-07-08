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
      <div class="d-flex gap-2 align-items-center">
        <select v-model="selectedCategory" class="form-select form-select-sm">
          <option value="">{{ copy.allCategories }}</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        <button class="btn om-primary-btn" type="button" @click="refreshPolicies" :disabled="loading">
          {{ loading ? copy.refreshing : copy.refresh }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-muted py-5 text-center">
      {{ copy.loading }}
    </div>

    <div v-else-if="filteredPolicies.length === 0" class="empty-state">
      <i class="bi bi-journal-text display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">{{ copy.emptyTitle }}</p>
      <p class="text-muted mb-0">
        {{ copy.emptyText }}
      </p>
    </div>

    <div v-else class="row g-3">
      <div v-for="policy in filteredPolicies" :key="policy.id" class="col-md-6 col-xl-4">
        <article class="card shadow-sm border-0 h-100 policy-card">
          <div class="card-body p-4">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-3">
              <div>
                <h2 class="h6 fw-bold mb-1">{{ policy.title }}</h2>
                <div class="small text-muted">{{ policy.category }}</div>
              </div>
              <span class="badge text-bg-success-subtle text-success border border-success-subtle">
                {{ policy.status }}
              </span>
            </div>

            <p class="text-muted small mb-3">
              {{ policy.description || copy.noDescription }}
            </p>

            <div class="vstack gap-2 small">
              <div v-if="policy.document_title" class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.linkedDocument }}</span>
                <span class="fw-medium text-end">{{ policy.document_title }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.updated }}</span>
                <span class="fw-medium text-end">{{ formatDate(policy.updated_at) }}</span>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { listPolicyCategories, listPublicPolicies, type PolicyRecordResponse } from '@/api/policies.api'
import { useLocaleStore } from '@/stores/locale.store'

const loading = ref(true)
const policies = ref<PolicyRecordResponse[]>([])
const categories = ref<string[]>([])
const selectedCategory = ref('')
const localeStore = useLocaleStore()
const copy = {
  kicker: localeStore.currentLocale === 'de' ? 'Regeln' : localeStore.currentLocale === 'en' ? 'Policies' : 'Règlements',
  title: localeStore.currentLocale === 'de' ? 'Öffentliche Regeln und Verfahren' : localeStore.currentLocale === 'en' ? 'Public rules and procedures' : 'Règles et procédures publiques',
  subtitle: localeStore.currentLocale === 'de' ? 'Durchsuchen Sie den veröffentlichten Richtlinienkatalog Ihrer Organisation.' : localeStore.currentLocale === 'en' ? "Browse the tenant's published policy catalog and filter by category." : "Parcourez le catalogue des règles publiées de l'organisation et filtrez par catégorie.",
  allCategories: localeStore.currentLocale === 'de' ? 'Alle catégories' : localeStore.currentLocale === 'en' ? 'All categories' : 'Toutes les catégories',
  refreshing: localeStore.currentLocale === 'de' ? 'Aktualisierung...' : localeStore.currentLocale === 'en' ? 'Refreshing...' : 'Actualisation...',
  refresh: localeStore.currentLocale === 'de' ? 'Actualiser' : localeStore.currentLocale === 'en' ? 'Refresh' : 'Actualiser',
  loading: localeStore.currentLocale === 'de' ? 'Richtlinien werden geladen...' : localeStore.currentLocale === 'en' ? 'Loading policies...' : 'Chargement des règlements...',
  emptyTitle: localeStore.currentLocale === 'de' ? 'Noch keine öffentlichen Richtlinien' : localeStore.currentLocale === 'en' ? 'No public policies yet' : 'Aucun règlement public pour le moment',
  emptyText: localeStore.currentLocale === 'de' ? 'Das Admin-Team hat noch keine organisationsweiten Regeln veröffentlicht.' : localeStore.currentLocale === 'en' ? 'The admin team has not published any tenant-wide rules yet.' : "L'équipe administrative n'a pas encore publié de règles globales.",
  noDescription: localeStore.currentLocale === 'de' ? 'Keine Beschreibung vorhanden.' : localeStore.currentLocale === 'en' ? 'No description provided.' : 'Aucune description fournie.',
  linkedDocument: localeStore.currentLocale === 'de' ? 'Verknüpftes Dokument' : localeStore.currentLocale === 'en' ? 'Linked document' : 'Document lié',
  updated: localeStore.currentLocale === 'de' ? 'Mis à jour' : localeStore.currentLocale === 'en' ? 'Updated' : 'Mis à jour',
}

const filteredPolicies = computed(() => {
  if (!selectedCategory.value) {
    return policies.value
  }
  return policies.value.filter((policy) => policy.category === selectedCategory.value)
})

async function refreshPolicies() {
  loading.value = true
  try {
    const [policyResponse, categoryResponse] = await Promise.all([
      listPublicPolicies(),
      listPolicyCategories(),
    ])
    policies.value = policyResponse
    categories.value = categoryResponse.categories
  } finally {
    loading.value = false
  }
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString()
}

onMounted(refreshPolicies)
</script>

<style scoped>
.policy-card {
  border-radius: 1rem;
}
</style>
