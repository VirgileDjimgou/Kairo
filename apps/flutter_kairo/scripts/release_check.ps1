param(
    [ValidateSet('staging', 'production')]
    [string]$Flavor = 'staging',
    [Parameter(Mandatory = $true)]
    [string]$ApiBaseUrl,
    [switch]$BuildAab,
    [switch]$ConfirmProduction
)

$ErrorActionPreference = 'Stop'

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$Step
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

if ($Flavor -eq 'production' -and -not $ConfirmProduction) {
    throw 'Production verification requires -ConfirmProduction. This command never deploys or promotes a release.'
}

$flutter = Join-Path $PSScriptRoot 'flutter.ps1'
$defines = @("--dart-define=KAIRO_FLAVOR=$Flavor", "--dart-define=KAIRO_API_BASE_URL=$ApiBaseUrl")
$flutterCommand = (Get-Command flutter.bat -ErrorAction SilentlyContinue).Source
if (-not $flutterCommand) {
    $flutterCommand = (Get-Command flutter -ErrorAction SilentlyContinue).Source
}
if (-not $flutterCommand) {
    $flutterCommand = Join-Path $env:LOCALAPPDATA 'KairoTools\flutter\bin\flutter.bat'
}
$dart = Join-Path (Split-Path -Parent $flutterCommand) 'dart.bat'
if (-not (Test-Path $dart)) {
    throw 'Dart SDK command not found. Install Flutter/Dart before running release checks.'
}

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    Invoke-Checked -FilePath $flutter -Arguments @('pub', 'get') -Step 'Dependency resolution'
    Invoke-Checked -FilePath $dart -Arguments @('format', '--set-exit-if-changed', 'lib', 'test') -Step 'Dart formatting verification'
    Invoke-Checked -FilePath $flutter -Arguments @('analyze') -Step 'Flutter analysis'
    Invoke-Checked -FilePath $flutter -Arguments @('test') -Step 'Flutter tests'
    Invoke-Checked -FilePath $flutter -Arguments (@('build', 'web', '--release') + $defines) -Step 'Flutter Web build'
    Invoke-Checked -FilePath $flutter -Arguments (@('build', 'apk', '--debug') + $defines) -Step 'Android debug APK build'

    if ($BuildAab) {
        Invoke-Checked -FilePath $flutter -Arguments (@('build', 'appbundle', '--release') + $defines) -Step 'Android signed app bundle build'
    }
} finally {
    Pop-Location
}

Write-Host "Release readiness checks completed for $Flavor."
