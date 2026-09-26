import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { loadRoadmap } from './roadmap.mjs';
import { isLockStale, loadLock, loadState, ensureStateDir, stateDir } from './state.mjs';

function run(command, args = []) {
  const isWindows = process.platform === 'win32';
  const result = isWindows
    ? spawnSync(`${command} ${args.join(' ')}`, {
      encoding: 'utf8',
      shell: true,
      timeout: 30000,
    })
    : spawnSync(command, args, {
      encoding: 'utf8',
      timeout: 30000,
    });
  if (result.error) {
    return { ok: false, output: result.error.message };
  }
  const output = `${result.stdout ?? ''}${result.stderr ?? ''}`.trim();
  return { ok: result.status === 0, output };
}

function check(name, evaluator) {
  try {
    const result = evaluator();
    return { name, ...result };
  } catch (error) {
    return { name, status: 'fail', detail: error.message };
  }
}

function firebaseStatus(rootDir) {
  const candidates = [
    process.env.GOOGLE_APPLICATION_CREDENTIALS,
    process.env.FIREBASE_SERVICE_ACCOUNT_JSON,
    process.env.FIREBASE_SERVICE_ACCOUNT_PATH,
  ].filter(Boolean);
  for (const candidate of candidates) {
    if (candidate && existsSync(candidate)) {
      return 'configured (service account file present)';
    }
  }
  const serverPaths = [
    join(rootDir, 'services/api/.private/firebase-service-account.json'),
    join(rootDir, 'services/api/.private/firebase_admin.json'),
    join(rootDir, 'services/api/.private/google-services.json'),
  ];
  if (serverPaths.some((path) => existsSync(path))) {
    return 'configured (private server credential present)';
  }
  if (process.env.FCM_PROJECT_ID || process.env.FIREBASE_PROJECT_ID) {
    return 'partially configured (project id present, credential not verified)';
  }
  return 'not configured';
}

export function runDoctor(rootDir) {
  const checks = [];
  const nodeMajor = Number(process.versions.node.split('.')[0]);

  checks.push({
    name: 'Node.js',
    status: nodeMajor >= 20 ? 'ok' : 'warn',
    detail: process.version,
  });

  const npm = run('npm', ['--version']);
  checks.push({
    name: 'npm',
    status: npm.ok ? 'ok' : 'fail',
    detail: npm.output || 'not available',
  });

  checks.push({
    name: 'Git repository',
    status: existsSync(join(rootDir, '.git')) ? 'ok' : 'fail',
    detail: existsSync(join(rootDir, '.git')) ? rootDir : '.git not found',
  });

  const opencode = run('opencode', ['--version']);
  checks.push({
    name: 'OpenCode',
    status: opencode.ok ? 'ok' : 'warn',
    detail: opencode.output || 'opencode binary not found on PATH',
  });

  checks.push(check('OpenCode config', () => {
    const path = join(rootDir, 'opencode.json');
    if (!existsSync(path)) {
      return { status: 'warn', detail: 'opencode.json not present' };
    }
    JSON.parse(readFileSync(path, 'utf8'));
    return { status: 'ok', detail: 'opencode.json is parseable JSON' };
  }));

  const queueCandidates = [
    join(rootDir, '.opencode/node_modules/opencode-queue'),
    join(rootDir, '.opencode/node_modules/@opencode/queue'),
  ];
  const queueGlobal = run('npm', ['ls', '-g', '--depth=0', 'opencode-queue']);
  const queueInstalled = queueCandidates.some((path) => existsSync(path))
    || (queueGlobal.ok && queueGlobal.output.includes('opencode-queue'));
  checks.push({
    name: 'OpenCode Queue',
    status: queueInstalled ? 'ok' : 'warn',
    detail: queueInstalled
      ? 'queue package detected; batch correctness does not depend on it'
      : 'not installed; using the native Kairo sprint batch state machine',
  });

  let roadmap = null;
  checks.push(check('Roadmap parseable', () => {
    roadmap = loadRoadmap(rootDir);
    return { status: 'ok', detail: `${roadmap.sprints.length} sprints (S${roadmap.sprints[0].id}–S${roadmap.sprints[roadmap.sprints.length - 1].id})` };
  }));

  checks.push(check('State directory writable', () => {
    ensureStateDir(rootDir);
    return { status: 'ok', detail: stateDir(rootDir) };
  }));

  checks.push(check('Competing active batch', () => {
    const lock = loadLock(rootDir);
    if (!lock || lock.released_at) {
      return { status: 'ok', detail: 'no active lock' };
    }
    if (isLockStale(lock)) {
      return { status: 'warn', detail: `stale lock from batch ${lock.batch_id} can be taken over` };
    }
    const state = loadState(rootDir);
    if (state && state.batch_id === lock.batch_id && ['running', 'paused'].includes(state.status)) {
      return { status: 'warn', detail: `batch ${lock.batch_id} is ${state.status}; resume it instead of starting a new one` };
    }
    return { status: 'ok', detail: `lock ${lock.batch_id} present but batch is not active` };
  }));

  const python = run(process.platform === 'win32' ? 'python' : 'python3', ['--version']);
  checks.push({
    name: 'Python',
    status: python.ok ? 'ok' : 'fail',
    detail: python.output || 'python not available',
  });

  const flutterTrack = existsSync(join(rootDir, 'apps/flutter_kairo/pubspec.yaml'));
  const flutter = run(process.platform === 'win32' ? 'flutter.bat' : 'flutter', ['--version']);
  checks.push({
    name: 'Flutter',
    status: flutter.ok ? 'ok' : (flutterTrack ? 'warn' : 'warn'),
    detail: flutter.ok
      ? flutter.output.split('\n')[0]
      : 'flutter not on PATH; Flutter track exists but local builds require the Flutter SDK',
  });

  const docker = run('docker', ['--version']);
  checks.push({
    name: 'Docker',
    status: docker.ok ? 'ok' : 'warn',
    detail: docker.output || 'docker not available',
  });

  const criticalFiles = [
    'AGENTS.md',
    'PROJECT_STATUS.md',
    'docs/roadmap/KAIRO_V2_ROADMAP.json',
    'services/api/pyproject.toml',
    'apps/web/package.json',
    'apps/flutter_kairo/pubspec.yaml',
    'scripts/check-sensitive-files.mjs',
  ];
  const missing = criticalFiles.filter((relative) => !existsSync(join(rootDir, relative)));
  checks.push({
    name: 'Critical project files',
    status: missing.length === 0 ? 'ok' : 'fail',
    detail: missing.length === 0 ? `${criticalFiles.length} present` : `missing: ${missing.join(', ')}`,
  });

  checks.push({
    name: 'Firebase credentials',
    status: 'ok',
    detail: `${firebaseStatus(rootDir)} (secrets are never printed)`,
  });

  const failing = checks.filter((entry) => entry.status === 'fail');
  const warnings = checks.filter((entry) => entry.status === 'warn');
  return {
    ok: failing.length === 0,
    checks,
    summary: `${checks.length - failing.length - warnings.length} ok, ${warnings.length} warning, ${failing.length} failing`,
  };
}

export function formatDoctor(result) {
  const lines = [];
  lines.push('## Kairo Sprint Batch Doctor');
  lines.push('');
  for (const entry of result.checks) {
    const marker = entry.status === 'ok' ? 'OK  ' : entry.status === 'warn' ? 'WARN' : 'FAIL';
    lines.push(`${marker}  ${entry.name}: ${entry.detail}`);
  }
  lines.push('');
  lines.push(`Summary: ${result.summary}`);
  lines.push('');
  return lines.join('\n');
}
