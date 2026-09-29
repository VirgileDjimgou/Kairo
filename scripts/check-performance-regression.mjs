#!/usr/bin/env node
/**
 * Performance regression signal.
 *
 * Runs the deterministic 200-member performance harness and compares p95
 * latency and SQL statement counts against the committed thresholds in
 * docs/performance/performance-baseline.json.
 *
 * This is intentionally opt-in (npm run perf:check), not part of generic CI:
 * absolute latencies depend on the developer/operator machine. Statement-count
 * regressions are the primary signal.
 *
 * Usage: node scripts/check-performance-regression.mjs [--json]
 */
import { execFileSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const asJson = process.argv.includes('--json');
const baselinePath = path.join(root, 'docs/performance/performance-baseline.json');
const baseline = JSON.parse(readFileSync(baselinePath, 'utf8'));

function pythonExecutable() {
  const candidates = [
    path.join(root, '.venv', 'Scripts', 'python.exe'),
    path.join(root, '.venv', 'bin', 'python'),
    process.env.PYTHON,
  ].filter(Boolean);
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}

const tempDir = mkdtempSync(path.join(tmpdir(), 'kairo-perf-'));
const tempJson = path.join(tempDir, 'result.json');
const tempMarkdown = path.join(tempDir, 'result.md');

let report;
try {
  execFileSync(
    pythonExecutable(),
    [
      'services/api/scripts/performance_baseline.py',
      '--sizes',
      '200',
      '--iterations',
      '3',
      '--output',
      tempJson,
      '--markdown',
      tempMarkdown,
    ],
    { cwd: root, stdio: 'inherit' },
  );
  report = JSON.parse(readFileSync(tempJson, 'utf8'));
} finally {
  rmSync(tempDir, { recursive: true, force: true });
}

const measured = report.sizes['200'] ?? {};
const thresholds = baseline.thresholds ?? {};
const violations = [];

for (const [operation, values] of Object.entries(measured)) {
  const threshold = thresholds[operation];
  if (!threshold) {
    violations.push(`${operation}: no committed threshold`);
    continue;
  }
  if (values.p95_ms > threshold.max_p95_ms) {
    violations.push(
      `${operation}: p95 ${values.p95_ms}ms exceeds ${threshold.max_p95_ms}ms`,
    );
  }
  if (values.statements > threshold.max_statements) {
    violations.push(
      `${operation}: ${values.statements} statements exceed ${threshold.max_statements}`,
    );
  }
}

if (asJson) {
  console.log(JSON.stringify({ measured, violations }, null, 2));
} else {
  console.log('Performance regression check (200 members)');
  for (const [operation, values] of Object.entries(measured)) {
    const threshold = thresholds[operation] ?? {};
    console.log(
      `  ${operation.padEnd(28)} p95=${String(values.p95_ms).padStart(8)}ms (max ${threshold.max_p95_ms}) statements=${values.statements} (max ${threshold.max_statements})`,
    );
  }
  for (const violation of violations) console.log(`  VIOLATION ${violation}`);
}

if (violations.length > 0) {
  console.error('');
  console.error('Performance regression detected. Re-run npm run perf:baseline to refresh')
  console.error('thresholds only after confirming the change is intentional.');
  process.exit(1);
}
console.log('');
console.log('OK: representative workloads are inside the committed thresholds.');
