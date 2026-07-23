[CmdletBinding()]
param(
  [string]$EnvFile = '.env.production.local'
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $EnvFile)) {
  throw "Production environment file not found: $EnvFile"
}

& .\scripts\pilot_acceptance_preflight.ps1 -EnvFile $EnvFile

& docker compose --env-file $EnvFile -f docker-compose.yml -f docker-compose.prod.yml --profile tunnel up -d --build
if ($LASTEXITCODE -ne 0) {
  throw 'Production Compose startup failed. Inspect it with: docker compose --env-file .env.production.local logs'
}

Write-Output 'Production stack started. Verify it through https://app.combissportverein.org.'
