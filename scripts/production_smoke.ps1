param(
  [string]$BaseUrl = 'http://localhost'
)

if ($BaseUrl -eq 'http://localhost' -and $env:APP_BASE_URL) {
  $BaseUrl = $env:APP_BASE_URL
}

$BaseUrl = $BaseUrl.TrimEnd('/')
$temporaryBody = Join-Path $env:TEMP "kairo-production-smoke-$PID.txt"
$checks = @(
  @{ Label = 'Health endpoint'; Path = '/health'; ExpectedStatus = '200'; ExpectedBody = '"status"' },
  @{ Label = 'Metrics endpoint'; Path = '/metrics'; ExpectedStatus = '200'; ExpectedBody = '# HELP' },
  @{ Label = 'Root page'; Path = '/'; ExpectedStatus = '200'; ExpectedBody = '' },
  @{ Label = 'API docs blocked'; Path = '/docs'; ExpectedStatus = '404'; ExpectedBody = '' },
  @{ Label = 'API redoc blocked'; Path = '/redoc'; ExpectedStatus = '404'; ExpectedBody = '' },
  @{ Label = 'OpenAPI blocked'; Path = '/openapi.json'; ExpectedStatus = '404'; ExpectedBody = '' }
)

$passed = 0
$failed = 0

Write-Output '--- Kairo Production Smoke Check ---'
Write-Output "Target: $BaseUrl"
Write-Output ''

try {
  foreach ($check in $checks) {
    $status = & curl.exe -sS -o $temporaryBody -w '%{http_code}' "$BaseUrl$($check.Path)"
    $body = if (Test-Path $temporaryBody) { Get-Content $temporaryBody -Raw } else { '' }

    if ($status -ne $check.ExpectedStatus) {
      Write-Output "  FAIL  $($check.Label) - expected HTTP $($check.ExpectedStatus), got $status"
      $failed++
      continue
    }

    if ($check.ExpectedBody -and -not $body.Contains($check.ExpectedBody)) {
      Write-Output "  FAIL  $($check.Label) - body missing '$($check.ExpectedBody)'"
      $failed++
      continue
    }

    Write-Output "  PASS  $($check.Label)"
    $passed++
  }
} finally {
  Remove-Item -LiteralPath $temporaryBody -Force -ErrorAction SilentlyContinue
}

Write-Output ''
Write-Output "--- Results: $passed passed, $failed failed ---"

if ($failed -gt 0) {
  exit 1
}
