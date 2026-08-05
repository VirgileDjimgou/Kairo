[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$ArchiveName,
  [switch]$IUnderstandThisReplacesData,
  [string]$EnvironmentFile = '.env.core'
)

$ErrorActionPreference = 'Stop'
if (-not $IUnderstandThisReplacesData) {
  throw 'Refusing restore. Re-run with -IUnderstandThisReplacesData after board approval. This replaces the running database.'
}

$archive = "/var/backups/$ArchiveName"
$manifest = "$archive.manifest.json"
$extractName = "restore-$([guid]::NewGuid().ToString('N'))"
$extract = "/var/backups/$extractName"
$compose = @('--env-file', $EnvironmentFile, '-f', 'docker-compose.core.yml')

& docker compose @compose exec -T worker python -m app.modules.backup.cli verify $archive $manifest
if ($LASTEXITCODE -ne 0) { throw 'Archive verification failed. No platform data was changed.' }
& docker compose @compose exec -T worker python -m app.modules.backup.cli extract $archive $manifest $extract
if ($LASTEXITCODE -ne 0) { throw 'Archive extraction failed. No platform data was changed.' }

$hostExtract = Join-Path (Join-Path (Get-Location) 'backups') $extractName
$sql = Join-Path $hostExtract 'postgres.sql'
if (-not (Test-Path $sql)) { throw 'Recovered PostgreSQL dump is missing.' }

Write-Host 'Entering maintenance mode and restoring PostgreSQL...'
& docker compose @compose stop api worker scheduler web
$postgres = (& docker compose @compose ps -q postgres).Trim()
if (-not $postgres) { throw 'PostgreSQL container is not available.' }
try {
  & docker cp $sql "${postgres}:/tmp/kairo-restore.sql"
  & docker exec $postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres -f /tmp/kairo-restore.sql'
  if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL restore failed. Keep maintenance mode active and investigate the archive.' }
  & docker compose @compose run --rm --no-deps worker python -m app.modules.backup.cli replace-documents "$extract/documents"
  if ($LASTEXITCODE -ne 0) { throw 'Document restore failed. The database was restored; documents require follow-up.' }
} finally {
  & docker compose @compose up -d api worker scheduler web
}
Write-Host 'Restore completed. Run the production smoke check. For an incident response, rotate JWT/session secrets after the restore to invalidate sessions that existed before the snapshot.'
