[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$FlutterArguments
)

$candidates = @(
    @(
        (Get-Command flutter.bat -ErrorAction SilentlyContinue).Source,
        (Get-Command flutter -ErrorAction SilentlyContinue).Source,
        (Join-Path $env:LOCALAPPDATA 'KairoTools\flutter\bin\flutter.bat')
    ) | Where-Object { $_ -and (Test-Path $_) }
)

if ($candidates.Count -eq 0) {
    throw 'Flutter SDK not found. Install Flutter or place it under %LOCALAPPDATA%\KairoTools\flutter.'
}

& $candidates[0] @FlutterArguments
exit $LASTEXITCODE
