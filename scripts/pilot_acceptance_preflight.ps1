param(
  [string]$EnvFile = '.env',
  [switch]$AllowIncomplete
)

if (-not (Test-Path -LiteralPath $EnvFile)) {
  throw "Environment file not found: $EnvFile"
}

$settings = @{}
Get-Content -LiteralPath $EnvFile | ForEach-Object {
  if ($_ -match '^\s*([^#=]+)=(.*)$') {
    $settings[$matches[1].Trim()] = $matches[2].Trim()
  }
}

function Has-NonPlaceholderValue([string]$Key) {
  $value = $settings[$Key]
  return -not [string]::IsNullOrWhiteSpace($value) -and
    -not $value.StartsWith('change-me') -and
    $value -ne 'orgmind_dev_password'
}

$checks = @(
  @{ Label = 'APP_ENV is production'; Passed = $settings['APP_ENV'] -eq 'production' },
  @{ Label = 'APP_DEBUG is false'; Passed = $settings['APP_DEBUG'] -eq 'false' },
  @{ Label = 'JWT secret is non-placeholder'; Passed = Has-NonPlaceholderValue 'JWT_SECRET_KEY' },
  @{ Label = 'PostgreSQL password is non-placeholder'; Passed = Has-NonPlaceholderValue 'POSTGRES_PASSWORD' },
  @{ Label = 'MinIO password is non-placeholder'; Passed = Has-NonPlaceholderValue 'MINIO_ROOT_PASSWORD' },
  @{ Label = 'Public base URL uses HTTPS'; Passed = $settings['APP_BASE_URL'] -like 'https://*' },
  @{ Label = 'CORS configuration exists'; Passed = -not [string]::IsNullOrWhiteSpace($settings['CORS_ORIGINS']) },
  @{ Label = 'Cloudflare tunnel token exists'; Passed = Has-NonPlaceholderValue 'CLOUDFLARE_TUNNEL_TOKEN' }
)

$passed = 0
$failed = 0

Write-Output '--- Kairo Operational Pilot Preflight ---'
Write-Output "Environment file: $EnvFile"
Write-Output ''

foreach ($check in $checks) {
  if ($check.Passed) {
    Write-Output "  PASS  $($check.Label)"
    $passed++
  } else {
    Write-Output "  FAIL  $($check.Label)"
    $failed++
  }
}

Write-Output ''
Write-Output "--- Results: $passed passed, $failed failed ---"

if ($failed -gt 0 -and -not $AllowIncomplete) {
  throw 'Operational pilot preflight failed.'
}
