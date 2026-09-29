<template>
  <div
    v-if="authStore.isDemoSession && suggestedActions.length"
    class="demo-tour card border-0 shadow-sm mb-4"
    data-testid="demo-guided-tour"
  >
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis mb-2">
            <i class="bi bi-signpost-split me-1"></i>{{ localeStore.t("demo.tourTitle") }}
          </div>
          <h2 class="h6 fw-bold mb-1">{{ localeStore.t("demo.tourSubtitle") }}</h2>
        </div>
        <RouterLink to="/demo" class="btn btn-outline-secondary btn-sm align-self-start">
          <i class="bi bi-arrow-repeat me-1"></i>{{ localeStore.t("demo.tourRestart") }}
        </RouterLink>
      </div>

      <ol class="demo-tour__steps list-unstyled mt-3 mb-0">
        <li v-for="(action, index) in suggestedActions" :key="action.to + action.label">
          <RouterLink :to="action.to" class="demo-tour__step">
            <span class="demo-tour__index">{{ index + 1 }}</span>
            <span class="demo-tour__icon"><i :class="action.icon"></i></span>
            <span class="demo-tour__label">{{ action.label }}</span>
            <span class="demo-tour__go small">{{ localeStore.t("demo.tourGo") }}</span>
          </RouterLink>
        </li>
      </ol>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useLocaleStore } from "@/stores/locale.store";
import { useRoleNavigation } from "@/composables/useRoleNavigation";

const authStore = useAuthStore();
const localeStore = useLocaleStore();
const { moduleNavigation } = useRoleNavigation();

const suggestedActions = computed(() => moduleNavigation.value.slice(0, 3));
</script>

<style scoped>
.demo-tour__steps {
  display: grid;
  gap: 0.5rem;
}

.demo-tour__step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.85rem;
  border-radius: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #14233a;
  text-decoration: none;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.demo-tour__step:hover {
  background: rgba(31, 79, 143, 0.06);
  border-color: rgba(31, 79, 143, 0.3);
}

.demo-tour__index {
  display: inline-flex;
  width: 1.6rem;
  height: 1.6rem;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #14233a;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  flex: 0 0 auto;
}

.demo-tour__icon {
  color: #1e63b5;
}

.demo-tour__label {
  font-weight: 600;
}

.demo-tour__go {
  margin-left: auto;
  color: #1e63b5;
}
</style>
