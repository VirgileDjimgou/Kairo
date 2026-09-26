import { execFileSync } from 'node:child_process';

const allowedFixtures = new Set([
  'seed/sample-members.csv',
  'seed/sample-contributions.csv',
]);

const forbiddenPatterns = [
  {
    reason: 'database files are local-only artifacts',
    pattern: /\.(sqlite|sqlite3|db)$/i,
  },
  {
    reason: 'backup and dump archives must never be versioned',
    pattern: /\.(bak|backup|dump|tar|tar\.gz|tgz|gz|7z|rar|zip)$/i,
  },
  {
    reason: 'operational archive staging directories are not source code',
    pattern: /(^|\/)(backups|dumps|backup-archives)(\/)/i,
  },
  {
    reason: 'spreadsheet workbooks can contain member or financial data',
    pattern: /\.(xlsx|xls|ods)$/i,
  },
  {
    reason: 'operational documents (statutes, minutes, sanctions, reports) belong in private tenant storage, not Git',
    pattern: /\.(pdf|docx|doc|odt|pptx|ppt|rtf)$/i,
  },
  {
    reason: 'tabular data exports must be kept out of Git (only the fictional seed fixtures are allowed)',
    pattern: /\.(csv|tsv)$/i,
  },
  {
    reason: 'financial or member data exports must be kept out of Git',
    pattern: /(?:contribution|cotisation|payment|paiement|financial|finance|adherent|member|bilan|sanzion|sanction|mitglied|beitrag).+\.(csv|tsv|json|xml)$/i,
  },
  {
    reason: 'secret-bearing environment files must never be versioned (documented *.example templates are allowed)',
    pattern: /(^|\/)\.env(?![^/]*\.example$)[^/]*$/,
  },
  {
    reason: 'secret-bearing key material must never be versioned',
    pattern: /(^|\/)[^/]*\.(pem|key|p12|pfx|jks)$/i,
  },
  {
    reason: 'service account or credential JSON must never be versioned',
    pattern: /(^|\/)[^/]*(?:service[-_]?account|credentials|secret)[^/]*\.json$/i,
  },
];

const trackedFiles = execFileSync('git', ['ls-files', '-z'], {
  encoding: 'utf8',
}).split('\0').filter(Boolean);

const violations = trackedFiles.filter((file) => (
  !allowedFixtures.has(file)
  && forbiddenPatterns.some(({ pattern }) => pattern.test(file))
));

if (violations.length > 0) {
  console.error('Sensitive-file policy violations:');
  for (const file of violations) {
    const policy = forbiddenPatterns.find(({ pattern }) => pattern.test(file));
    console.error(`- ${file}: ${policy.reason}`);
  }
  process.exit(1);
}

console.log(`Sensitive-file policy passed (${trackedFiles.length} tracked files checked).`);
