#!/usr/bin/env node
/**
 * Non-secret Firebase/Web Push diagnostics for Kairo operators.
 *
 * The doctor never sends anything unless --live is passed together with a
 * FIREBASE_TEST_TOKEN environment variable, and it never prints tokens, keys or
 * credential contents. It is intentionally not wired into CI.
 */
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const asJson = process.argv.includes('--json');
const live = process.argv.includes('--live');

const FIREBASE_ENV_KEYS = [
  'FIREBASE_MESSAGING_ENABLED',
  'FIREBASE_SERVICE_ACCOUNT_PATH',
  'FIREBASE_SERVICE_ACCOUNT_JSON',
  'GOOGLE_APPLICATION_CREDENTIALS',
  'FIREBASE_PROJECT_ID',
  'FCM_PROJECT_ID',
];

const WEB_PUSH_ENV_KEYS = [
  'WEB_PUSH_ENABLED',
  'WEB_PUSH_VAPID_PUBLIC_KEY',
  'WEB_PUSH_VAPID_PRIVATE_KEY',
  'WEB_PUSH_VAPID_SUBJECT',
];

const CANDIDATE_FILES = [
  'services/api/.private/firebase-admin.json',
  'services/api/.private/firebase-service-account.json',
  'apps/flutter_kairo/android/app/google-services.json',
];

function pythonCommand() {
  const windowsVenv = path.join(root, '.venv', 'Scripts', 'python.exe');
  if (existsSync(windowsVenv)) return windowsVenv;
  const unixVenv = path.join(root, '.venv', 'bin', 'python');
  if (existsSync(unixVenv)) return unixVenv;
  return 'python';
}

function credentialProjectId(relativePath) {
  try {
    const parsed = JSON.parse(readFileSync(path.join(root, relativePath), 'utf8'));
    if (typeof parsed.project_id === 'string') return parsed.project_id;
    if (parsed.project_info && typeof parsed.project_info.project_id === 'string') {
      return parsed.project_info.project_id;
    }
    return null;
  } catch {
    return null;
  }
}

function pythonImportCheck(moduleName) {
  const result = spawnSync(pythonCommand(), ['-c', `import ${moduleName}`], {
    encoding: 'utf8',
  });
  return result.status === 0;
}

function runLiveSmokeTest() {
  const token = process.env.FIREBASE_TEST_TOKEN;
  if (!token) {
    return { requested: true, sent: false, reason: 'missing_token' };
  }
  const credentialsPath = process.env.FIREBASE_SERVICE_ACCOUNT_PATH;
  if (!credentialsPath) {
    return { requested: true, sent: false, reason: 'missing_service_account_path' };
  }
  const script = [
    'import json, sys',
    'import firebase_admin',
    'from firebase_admin import credentials, messaging',
    'try:',
    '    if not firebase_admin._apps:',
    '        firebase_admin.initialize_app(credentials.Certificate(sys.argv[1]))',
    '    messaging.send(messaging.Message(token=sys.argv[2], notification=messaging.Notification(title="Kairo", body="Test de notification.")))',
    '    print(json.dumps({"sent": True}))',
    'except Exception as exc:',
    '    print(json.dumps({"sent": False, "error": type(exc).__name__}))',
  ].join('\n');
  const result = spawnSync(pythonCommand(), ['-c', script, credentialsPath, token], {
    encoding: 'utf8',
    env: { ...process.env },
  });
  try {
    return { requested: true, ...JSON.parse(result.stdout.trim()) };
  } catch {
    return { requested: true, sent: false, reason: 'smoke_test_failed' };
  }
}

const credentialFiles = CANDIDATE_FILES.map((relativePath) => {
  const absolute = path.join(root, relativePath);
  const present = existsSync(absolute);
  return {
    path: relativePath,
    present,
    project_id: present ? credentialProjectId(relativePath) : null,
  };
});

const firebaseEnv = Object.fromEntries(
  FIREBASE_ENV_KEYS.map((key) => [key, process.env[key] ? 'set' : 'unset']),
);
const webPushEnv = Object.fromEntries(
  WEB_PUSH_ENV_KEYS.map((key) => [key, process.env[key] ? 'set' : 'unset']),
);

const report = {
  firebase_env: firebaseEnv,
  web_push_env: webPushEnv,
  credential_files: credentialFiles,
  python_packages: {
    firebase_admin: pythonImportCheck('firebase_admin'),
    pywebpush: pythonImportCheck('pywebpush'),
  },
  web_push_configured: Boolean(
    process.env.WEB_PUSH_ENABLED === 'true' &&
      process.env.WEB_PUSH_VAPID_PUBLIC_KEY &&
      process.env.WEB_PUSH_VAPID_PRIVATE_KEY,
  ),
  firebase_configured: Boolean(
    (process.env.FIREBASE_MESSAGING_ENABLED === 'true' &&
      (process.env.FIREBASE_SERVICE_ACCOUNT_PATH || process.env.GOOGLE_APPLICATION_CREDENTIALS)) ||
      credentialFiles.some((file) => file.present),
  ),
  live: live
    ? runLiveSmokeTest()
    : { requested: false, sent: false, note: 'pass --live and FIREBASE_TEST_TOKEN to send one test push' },
};

if (asJson) {
  console.log(JSON.stringify(report, null, 2));
  process.exit(0);
}

const mark = (value) => (value ? 'OK' : 'MISSING');
console.log('Kairo notification doctor (no secrets are printed)');
console.log('');
console.log(`Web Push configured : ${mark(report.web_push_configured)}`);
console.log(`Firebase configured : ${mark(report.firebase_configured)}`);
console.log(`python firebase_admin: ${mark(report.python_packages.firebase_admin)}`);
console.log(`python pywebpush     : ${mark(report.python_packages.pywebpush)}`);
console.log('');
console.log('Credential candidates:');
for (const file of credentialFiles) {
  console.log(`  ${file.present ? 'present' : 'absent '} ${file.path}${file.project_id ? ` (project ${file.project_id})` : ''}`);
}
console.log('');
console.log('Environment:');
for (const [key, value] of [...Object.entries(firebaseEnv), ...Object.entries(webPushEnv)]) {
  console.log(`  ${value.padEnd(5)} ${key}`);
}
console.log('');
if (report.live.requested) {
  console.log(`Live test: ${report.live.sent ? 'sent' : 'not sent'}${report.live.reason ? ` (${report.live.reason})` : ''}`);
} else {
  console.log(report.live.note);
}
