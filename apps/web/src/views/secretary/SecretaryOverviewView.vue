<template>
  <div class="p-4 p-lg-5">
    <div class="secretary-hero rounded-4 p-4 p-lg-5 mb-4" data-testid="secretary-overview">
      <div class="d-flex flex-column flex-xl-row justify-content-between gap-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">
            Secretary general
          </div>
          <h1 class="h3 fw-bold mb-2">Official records and communication workspace</h1>
          <p class="text-muted mb-0 hero-copy">
            Manage the documents, policies, and announcements that shape the formal life of the organization, without entering finance or disciplinary operations.
          </p>
        </div>
        <div class="d-flex flex-wrap gap-2 align-items-start">
          <RouterLink to="/secretary/documents" class="btn btn-primary">Open documents</RouterLink>
          <RouterLink to="/secretary/announcements" class="btn btn-outline-secondary">Open announcements</RouterLink>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <RouterLink to="/secretary/documents" class="card-link text-decoration-none">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="icon-tile mb-3"><i class="bi bi-file-earmark-text fs-4"></i></div>
              <h2 class="h6 fw-bold mb-2">Documents</h2>
              <p class="text-muted small mb-0">
                Upload statutes, meeting records, internal notices, and operational reference material.
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
              <h2 class="h6 fw-bold mb-2">Policies</h2>
              <p class="text-muted small mb-0">
                Publish governance rules and keep policy references aligned with the official documents.
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
              <h2 class="h6 fw-bold mb-2">Announcements</h2>
              <p class="text-muted small mb-0">
                Prepare and publish official notices for members without touching finance or sanctions data.
              </p>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Boundaries
        </div>
        <div class="row g-3">
          <div class="col-md-6">
            <div class="boundary-card ok h-100">
              <div class="fw-semibold mb-2">Included in this workspace</div>
              <ul class="small text-muted mb-0">
                <li>Official documents and protocols</li>
                <li>Policy publication and updates</li>
                <li>Member-facing announcements</li>
              </ul>
            </div>
          </div>
          <div class="col-md-6">
            <div class="boundary-card blocked h-100" data-testid="secretary-boundaries">
              <div class="fw-semibold mb-2">Explicitly excluded</div>
              <ul class="small text-muted mb-0">
                <li>Contribution mutation and finance operations</li>
                <li>Disciplinary record administration</li>
                <li>Tenant-wide settings and unrestricted admin controls</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
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
