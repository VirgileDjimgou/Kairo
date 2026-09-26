<#
.SYNOPSIS
  Prints the exact git-filter-repo commands required to purge the historical
  exposures documented in docs/security/HISTORY_EXPOSURE_REPORT.md.

.DESCRIPTION
  HUMAN REQUIRED. This script NEVER executes history rewriting, NEVER pushes and
  NEVER touches remotes. It only prints the remediation plan and verifies the
  local prerequisites. Remote history rewriting is destructive and externally
  visible; it must be run deliberately by the repository owner on a fresh clone
  after the JWT secret has been rotated.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

Write-Host '=== HUMAN REQUIRED: git history remediation plan ===' -ForegroundColor Yellow
Write-Host @'

Preconditions (in this order):
  1. ROTATE the exposed JWT secret on every deployment that used the committed
     value (see docs/security/HISTORY_EXPOSURE_REPORT.md, section A).
  2. Back up the repository: create a bare mirror clone.
  3. Install git-filter-repo (https://github.com/newren/git-filter-repo).
  4. Run the commands below on a FRESH clone, never on your daily working tree.
  5. Coordinate with every collaborator: after the rewrite all clones must
     re-clone. The subsequent push is a force push and requires approval.

'@

Write-Host '--- Step 1: mirror backup ---' -ForegroundColor Cyan
Write-Host 'git clone --mirror git@github.com:VirgileDjimgou/Kairo.git kairo-history-backup.git'

Write-Host ''
Write-Host '--- Step 2: fresh clone to rewrite ---' -ForegroundColor Cyan
Write-Host 'git clone git@github.com:VirgileDjimgou/Kairo.git kairo-history-fix'
Write-Host 'cd kairo-history-fix'

Write-Host ''
Write-Host '--- Step 3: remove real association documents and artifacts ---' -ForegroundColor Cyan
Write-Host 'git filter-repo --path "Combis Sport Verein" --invert-paths'
Write-Host 'git filter-repo --path services/api/tmp/pdfs/finance-report-preview.pdf --invert-paths'
Write-Host 'git filter-repo --path .vscode/PythonImportHelper-v2-Completion.json --invert-paths'

Write-Host ''
Write-Host '--- Step 4: purge the historical JWT secret value ---' -ForegroundColor Cyan
Write-Host '# The secret literal is deliberately NOT printed by this script and is not'
Write-Host '# stored anywhere in the repository. Extract it once from the exposed commit:'
Write-Host 'git show 2f03643f:docker-compose.prod.yml | findstr JWT_SECRET_KEY'
Write-Host '# then substitute the value below:'
Write-Host 'git filter-repo --replace-text <(printf "%s==>REMOVED_SECRET\n" "<EXPOSED_VALUE_FROM_COMMIT_2f03643f>")'

Write-Host ''
Write-Host '--- Step 5: verify before any push ---' -ForegroundColor Cyan
Write-Host 'git log --all -- "Combis Sport Verein"        # expect empty'
Write-Host 'git log --all --grep "VPiLJSFr"                # expect empty'
Write-Host 'docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest detect --source=/repo --no-banner'

Write-Host ''
Write-Host '--- Step 6: publish (REQUIRES EXPLICIT APPROVAL) ---' -ForegroundColor Cyan
Write-Host 'git push --force --mirror origin'
Write-Host '# then ask GitHub support to purge cached blobs / secret scanning references'

Write-Host ''
Write-Host 'This script performed no changes. Review, approve and execute manually.' -ForegroundColor Yellow
