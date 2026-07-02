# Professional Release Candidate Checklist

Use this checklist when validating Kairo as a release candidate for a professional association deployment.

## Role Matrix

- [ ] `member` can only access personal data and read-only association information
- [ ] `secretary_general` can manage documents, policies, and announcements
- [ ] `treasurer` can manage finance operations without disciplinary power
- [ ] `auditor` can review finance and audit data without mutating records
- [ ] `censor` can manage disciplinary records without finance access
- [ ] `sports_manager` can manage sports events without admin spillover
- [ ] `president` and `vice_president` can use the governance cockpit without principal-admin powers
- [ ] `principal_admin` can manage tenant-wide settings without breaking tenant isolation

## Backend Verification

- [ ] Run the release-candidate backend matrix
- [ ] Confirm all module guards still return `403` for disabled or unauthorized access
- [ ] Confirm cross-tenant settings mutation is rejected
- [ ] Confirm the chatbot still refuses unauthorized structured answers before LLM calls
- [ ] Confirm audit logging still captures sensitive mutations

## Browser Verification

- [ ] Run the release-candidate browser matrix
- [ ] Confirm each role lands in the correct workspace
- [ ] Confirm ordinary members keep a compact, read-first navigation shell
- [ ] Confirm the principal-admin shell is visibly distinct from office workspaces

## Release Hygiene

- [ ] README, roadmap, status, and AI handoff docs are in sync
- [ ] Demo seed includes the expanded role set
- [ ] Demo walkthrough covers the expanded role set
- [ ] Known risks are documented explicitly
- [ ] No unresolved tenant-isolation or role-leak issue remains open
