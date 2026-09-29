#!/usr/bin/env node
/** Cross-platform launcher for the deterministic performance baseline. */
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

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

execFileSync(
  pythonExecutable(),
  ['services/api/scripts/performance_baseline.py', ...process.argv.slice(2)],
  { cwd: root, stdio: 'inherit' },
);
