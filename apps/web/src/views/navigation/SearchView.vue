<template>
  <div class="p-3 p-md-4 p-lg-5">
    <PageHeader :title="copy.title" :subtitle="copy.subtitle" />
    <div class="card border-0 shadow-sm">
      <div class="card-body p-3 p-md-4">
        <GlobalSearchPanel />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import GlobalSearchPanel from '@/components/search/GlobalSearchPanel.vue'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()

const copy = computed(() => ({
  title: localeStore.t('search.title'),
  subtitle: localeStore.t('search.subtitle'),
}))
</script>
