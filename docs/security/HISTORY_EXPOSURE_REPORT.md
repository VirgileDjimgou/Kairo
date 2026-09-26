# Git History Exposure Report

Last updated: 2026-09-25 (Roadmap V2 Sprint 101)
Repository: github.com/VirgileDjimgou/Kairo (public)
Baseline commit audited: 713cc5b79a81b5c83bc30e8280bebc8d0147fe1d

## Scope and method

- `git ls-files` path audit of the tracked tree for document, spreadsheet and
  secret classes.
- `git log --diff-filter=A --name-only` sweep for every document-class path ever
  added across all history.
- gitleaks v8 full-history scan (`zricethezav/gitleaks:latest detect`) with
  `--redact`; report of record kept out of the repository.
- No remote history was rewritten. No commit was rewritten. All remediation
  below is **HUMAN_REQUIRED**.

## HEAD status (after Sprint 101)

The current tracked tree contains **no confirmed real tenant operational
documents**. Real documents remain on the operator workstation in the git-ignored
`Combis Sport Verein/` staging area only.

| Finding | Class | In HEAD? | Action taken |
| --- | --- | --- | --- |
| 51 real association documents under `Combis Sport Verein/` | Personal data, financial data, governance records | Removed from tracking in Sprint 101 (local copies preserved) | `git rm --cached`, `.gitignore` rule, policy documented |
| `JWT_SECRET_KEY` value in `docker-compose.prod.yml` | Live credential (signing key) | Removed in Sprint 100 (compose now fails closed) | HUMAN_REQUIRED: rotation |
| `services/api/tmp/pdfs/finance-report-preview.pdf` | Generated preview artifact | Removed from tracking in Sprint 101 | `git rm --cached` |
| `.vscode/PythonImportHelper-v2-Completion.json` | Editor cache | Removed from tracking in Sprint 101 | `git rm --cached` |

## Historical exposure detail

### 1. Real association documents (personal and financial data)

Introduced in commits `66b24a5`, `5619b6e` and `4a12702`. Classes:

- **Named disciplinary material** — warning and formal-notice documents whose
  filenames contain full member names (highest sensitivity).
- **Financial data** — contribution spreadsheets, annual/semi-annual financial
  reports and balances.
- **Governance records** — statutes, general assembly minutes (including June
  2026 minutes), board acknowledgements.
- **Membership material** — application forms, member competence catalogue.

Because the repository is public, these files are world-readable through the
commit history until history remediation is performed or the content is
formally withdrawn/re-issued by the association.

### 2. Historical signing secret

Commit `2f03643f` (`docker-compose.prod.yml`) contains a concrete
`JWT_SECRET_KEY` value. Any deployment that used the committed value must be
considered compromised: an attacker with the repository can forge valid session
tokens for that deployment.

## HUMAN_REQUIRED remediation

Nothing below was executed automatically. Remote history rewriting is a
destructive, externally visible operation and requires explicit operator
approval.

### A. Rotate the exposed JWT secret (do this first)

1. Generate a new secret on the deployment host:
   `openssl rand -base64 48`
2. Set `JWT_SECRET_KEY` in the production environment (never in the repo).
3. Restart API and worker containers.
4. All existing sessions become invalid; users must sign in again.
5. Record the rotation date in the deployment log.

### B. Purge the exposed documents and secret from history

A prepared script is available at
`scripts/security/prepare-history-remediation.ps1`. It prints the exact
`git filter-repo` commands and performs a dry run only. To execute:

1. Take a full backup clone of the repository.
2. Install `git-filter-repo` on the operator machine.
3. Run the printed commands against a fresh clone (not this working tree).
4. Verify with gitleaks and `git log --all -- "Combis Sport Verein"` (expect no
   results).
5. Coordinate the force-push with every collaborator (all clones must re-clone).
6. Request GitHub cache/secret-scanning invalidation for the old blobs.

### C. Privacy follow-up with the association

- The named disciplinary documents concern identifiable people. The association
  should be informed so it can apply its own retention and notification duties.
- Re-issue any document whose confidentiality matters through tenant storage
  (MinIO/S3) instead of distribution channels.

## Acceptance evidence

- Current HEAD contains no confirmed real tenant operational documents.
- Development fixtures (`seed/*.csv`) are fictional (example.com identities).
- `scripts/check-sensitive-files.mjs` now covers operational document classes
  (PDF/DOCX/DOC/ODT/PPTX/RTF, CSV/TSV outside fixtures, spreadsheets, archives,
  secret material) and passes on the tracked tree while rejecting synthetic
  operational-document fixtures.
- This report exists and no remote history was rewritten automatically.
