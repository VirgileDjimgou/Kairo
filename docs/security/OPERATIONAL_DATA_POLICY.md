# Operational Data Policy

Last updated: 2026-09-25 (Roadmap V2 Sprint 101)

## Rule

Real association documents and operational data are **not source code**. They must
never be committed to this repository — not in `HEAD`, not in a branch, not in a
release tag.

Operational data includes, without limitation:

- statutes, bylaws, internal rules and codes of conduct;
- general assembly minutes and board decisions;
- membership applications, member registers and member contact data;
- contribution records, financial reports, budgets and balances;
- disciplinary records, warnings, sanctions and formal notices;
- sponsorships, contracts and correspondence;
- exports or spreadsheets containing any of the above.

## Where operational documents belong

| Content | Storage |
| --- | --- |
| Association documents for AI retrieval | MinIO/S3 object storage, uploaded through the Kairo document module (tenant-scoped, access-controlled) |
| Backups of the association's data | Encrypted backup archives written by the Kairo backup service to the operator-configured S3 destination |
| Local working copies during migration | An untracked local directory such as `Combis Sport Verein/` (git-ignored by policy) — never staged |
| Fictional development fixtures | `seed/` (allow-listed in `scripts/check-sensitive-files.mjs`) |

The Kairo application already provides the correct home: documents uploaded through
the API are stored in object storage, parsed and indexed with tenant-scoped access
control. The repository carries only fictional fixtures.

## Enforcement

`scripts/check-sensitive-files.mjs` rejects tracked files that match operational
data classes: spreadsheets, documents (PDF/DOCX/DOC/ODT/PPTX/RTF), tabular exports
(CSV/TSV outside the fictional seed fixtures), database dumps, backup archives,
secret-bearing key material and credential JSON.

```bash
node scripts/check-sensitive-files.mjs
```

The script runs in CI (`security` job). Do not weaken it to land a document; move
the document to tenant storage instead.

## Local staging areas

- `Combis Sport Verein/` is a **local, git-ignored** staging directory that may
  contain real association documents on an operator workstation. It is excluded
  from the tracked tree by `.gitignore` and by the sensitive-file policy.
- `services/api/tmp/` is git-ignored generated output.
- If real documents must be moved between machines, use the association's private
  storage or an encrypted channel — never a Git commit.
