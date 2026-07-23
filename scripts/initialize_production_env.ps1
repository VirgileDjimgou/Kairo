[CmdletBinding()]
param(
  [string]$OutputFile = '.env.production.local',
  [string]$AppHostname = 'app.combissportverein.org'
)

$ErrorActionPreference = 'Stop'

function New-UrlSafeSecret([int]$ByteCount) {
  $bytes = New-Object byte[] $ByteCount
  [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
  return [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

if (Test-Path -LiteralPath $OutputFile) {
  throw "Refusing to overwrite existing production environment file: $OutputFile"
}

if ($AppHostname -notmatch '^[a-z0-9.-]+$') {
  throw 'AppHostname must be a lowercase hostname without a protocol or path.'
}

$template = Get-Content -LiteralPath '.env.production.example' -Raw
$jwtSecret = New-UrlSafeSecret 48
$postgresPassword = New-UrlSafeSecret 32
$minioPassword = New-UrlSafeSecret 32
$corsOrigins = 'CORS_ORIGINS=["https://{0}"]' -f $AppHostname
$template = $template.Replace('APP_BASE_URL=http://localhost', "APP_BASE_URL=https://$AppHostname")
$template = $template.Replace('API_BASE_URL=http://localhost/api/v1', 'API_BASE_URL=/api/v1')
$template = $template.Replace('CORS_ORIGINS=["http://localhost"]', $corsOrigins)
$template = $template.Replace('JWT_SECRET_KEY=change-me-to-a-long-random-string', "JWT_SECRET_KEY=$jwtSecret")
$template = $template.Replace('POSTGRES_PASSWORD=change-me-to-a-strong-password', "POSTGRES_PASSWORD=$postgresPassword")
$template = $template.Replace('postgresql+psycopg://orgmind:change-me-to-a-strong-password@postgres:5432/orgmind', "postgresql+psycopg://orgmind:$postgresPassword@postgres:5432/orgmind")
$template = $template.Replace('MINIO_ROOT_PASSWORD=change-me-to-a-strong-password', "MINIO_ROOT_PASSWORD=$minioPassword")
$template = "KAIRO_ENV_FILE=$OutputFile`r`n$template"

$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText([System.IO.Path]::GetFullPath($OutputFile), $template, $utf8WithoutBom)

Write-Output "Created $OutputFile with generated JWT, PostgreSQL, and MinIO secrets."
Write-Output 'Set CLOUDFLARE_TUNNEL_TOKEN locally, then run the pilot preflight. Secret values were not printed.'
