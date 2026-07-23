[CmdletBinding()]
param(
  [string]$EnvFile = '.env.production.local'
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

if (-not (Test-Path -LiteralPath $EnvFile)) {
  throw "Production environment file not found: $EnvFile"
}
if (docker ps --format '{{.Names}}' | Select-String -Quiet '^kairo-quick-demo-(api|web)$') {
  throw 'Stop the Quick Tunnel before rotating production database credentials.'
}

$postgresUser = Get-EnvironmentSetting -Path $EnvFile -Name 'POSTGRES_USER'
$postgresPassword = Get-EnvironmentSetting -Path $EnvFile -Name 'POSTGRES_PASSWORD'
$postgresDatabase = Get-EnvironmentSetting -Path $EnvFile -Name 'POSTGRES_DB'
if ($postgresUser -notmatch '^[A-Za-z_][A-Za-z0-9_]{0,62}$') {
  throw 'POSTGRES_USER contains unsupported characters.'
}
if ($postgresPassword -notmatch '^[A-Za-z0-9_-]{40,}$') {
  throw 'POSTGRES_PASSWORD must be the generated URL-safe production secret.'
}

$backupDirectory = Join-Path (Get-Location) 'backups'
New-Item -ItemType Directory -Force -Path $backupDirectory | Out-Null
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupPath = Join-Path $backupDirectory "kairo-before-production-password-rotation-$timestamp.sql"

Write-Output 'Creating a local PostgreSQL backup before credential rotation...'
& docker compose exec -T postgres pg_dump --username $postgresUser $postgresDatabase > $backupPath
if ($LASTEXITCODE -ne 0) {
  Remove-Item -LiteralPath $backupPath -Force -ErrorAction SilentlyContinue
  throw 'PostgreSQL backup failed. Production credentials were not changed.'
}

Write-Output 'Rotating the PostgreSQL password without printing it...'
& docker compose exec -T postgres psql --username $postgresUser --dbname postgres --set ON_ERROR_STOP=1 `
  --command "ALTER ROLE $postgresUser PASSWORD '$postgresPassword';" *> $null
if ($LASTEXITCODE -ne 0) {
  throw "PostgreSQL password rotation failed. Restore from $backupPath if required."
}

Write-Output "PostgreSQL credentials rotated. Backup retained at: $backupPath"
