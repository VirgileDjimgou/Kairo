<template>
  <div class="d-flex min-vh-100 admin-shell-bg">
    <aside class="admin-sidebar d-none d-lg-flex flex-column p-3">
      <div class="d-flex align-items-center gap-2 mb-4 px-1">
        <i class="bi bi-shield-lock text-primary fs-5"></i>
        <span class="fw-bold text-dark">Admin Console</span>
      </div>

      <nav class="nav flex-column gap-1">
        <RouterLink
          to="/admin"
          class="nav-link sidebar-link rounded"
          active-class="active"
          end
        >
          <i class="bi bi-speedometer2 me-2"></i>Overview
        </RouterLink>
        <a class="nav-link sidebar-link rounded disabled" href="#"
          ><i class="bi bi-people me-2"></i>Users</a
        >
        <RouterLink
          to="/admin/documents"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-file-earmark-text me-2"></i>Documents
        </RouterLink>
        <a class="nav-link sidebar-link rounded disabled" href="#"
          ><i class="bi bi-list-check me-2"></i>Ingestion Jobs</a
        >
        <a class="nav-link sidebar-link rounded disabled" href="#"
          ><i class="bi bi-shield-check me-2"></i>Roles & Permissions</a
        >
      </nav>
    </aside>

    <main class="flex-grow-1 overflow-auto">
      <header class="topbar sticky-top bg-white border-bottom">
        <div
          class="d-flex align-items-center justify-content-between gap-3 px-3 px-lg-4 py-3"
        >
          <div>
            <div class="text-muted small text-uppercase fw-semibold">
              Admin dashboard
            </div>
            <div class="fw-semibold">Operational control center</div>
          </div>
          <div
            class="badge bg-warning-subtle text-warning border border-warning-subtle px-3 py-2"
          >
            Sprint 3 documents
          </div>
        </div>
      </header>

      <section class="content-shell">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<style scoped>
.admin-shell-bg {
  background: linear-gradient(
    180deg,
    rgba(245, 247, 251, 1) 0%,
    rgba(245, 247, 251, 0.92) 100%
  );
}

.admin-sidebar {
  background: #ffffff;
  border-right: 1px solid var(--om-border, #d9e2ec);
  width: 260px;
  min-height: 100vh;
}

.topbar {
  z-index: 1020;
}

.sidebar-link {
  color: var(--om-text, #1f2937);
  font-size: 0.875rem;
  padding: 0.45rem 0.75rem;
  text-decoration: none;
}

.sidebar-link:hover,
.sidebar-link.active {
  background: rgba(31, 79, 143, 0.08);
  color: var(--om-primary, #1f4f8f);
  font-weight: 500;
}

.content-shell {
  padding: 0;
}
</style>