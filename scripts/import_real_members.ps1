[CmdletBinding()]
param(
  [string]$WorkbookPath = '..\ImportExcel\Année 2026.xlsx',
  [string]$TenantSlug = 'demo',
  [int]$Year = 2026
)

$ErrorActionPreference = 'Stop'

function Get-EnvironmentSetting {
  param([string]$Path, [string]$Name)

  $match = Select-String -LiteralPath $Path -Pattern "^$([regex]::Escape($Name))=(.*)$" | Select-Object -First 1
  if (-not $match) {
    throw "Missing $Name in $Path"
  }
  return $match.Matches[0].Groups[1].Value.Trim()
}

if (-not (Test-Path -LiteralPath $WorkbookPath)) {
  throw "Workbook not found: $WorkbookPath"
}
if (docker ps --format '{{.Names}}' | Select-String -Quiet '^kairo-quick-demo-(api|web)$') {
  throw 'Stop the Quick Tunnel before importing real member data.'
}

$privateDirectory = Join-Path (Get-Location) 'services\api\.private\member-imports'
New-Item -ItemType Directory -Force -Path $privateDirectory | Out-Null
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupPath = Join-Path $privateDirectory "before-member-import-$timestamp.sql"
$credentialsRelativePath = ".private/member-imports/member-credentials-$timestamp.csv"
$credentialsPath = Join-Path (Get-Location) "services\api\$credentialsRelativePath"
$workbookContainerPath = '/tmp/kairo-member-import.xlsx'
$postgresUser = Get-EnvironmentSetting -Path '.env' -Name 'POSTGRES_USER'
$postgresDatabase = Get-EnvironmentSetting -Path '.env' -Name 'POSTGRES_DB'

Write-Output 'Creating a private PostgreSQL backup before replacing ordinary members...'
& docker compose exec -T postgres pg_dump --username $postgresUser $postgresDatabase > $backupPath
if ($LASTEXITCODE -ne 0) {
  Remove-Item -LiteralPath $backupPath -Force -ErrorAction SilentlyContinue
  throw 'Database backup failed. The import was not started.'
}

$apiContainer = (& docker compose ps -q api).Trim()
if (-not $apiContainer) {
  throw 'The API container is not running.'
}
& docker cp $WorkbookPath "${apiContainer}:$workbookContainerPath"
if ($LASTEXITCODE -ne 0) {
  throw 'Could not copy the workbook into the API container.'
}

Write-Output 'Validating the workbook...'
& docker compose exec -T api python -m app.db.import_members_workbook `
  --workbook $workbookContainerPath `
  --credentials-output "/app/$credentialsRelativePath" `
  --tenant-slug $TenantSlug `
  --year $Year
if ($LASTEXITCODE -ne 0) {
  throw 'Workbook validation failed. No member data was changed.'
}

Write-Output 'Replacing ordinary members and their contributions in one transaction...'
& docker compose exec -T api python -m app.db.import_members_workbook `
  --workbook $workbookContainerPath `
  --credentials-output "/app/$credentialsRelativePath" `
  --tenant-slug $TenantSlug `
  --year $Year `
  --execute
if ($LASTEXITCODE -ne 0) {
  throw "Import failed. Restore the private backup if necessary: $backupPath"
}

Write-Output "Private database backup: $backupPath"
Write-Output "Private credentials file: $credentialsPath"
