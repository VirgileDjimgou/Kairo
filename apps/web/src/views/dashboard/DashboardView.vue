<template>
  <div class="p-4">
    <!-- Page header -->
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">Dashboard</h1>
        <p class="text-muted small mb-0">
          Welcome back, <strong>{{ authStore.user?.display_name }}</strong>
        </p>
      </div>
      <span
        class="badge bg-success-subtle text-success border border-success-subtle px-3 py-2"
      >
        <i class="bi bi-circle-fill me-1" style="font-size: 0.5rem"></i>
        System online
      </span>
    </div>

    <!-- Sprint status card -->
    <div class="alert alert-info border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex gap-3">
        <i class="bi bi-rocket-takeoff fs-4 flex-shrink-0"></i>
        <div>
          <h6 class="alert-heading mb-1">Sprint 9 complete</h6>
          <p class="mb-0 small">
            Policies and disciplinary records are now part of the product surface.
            Members can browse public policies and inspect their own disciplinary
            history; admins can create and manage policy and discipline records.
          </p>
        </div>
      </div>
    </div>

    <!-- Summary cards -->
    <div class="row g-3 mb-4">
      <div class="col-sm-6 col-lg-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-primary-subtle text-primary rounded-3 p-3">
              <i class="bi bi-person-badge fs-4"></i>
            </div>
            <div>
              <div class="text-muted small">My roles</div>
              <div class="fw-semibold">
                {{ authStore.user?.roles.join(", ") || "—" }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-success-subtle text-success rounded-3 p-3">
              <i class="bi bi-building fs-4"></i>
            </div>
            <div>
              <div class="text-muted small">Organization ID</div>
              <div class="fw-semibold font-monospace small">
                {{ authStore.user?.tenant_id?.slice(0, 8) }}…
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-warning-subtle text-warning rounded-3 p-3">
              <i class="bi bi-file-earmark-text fs-4"></i>
            </div>
            <div>
              <div class="text-muted small">Documents</div>
              <div class="fw-semibold">Sprint 3 - 7</div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-info-subtle text-info rounded-3 p-3">
              <i class="bi bi-journal-check fs-4"></i>
            </div>
            <div>
              <div class="text-muted small">Policies</div>
              <div class="fw-semibold">Sprint 9</div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-info-subtle text-info rounded-3 p-3">
              <i class="bi bi-chat-dots fs-4"></i>
            </div>
            <div>
              <div class="text-muted small">AI Chat</div>
              <div class="fw-semibold">Sprint 6</div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body d-flex align-items-center gap-3">
            <div class="stat-icon bg-success-subtle text-success rounded-3 p-3">
              <i class="bi bi-people fs-4"></i>
            </div>
            <div>
              <div class="text-muted small">Members</div>
              <div class="fw-semibold">Sprint 8</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Roadmap table -->
    <div class="card shadow-sm border-0">
      <div class="card-header bg-transparent border-bottom py-3">
        <h5 class="mb-0 fw-semibold">Sprint Roadmap</h5>
      </div>
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th class="ps-4">Sprint</th>
              <th>Goal</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sprint in sprints" :key="sprint.id">
              <td class="ps-4 fw-medium">{{ sprint.id }}</td>
              <td>{{ sprint.goal }}</td>
              <td>
                <span
                  class="badge rounded-pill"
                  :class="statusClass(sprint.status)"
                >
                  {{ sprint.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth.store";

const authStore = useAuthStore();

const sprints = [
  { id: "Sprint 0", goal: "Foundation & repository skeleton", status: "Done" },
  { id: "Sprint 1", goal: "Identity, tenancy & JWT auth", status: "Done" },
  { id: "Sprint 2", goal: "Professional Vue layout", status: "Done" },
  { id: "Sprint 3", goal: "Document upload & MinIO storage", status: "Done" },
  { id: "Sprint 4", goal: "Ingestion worker & parsers", status: "Done" },
  { id: "Sprint 5", goal: "Embeddings & Qdrant indexing", status: "Done" },
  { id: "Sprint 6", goal: "Secure RAG chat with citations", status: "Done" },
  { id: "Sprint 7", goal: "Admin RAG controls", status: "Done" },
  { id: "Sprint 8", goal: "Membership & contributions", status: "Done" },
  { id: "Sprint 9", goal: "Policies, rules & discipline", status: "Done" },
  { id: "Sprint 10", goal: "Events & announcements", status: "Planned" },
];

function statusClass(status: string) {
  return (
    {
      Done: "bg-success-subtle text-success border border-success-subtle",
      Next: "bg-primary-subtle text-primary border border-primary-subtle",
      Planned:
        "bg-secondary-subtle text-secondary border border-secondary-subtle",
    }[status] ?? "bg-secondary-subtle text-secondary"
  );
}
</script>

<style scoped>
.stat-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
