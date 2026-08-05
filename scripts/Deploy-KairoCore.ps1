[CmdletBinding()]
param(
  [string]$EnvironmentFile = '.env.core',
  [switch]$WithTunnel
)

$ErrorActionPreference = 'Stop'
$compose = @('--env-file', $EnvironmentFile, '-f', 'docker-compose.core.yml')

Write-Host '1/5 Creating the mandatory encrypted pre-deployment backup...'
& "$PSScriptRoot\Backup-Kairo.ps1" -EnvironmentFile $EnvironmentFile
if ($LASTEXITCODE -ne 0) { throw 'Deployment stopped because the pre-deployment backup failed.' }

Write-Host '2/5 Building core services without applying migrations automatically...'
& docker compose @compose build api worker scheduler web
if ($LASTEXITCODE -ne 0) { throw 'Core image build failed.' }

Write-Host '3/5 Applying database migrations only after the verified backup...'
& docker compose @compose run --rm --no-deps api alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Migration failed. The verified backup is available for isolated recovery.' }

Write-Host '4/5 Starting the core services...'
& docker compose @compose up -d postgres redis minio api worker scheduler web
if ($LASTEXITCODE -ne 0) { throw 'Core service start failed.' }
if ($WithTunnel) {
  & docker compose @compose --profile tunnel up -d cloudflared
  if ($LASTEXITCODE -ne 0) { throw 'Cloudflare tunnel start failed.' }
}

Write-Host '5/5 Deployment completed. Verify https://app.combissportverein.org/health.'
