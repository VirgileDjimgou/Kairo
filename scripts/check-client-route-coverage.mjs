#!/usr/bin/env node
/**
 * Client route coverage guard.
 *
 * Every literal API path used by the Vue PWA and the Flutter client must map to
 * an operation in the committed OpenAPI schema (docs/api/openapi.json). Dynamic
 * dispatchers are counted and reported but cannot be statically verified.
 *
 * Usage: node scripts/check-client-route-coverage.mjs [--json]
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const asJson = process.argv.includes('--json');
const schema = JSON.parse(readFileSync(path.join(root, 'docs/api/openapi.json'), 'utf8'));

function canonicalPath(raw) {
  let value = String(raw).trim().split('?')[0].split('#')[0];
  value = value.replace(/\$\{[^}]*\}/g, ':param');
  value = value.replace(/\/\$[A-Za-z_][A-Za-z0-9_]*/g, '/:param');
  value = value.replace(/\$[A-Za-z_][A-Za-z0-9_]*/g, '');
  value = value.replace(/\{[^}]+\}/g, ':param').replace(/:[A-Za-z_][A-Za-z0-9_]*/g, ':param');
  value = value.replace(/\/+/g, '/');
  if (!value.startsWith('/')) value = `/${value}`;
  if (value.startsWith('/api/v1/')) value = value.slice('/api/v1'.length);
  if (value === '/api/v1') value = '/';
  if (value.length > 1 && value.endsWith('/')) value = value.slice(0, -1);
  return value;
}

const documented = new Map();
for (const [route, operations] of Object.entries(schema.paths)) {
  for (const method of ['get', 'post', 'put', 'patch', 'delete']) {
    if (operations[method]) documented.set(`${method.toUpperCase()} ${canonicalPath(route)}`, route);
  }
}

function walk(directory, filter) {
  const results = [];
  for (const entry of readdirSync(directory)) {
    const absolute = path.join(directory, entry);
    const stats = statSync(absolute);
    if (stats.isDirectory()) {
      if (entry === 'generated' || entry === 'node_modules' || entry === 'build' || entry === 'dist') continue;
      results.push(...walk(absolute, filter));
    } else if (filter(absolute)) {
      results.push(absolute);
    }
  }
  return results;
}

const webFiles = walk(path.join(root, 'apps/web/src/api'), (file) => file.endsWith('.ts'));
const webCalls = [];
const webDynamic = [];
for (const file of webFiles) {
  const content = readFileSync(file, 'utf8');
  const relative = path.relative(root, file).replace(/\\/g, '/');
  const httpPattern = /http\.(get|post|put|patch|delete)(?:<[^>]*>)?\(\s*(['"`])([^'"`]+)\2/g;
  let match;
  while ((match = httpPattern.exec(content)) !== null) {
    webCalls.push({ source: relative, method: match[1].toUpperCase(), path: match[3] });
  }
  const fetchPattern = /fetch\(\s*`([^`]*)`/g;
  while ((match = fetchPattern.exec(content)) !== null) {
    const window = content.slice(match.index, match.index + 400);
    const methodMatch = window.match(/method:\s*["']([A-Z]+)["']/);
    const literal = match[1].replace(/^\$\{[^}]*\}/, '');
    if (!literal) {
      webDynamic.push({ source: relative, detail: match[1].trim() });
      continue;
    }
    webCalls.push({ source: relative, method: methodMatch ? methodMatch[1] : 'GET', path: literal });
  }
}

const flutterFiles = walk(path.join(root, 'apps/flutter_kairo/lib'), (file) => file.endsWith('.dart'));
const flutterCalls = [];
const flutterDynamic = [];
for (const file of flutterFiles) {
  const content = readFileSync(file, 'utf8');
  const relative = path.relative(root, file).replace(/\\/g, '/');
  const literalPattern = /requestJson\(\s*'([A-Z]+)'\s*,\s*'([^']+)'/g;
  let match;
  while ((match = literalPattern.exec(content)) !== null) {
    flutterCalls.push({ source: relative, method: match[1].toUpperCase(), path: match[2] });
  }
  const dynamicPattern = /requestJson\(\s*'([A-Z]+)'\s*,\s*(?!')/g;
  while ((match = dynamicPattern.exec(content)) !== null) {
    flutterDynamic.push({ source: relative, detail: `requestJson(${match[1]}, <dynamic path>)` });
  }
  const getPattern = /getJson\(\s*'([^']+)'/g;
  while ((match = getPattern.exec(content)) !== null) {
    flutterCalls.push({ source: relative, method: 'GET', path: match[1] });
  }
  const bytesPattern = /requestBytes\(\s*'([^']+)'/g;
  while ((match = bytesPattern.exec(content)) !== null) {
    flutterCalls.push({ source: relative, method: 'GET', path: match[1] });
  }
  const uploadPattern = /uploadFile\(\s*path:\s*'([^']+)'/g;
  while ((match = uploadPattern.exec(content)) !== null) {
    flutterCalls.push({ source: relative, method: 'POST', path: match[1] });
  }
}

const unknown = [];
for (const call of [...webCalls, ...flutterCalls]) {
  const key = `${call.method} ${canonicalPath(call.path)}`;
  if (!documented.has(key)) {
    unknown.push({ ...call, canonical: canonicalPath(call.path) });
  }
}

const report = {
  documented_operations: documented.size,
  web: { literal_calls: webCalls.length, dynamic_calls: webDynamic.length },
  flutter: { literal_calls: flutterCalls.length, dynamic_calls: flutterDynamic.length },
  unknown_calls: unknown,
  dynamic: { web: webDynamic, flutter: flutterDynamic },
};

if (asJson) {
  console.log(JSON.stringify(report, null, 2));
} else {
  console.log('Client route coverage');
  console.log(`  documented operations: ${report.documented_operations}`);
  console.log(`  Vue literal calls: ${report.web.literal_calls} (dynamic: ${report.web.dynamic_calls})`);
  console.log(`  Flutter literal calls: ${report.flutter.literal_calls} (dynamic: ${report.flutter.dynamic_calls})`);
  for (const call of unknown) {
    console.log(`  UNKNOWN ${call.method} ${call.path} -> ${call.canonical} (${call.source})`);
  }
  if (report.dynamic.web.length + report.dynamic.flutter.length > 0) {
    console.log('  Dynamic dispatchers (not statically verifiable):');
    for (const entry of [...report.dynamic.web, ...report.dynamic.flutter]) {
      console.log(`    ${entry.source}: ${entry.detail}`);
    }
  }
}

if (unknown.length > 0) {
  console.error('');
  console.error(`${unknown.length} client call(s) do not match any documented OpenAPI operation.`);
  process.exit(1);
}
console.log('');
console.log('OK: every statically visible client call maps to a documented operation.');
