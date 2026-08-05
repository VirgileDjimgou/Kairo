[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ArchiveName,
  [string]$EnvironmentFile = '.env.core'
)

$ErrorActionPreference = 'Stop'
$archive = "/var/backups/$ArchiveName"
$manifest = "$archive.manifest.json"
$extract = "/var/backups/restore-drill-$([guid]::NewGuid().ToString('N'))"
$compose = @('--env-file', $EnvironmentFile, '-f', 'docker-compose.core.yml')

Write-Host '1/3 Verifying the encrypted archive and signed manifest...'
& docker compose @compose exec -T worker python -m app.modules.backup.cli verify $archive $manifest
if ($LASTEXITCODE -ne 0) { throw 'Archive integrity verification failed.' }

Write-Host '2/3 Extracting into an isolated recovery workspace...'
& docker compose @compose exec -T worker python -m app.modules.backup.cli extract $archive $manifest $extract
if ($LASTEXITCODE -ne 0) { throw 'Archive extraction failed.' }

$hostExtract = Join-Path (Join-Path (Get-Location) 'backups') ([IO.Path]::GetFileName($extract))
if (-not (Test-Path (Join-Path $hostExtract 'postgres.sql'))) { throw 'The restored PostgreSQL payload is missing.' }

$container = "kairo-recovery-drill-$([guid]::NewGuid().ToString('N').Substring(0,8))"
try {
  Write-Host '3/3 Restoring PostgreSQL to an isolated disposable container...'
  & docker run -d --rm --name $container -e POSTGRES_PASSWORD=recovery -e POSTGRES_USER=recovery -e POSTGRES_DB=recovery postgres:16-alpine | Out-Null
  Start-Sleep -Seconds 5
  & docker cp (Join-Path $hostExtract 'postgres.sql') "${container}:/tmp/postgres.sql"
  & docker exec $container psql -v ON_ERROR_STOP=1 -U recovery -d postgres -f /tmp/postgres.sql
  if ($LASTEXITCODE -ne 0) { throw 'Isolated PostgreSQL restore failed.' }
  & docker exec $container psql -U recovery -d orgmind -tAc "SELECT 'members=' || COUNT(*) FROM membership_profiles UNION ALL SELECT 'contributions=' || COUNT(*) FROM contribution_records UNION ALL SELECT 'sanctions=' || COUNT(*) FROM disciplinary_records UNION ALL SELECT 'expenses=' || COUNT(*) FROM expense_records;"
  if ($LASTEXITCODE -ne 0) { throw 'Restored database verification query failed.' }
  Write-Host 'Recovery drill PASSED: archive integrity, extraction and isolated PostgreSQL restoration succeeded with member, contribution, sanction and expense data.'
} finally {
  & docker rm -f $container 2>$null | Out-Null
}
