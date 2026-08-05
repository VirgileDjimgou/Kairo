[CmdletBinding()]
param(
  [string]$TenantSlug = '',
  [string]$EnvironmentFile = '.env.core'
)

$ErrorActionPreference = 'Stop'
$compose = @('--env-file', $EnvironmentFile, '-f', 'docker-compose.core.yml')
if (-not (Test-Path $EnvironmentFile)) { throw "Environment file not found: $EnvironmentFile" }

Write-Host 'Creating encrypted Kairo recovery archive...'
$arguments = @('compose') + $compose + @('exec', '-T', 'worker', 'python', '-m', 'app.modules.backup.cli', 'backup')
if ($TenantSlug) { $arguments += @('--tenant-slug', $TenantSlug) }
& docker @arguments
if ($LASTEXITCODE -ne 0) { throw 'The encrypted recovery backup failed.' }
Write-Host 'Backup complete. The archive and its signed manifest are in .\backups and, when configured, in the external S3 destination.'
