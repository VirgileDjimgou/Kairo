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
    reason: 'backup and dump files must never be versioned',
    pattern: /(^|\/)(backups?|dumps?|exports?)(\/|$)|\.(bak|backup|dump)$/i,
  },
  {
    reason: 'spreadsheet workbooks can contain member or financial data',
    pattern: /\.(xlsx|xls|ods)$/i,
  },
  {
    reason: 'financial or member data exports must be kept out of Git',
    pattern: /(?:contribution|cotisation|payment|paiement|financial|finance|adherent|member).+\.(csv|tsv|json)$/i,
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
