[CmdletBinding()]
param([string]$DemoEnvFile = '.env.quick-demo')

$ErrorActionPreference = 'Stop'

function Remove-TunnelContainer {
  param([string]$Name)

  $existing = & docker ps -aq --filter "name=^/$Name$"
  if ($LASTEXITCODE -eq 0 -and $existing) {
    & docker rm -f $Name | Out-Null
  }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw 'Docker CLI was not found. Install and start Docker Desktop before running this script.'
}

Remove-TunnelContainer -Name 'kairo-quick-demo-api'
Remove-TunnelContainer -Name 'kairo-quick-demo-web'
Remove-Item -LiteralPath (Join-Path (Get-Location) $DemoEnvFile) -Force -ErrorAction SilentlyContinue
Remove-Item Env:\KAIRO_ENV_FILE -ErrorAction SilentlyContinue

& docker compose up -d --force-recreate api worker web
if ($LASTEXITCODE -ne 0) {
  throw 'The tunnels were stopped, but the standard local services could not be restored. Run: docker compose up -d --force-recreate api worker web'
}

Write-Output 'Kairo Quick Demo stopped. The standard local API, worker, and web services were restored.'
