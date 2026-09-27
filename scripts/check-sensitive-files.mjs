import { execFileSync } from 'node:child_process';

const allowedFixtures = new Set([
  'seed/sample-members.csv',
  'seed/sample-contributions.csv',
]);

// Source trees legitimately contain JSON/XML catalogs whose names include
// domain words (for example apps/web/src/i18n/fr/membership.json). They are
// code, not operational data exports, so the data-export rule skips them while
// still rejecting exported data outside a source tree.
const sourceTreePatterns = [
  /^apps\/web\/src\//,
  /^apps\/flutter_kairo\/lib\//,
  /^services\/api\/app\//,
];

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
    skipSourceTrees: true,
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

function isViolation(file) {
  return forbiddenPatterns.some(({ pattern, skipSourceTrees }) => {
    if (!pattern.test(file)) return false;
    if (skipSourceTrees && sourceTreePatterns.some((source) => source.test(file))) return false;
    return true;
  });
}

const violations = trackedFiles.filter((file) => (
  !allowedFixtures.has(file)
  && isViolation(file)
));

if (violations.length > 0) {
  console.error('Sensitive-file policy violations:');
  for (const file of violations) {
    const policy = forbiddenPatterns.find(({ pattern, skipSourceTrees }) => (
      pattern.test(file)
      && !(skipSourceTrees && sourceTreePatterns.some((source) => source.test(file)))
    ));
    console.error(`- ${file}: ${policy.reason}`);
  }
  process.exit(1);
}

console.log(`Sensitive-file policy passed (${trackedFiles.length} tracked files checked).`);
