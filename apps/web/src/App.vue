<template>
  <RouterView />
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { RouterView } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useLocaleStore } from "@/stores/locale.store";

const authStore = useAuthStore();
const localeStore = useLocaleStore();

onMounted(() => {
  localeStore.initialize();
  void authStore.restoreSession();
});
</script>
