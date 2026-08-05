# Encrypted recovery runbook (Windows + Docker core)

## Scope and safety boundary

Kairo recovery archives contain the authoritative PostgreSQL data: member profiles,
password hashes, roles, contributions, donations, sanctions, expenses, audit history,
notification state, and all MinIO documents. Redis is a rebuildable queue/cache and
Qdrant is rebuilt from restored documents; neither is a source of record.

Archives are encrypted with Fernet, carry a SHA-256 digest, and use a signed JSON
manifest. Archives are never downloadable through the browser. The recovery centre
only shows their status and accepts an encrypted upload for verification/staging. The
host operator performs an actual restore in maintenance mode.

Only the president, secretary general, and emergency principal administrator may use
the centre. Every run is tenant-audited and raw recovery data remains host-only.

## One-time production configuration

Set non-placeholder private `.env.core` values:

```dotenv
BACKUP_ENABLED=true
BACKUP_AUTO_ENABLED=true
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION_KEY=<a Fernet key>
BACKUP_MANIFEST_SIGNING_KEY=<a distinct long random secret>
BACKUP_PITR_ENABLED=true
```

For an encrypted off-site copy, configure an association-owned S3-compatible bucket:

```dotenv
BACKUP_EXTERNAL_S3_ENDPOINT=https://s3.example.org
BACKUP_EXTERNAL_S3_BUCKET=kairo-recovery
BACKUP_EXTERNAL_S3_ACCESS_KEY=...
BACKUP_EXTERNAL_S3_SECRET_KEY=...
```

The archive is encrypted before upload. Never use a public bucket. PostgreSQL archives
WAL files to its private Docker volume. A normal product restore uses a verified logical
snapshot; physical point-in-time recovery must be performed on an isolated host by a
PostgreSQL operator, never from the browser.

## Everyday operation

The scheduler requests one encrypted archive per day. The Recovery Centre records its
timestamp, integrity status, and SHA-256 fingerprint. To create a manual archive:

```powershell
.\scripts\Backup-Kairo.ps1
```

Use this pre-migration deployment procedure:

```powershell
.\scripts\Deploy-KairoCore.ps1 -WithTunnel
```

It stops if its pre-deployment archive fails verification, then builds, migrates, and
restarts core services. Critical CSV imports and record deletions are also blocked
server-side unless a pre-operation backup succeeds.

## Non-destructive recovery exercise

Run this after the first backup and at least quarterly:

```powershell
.\scripts\Test-KairoRecoveryDrill.ps1 -ArchiveName kairo-recovery-....enc
```

The command verifies the signature, SHA-256, and encryption; extracts to an isolated
workspace; restores into a disposable PostgreSQL container; and checks members,
contributions, sanctions, and expenses. It never changes production data.

To exercise corruption handling, alter a copy of an archive and run this drill. It must
fail during verification, before extraction or a database command.

## Disaster recovery (board-authorised)

1. Put the association in maintenance mode and select a verified archive.
2. Run the isolated recovery exercise first.
3. Obtain president or secretary-general approval of the data-loss window.
4. Restore with explicit confirmation:

   ```powershell
   .\scripts\Restore-KairoBackup.ps1 -ArchiveName kairo-recovery-....enc -IUnderstandThisReplacesData
   ```

5. The script restores PostgreSQL, replaces the document bucket (including objects
   created after the snapshot), and starts services again.
6. Rotate JWT/session secrets after an incident restore, force fresh sign-in, and run
   authenticated role, tenant-isolation, and finance smoke checks.

Never restore an unsigned, unverified, or tenant-unknown archive. Keep recovery keys
separate from the Docker host and archive destination.
