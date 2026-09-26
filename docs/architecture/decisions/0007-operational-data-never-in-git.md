# ADR-007: Operational Data Never Enters Git

Status: Accepted (added by Roadmap V2 Sprint 101 after a real exposure)

## Context

Real association documents (statutes, minutes, financial reports, named
disciplinary notices, member data) were found committed to the repository. Git
is the wrong store for this class of data: it replicates to every clone and its
history is effectively immutable.

## Decision

Operational documents live in MinIO/S3 through the tenant-scoped document
module. The repository carries only fictional fixtures (`seed/`). The
sensitive-file policy (`scripts/check-sensitive-files.mjs`) rejects tracked
operational document classes, and local staging directories are git-ignored.

## Consequences

- Developers import real documents locally through the document module, never
  through commits.
- Exposure incidents are handled with `docs/security/HISTORY_EXPOSURE_REPORT.md`
  and operator-approved history remediation (HUMAN_REQUIRED).
