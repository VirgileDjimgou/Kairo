[CmdletBinding()]
param(
  [string]$EnvFile = '.env',
  [string]$DemoEnvFile = '.env.quick-demo',
  [string]$ConfigFile = 'infra/cloudflare/quick-demo.psd1',
  [int]$StartupTimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'

function Set-EnvironmentSetting {
  param([string]$Content, [string]$Name, [string]$Value)

  $pattern = "(?m)^$([regex]::Escape($Name))=.*$"
  $replacement = "$Name=$Value"
  if ($Content -match $pattern) {
    return [regex]::Replace($Content, $pattern, $replacement)
  }

  return "$Content`r`n$replacement`r`n"
}

function Get-EnvironmentSetting {
  param([string]$Content, [string]$Name)

  $match = [regex]::Match($Content, "(?m)^$([regex]::Escape($Name))=(.*)$")
  if ($match.Success) {
    return $match.Groups[1].Value.Trim()
  }

  return ''
}

function Get-CorsOrigins {
  param([string]$Value)

  if ([string]::IsNullOrWhiteSpace($Value)) {
    return @()
  }

  if ($Value.TrimStart().StartsWith('[')) {
    try {
      return @($Value | ConvertFrom-Json)
    } catch {
      throw 'CORS_ORIGINS must be a comma-separated origin list or a JSON array.'
    }
  }

  return @($Value.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

function Write-EnvironmentFile {
  param([string]$Path, [string]$Content)

  $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText([System.IO.Path]::GetFullPath($Path), $Content, $utf8WithoutBom)
}

function Remove-TunnelContainer {
  param([string]$Name)

  $existing = & docker ps -aq --filter "name=^/$Name$"
  if ($LASTEXITCODE -eq 0 -and $existing) {
    & docker rm -f $Name | Out-Null
  }
}

function Start-QuickTunnel {
  param([string]$Name, [int]$Port, [int]$TimeoutSeconds)

  Remove-TunnelContainer -Name $Name
  & docker run -d --rm --name $Name cloudflare/cloudflared:latest tunnel --url "http://host.docker.internal:$Port" | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "Could not start the $Name container. Ensure Docker Desktop is running."
  }

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    $logs = & docker logs $Name 2>&1
    $urlMatch = [regex]::Match(($logs -join "`n"), 'https://[a-z0-9-]+\.trycloudflare\.com')
    if ($urlMatch.Success) {
      return $urlMatch.Value
    }
    Start-Sleep -Seconds 2
  } while ((Get-Date) -lt $deadline)

  throw "Timed out waiting for the $Name URL. Inspect it with: docker logs $Name"
}

function Wait-ForApi {
  param([int]$TimeoutSeconds)

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    & curl.exe -fsS http://localhost:8000/health *> $null
    if ($LASTEXITCODE -eq 0) {
      return
    }
    Start-Sleep -Seconds 3
  } while ((Get-Date) -lt $deadline)

  throw 'Timed out waiting for Kairo API health. Inspect it with: docker compose logs api'
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
  throw "Environment file not found: $EnvFile"
}
if (-not (Test-Path -LiteralPath $ConfigFile)) {
  throw "Quick Demo configuration file not found: $ConfigFile"
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  throw 'Docker CLI was not found. Install and start Docker Desktop before running this script.'
}

$quickDemoConfig = Import-PowerShellDataFile -LiteralPath $ConfigFile
$instancePrefix = [string]$quickDemoConfig.InstanceLabelPrefix
if ($instancePrefix -notmatch '^[a-z0-9-]{1,40}$') {
  throw 'InstanceLabelPrefix must contain only lowercase letters, digits, and hyphens.'
}
$instanceLabel = '{0}-{1:D4}' -f $instancePrefix, (Get-Random -Minimum 0 -Maximum 10000)
$sourceEnv = Get-Content -LiteralPath $EnvFile -Raw
$demoEnvPath = Join-Path (Get-Location) $DemoEnvFile
$apiTunnelName = 'kairo-quick-demo-api'
$webTunnelName = 'kairo-quick-demo-web'

try {
  Remove-TunnelContainer -Name $apiTunnelName
  Remove-TunnelContainer -Name $webTunnelName
  Write-EnvironmentFile -Path $demoEnvPath -Content $sourceEnv
  $env:KAIRO_ENV_FILE = $DemoEnvFile

  Write-Output 'Starting the local Kairo stack for the temporary demo...'
  & docker compose up -d --build
  if ($LASTEXITCODE -ne 0) {
    throw 'Kairo Compose startup failed. Inspect it with: docker compose logs'
  }

  Wait-ForApi -TimeoutSeconds $StartupTimeoutSeconds
  $apiUrl = Start-QuickTunnel -Name $apiTunnelName -Port 8000 -TimeoutSeconds $StartupTimeoutSeconds

  $demoEnv = Set-EnvironmentSetting -Content $sourceEnv -Name 'VITE_API_BASE_URL' -Value "$apiUrl/api/v1"
  Write-EnvironmentFile -Path $demoEnvPath -Content $demoEnv
  & docker compose up -d --force-recreate web
  if ($LASTEXITCODE -ne 0) {
    throw 'Could not restart the web service with the temporary API URL.'
  }

  $webUrl = Start-QuickTunnel -Name $webTunnelName -Port 5173 -TimeoutSeconds $StartupTimeoutSeconds
  $corsOrigins = Get-CorsOrigins -Value (Get-EnvironmentSetting -Content $sourceEnv -Name 'CORS_ORIGINS')
  $demoCorsOrigins = @($corsOrigins + $webUrl | Select-Object -Unique | ConvertTo-Json -Compress)
  $demoEnv = Set-EnvironmentSetting -Content $demoEnv -Name 'CORS_ORIGINS' -Value $demoCorsOrigins
  $demoEnv = Set-EnvironmentSetting -Content $demoEnv -Name 'APP_BASE_URL' -Value $webUrl
  Write-EnvironmentFile -Path $demoEnvPath -Content $demoEnv
  & docker compose up -d --force-recreate api
  if ($LASTEXITCODE -ne 0) {
    throw 'Could not restart the API service with the temporary CORS origin.'
  }

  Wait-ForApi -TimeoutSeconds $StartupTimeoutSeconds
  Write-Output ''
  Write-Output '--- Kairo Quick Demo Ready ---'
  Write-Output "Local session label: $instanceLabel"
  Write-Output "Share this temporary application URL: $webUrl"
  Write-Output 'Only share the application URL. Do not share tunnel logs, .env files, or internal service URLs.'
  Write-Output 'To stop the demo and return to the standard local environment, run:'
  Write-Output '  .\scripts\stop_quick_demo.ps1'
} catch {
  Remove-TunnelContainer -Name $apiTunnelName
  Remove-TunnelContainer -Name $webTunnelName
  Remove-Item -LiteralPath $demoEnvPath -Force -ErrorAction SilentlyContinue
  Remove-Item Env:\KAIRO_ENV_FILE -ErrorAction SilentlyContinue
  & docker compose up -d --force-recreate api worker web *> $null
  throw
}
