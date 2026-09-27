#!/usr/bin/env node
/**
 * OpenAPI contract guard.
 *
 * Regenerates the FastAPI schema and compares it with the committed baseline in
 * docs/api/openapi.json. Breaking changes fail the check; additive changes are
 * reported. Use --update after an intentional contract change.
 *
 * Usage:
 *   node scripts/check-openapi-contract.mjs
 *   node scripts/check-openapi-contract.mjs --update
 *   node scripts/check-openapi-contract.mjs --baseline <path> --json
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const update = args.includes('--update');
const asJson = args.includes('--json');
const baselineArg = args.indexOf('--baseline');
const baselinePath = path.resolve(
  root,
  baselineArg >= 0 && args[baselineArg + 1] ? args[baselineArg + 1] : 'docs/api/openapi.json',
);

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

function generateSchema() {
  const raw = execFileSync(pythonExecutable(), ['services/api/scripts/export_openapi.py'], {
    cwd: root,
    encoding: 'utf8',
    maxBuffer: 128 * 1024 * 1024,
  });
  return JSON.parse(raw);
}

function typeOf(schema) {
  if (!schema) return 'any';
  if (schema.$ref) return schema.$ref.split('/').pop();
  if (schema.enum) return `enum(${schema.enum.map(String).sort().join('|')})`;
  if (schema.anyOf) return `anyOf(${schema.anyOf.map(typeOf).sort().join('|')})`;
  if (schema.oneOf) return `oneOf(${schema.oneOf.map(typeOf).sort().join('|')})`;
  if (schema.allOf) return `allOf(${schema.allOf.map(typeOf).join('&')})`;
  const types = Array.isArray(schema.type) ? schema.type.slice().sort().join('|') : schema.type;
  if (types === 'array') return `array<${typeOf(schema.items)}>`;
  return types ?? 'any';
}

function resolve(schema, doc) {
  if (schema && schema.$ref) {
    const name = schema.$ref.split('/').pop();
    return doc?.components?.schemas?.[name] ?? null;
  }
  return schema ?? null;
}

function diffSchema(before, after, docBefore, docAfter, direction, location, seen = new Set()) {
  const breaking = [];
  if (!before || !after) return breaking;
  const beforeType = typeOf(before);
  const afterType = typeOf(after);
  if (beforeType !== afterType) {
    breaking.push(`${location}: type changed from ${beforeType} to ${afterType}`);
    return breaking;
  }
  if (before.$ref || after.$ref) {
    const name = (before.$ref ?? after.$ref).split('/').pop();
    if (seen.has(name)) return breaking;
    seen.add(name);
    return diffSchema(
      resolve(before, docBefore),
      resolve(after, docAfter),
      docBefore,
      docAfter,
      direction,
      location,
      seen,
    );
  }
  if (Array.isArray(before.enum) && Array.isArray(after.enum)) {
    for (const value of before.enum) {
      if (!after.enum.includes(value)) {
        breaking.push(`${location}: enum value "${value}" was removed`);
      }
    }
  }
  const beforeRequired = new Set(before.required ?? []);
  const afterRequired = new Set(after.required ?? []);
  if (direction === 'request') {
    for (const property of before.properties ? Object.keys(before.properties) : []) {
      if (!after.properties || !(property in after.properties)) {
        breaking.push(`${location}: request property "${property}" was removed`);
      }
    }
  } else {
    for (const property of beforeRequired) {
      if (!after.properties || !(property in after.properties)) {
        breaking.push(`${location}: required response property "${property}" was removed`);
      }
    }
  }
  if (direction === 'request') {
    for (const property of afterRequired) {
      if (!beforeRequired.has(property)) {
        breaking.push(`${location}: request property "${property}" became required`);
      }
    }
  }
  const beforeProperties = before.properties ?? {};
  const afterProperties = after.properties ?? {};
  for (const property of Object.keys(beforeProperties)) {
    if (!(property in afterProperties)) continue;
    breaking.push(
      ...diffSchema(
        beforeProperties[property],
        afterProperties[property],
        docBefore,
        docAfter,
        direction,
        `${location}.${property}`,
        seen,
      ),
    );
  }
  if (before.items && after.items) {
    breaking.push(
      ...diffSchema(before.items, after.items, docBefore, docAfter, direction, `${location}[]`, seen),
    );
  }
  const beforeAlternatives = before.anyOf ?? before.oneOf;
  const afterAlternatives = after.anyOf ?? after.oneOf;
  if (beforeAlternatives && afterAlternatives) {
    const beforeSet = new Set(beforeAlternatives.map(typeOf));
    const afterSet = new Set(afterAlternatives.map(typeOf));
    for (const alternative of beforeSet) {
      if (!afterSet.has(alternative)) {
        breaking.push(`${location}: alternative ${alternative} was removed`);
      }
    }
  }
  return breaking;
}

function diffOperation(beforePath, afterPath, docBefore, docAfter, location) {
  const breaking = [];
  const methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head'];
  for (const method of methods) {
    const before = beforePath?.[method];
    const after = afterPath?.[method];
    if (!before) continue;
    if (!after) {
      breaking.push(`${location} ${method.toUpperCase()}: operation was removed`);
      continue;
    }
    const beforeParameters = new Map(
      (before.parameters ?? []).map((parameter) => [`${parameter.in}:${parameter.name}`, parameter]),
    );
    const afterParameters = new Map(
      (after.parameters ?? []).map((parameter) => [`${parameter.in}:${parameter.name}`, parameter]),
    );
    for (const [key, parameter] of beforeParameters) {
      const next = afterParameters.get(key);
      if (!next) {
        breaking.push(`${location} ${method.toUpperCase()}: parameter ${key} was removed`);
        continue;
      }
      if (!parameter.required && next.required) {
        breaking.push(`${location} ${method.toUpperCase()}: parameter ${key} became required`);
      }
      breaking.push(
        ...diffSchema(
          parameter.schema,
          next.schema,
          docBefore,
          docAfter,
          'request',
          `${location} ${method.toUpperCase()} parameter ${key}`,
        ),
      );
    }
    const beforeBody = before.requestBody;
    const afterBody = after.requestBody;
    if (beforeBody) {
      if (!afterBody) {
        breaking.push(`${location} ${method.toUpperCase()}: request body was removed`);
      } else {
        if (!beforeBody.required && afterBody.required) {
          breaking.push(`${location} ${method.toUpperCase()}: request body became required`);
        }
        for (const mediaType of Object.keys(beforeBody.content ?? {})) {
          const beforeSchema = beforeBody.content[mediaType]?.schema;
          const afterSchema = afterBody.content?.[mediaType]?.schema;
          if (beforeSchema && !afterSchema) {
            breaking.push(`${location} ${method.toUpperCase()}: request body media type ${mediaType} was removed`);
            continue;
          }
          breaking.push(
            ...diffSchema(
              beforeSchema,
              afterSchema,
              docBefore,
              docAfter,
              'request',
              `${location} ${method.toUpperCase()} request ${mediaType}`,
            ),
          );
        }
      }
    }
    if (before.responses) {
      for (const status of Object.keys(before.responses)) {
        if (status === '422') continue;
        const beforeResponse = before.responses[status];
        const afterResponse = after.responses?.[status];
        if (!afterResponse) {
          breaking.push(`${location} ${method.toUpperCase()}: response ${status} was removed`);
          continue;
        }
        for (const mediaType of Object.keys(beforeResponse.content ?? {})) {
          const beforeSchema = beforeResponse.content[mediaType]?.schema;
          const afterSchema = afterResponse.content?.[mediaType]?.schema;
          if (beforeSchema && !afterSchema) {
            breaking.push(`${location} ${method.toUpperCase()}: response ${status} media type ${mediaType} was removed`);
            continue;
          }
          breaking.push(
            ...diffSchema(
              beforeSchema,
              afterSchema,
              docBefore,
              docAfter,
              'response',
              `${location} ${method.toUpperCase()} response ${status} ${mediaType}`,
            ),
          );
        }
      }
    }
  }
  return breaking;
}

function diffContracts(before, after) {
  const breaking = [];
  const additive = [];

  for (const route of Object.keys(before.paths ?? {})) {
    if (!(route in (after.paths ?? {}))) {
      breaking.push(`path ${route} was removed`);
      continue;
    }
    breaking.push(
      ...diffOperation(before.paths[route], after.paths[route], before, after, `path ${route}`),
    );
  }
  for (const route of Object.keys(after.paths ?? {})) {
    if (!(route in (before.paths ?? {}))) additive.push(`path ${route} was added`);
  }

  const beforeSchemas = before.components?.schemas ?? {};
  const afterSchemas = after.components?.schemas ?? {};
  for (const name of Object.keys(beforeSchemas)) {
    if (!(name in afterSchemas)) {
      breaking.push(`schema ${name} was removed`);
      continue;
    }
    // A schema used by both responses and requests is checked response-strict,
    // which is the conservative choice for consumers.
    breaking.push(
      ...diffSchema(beforeSchemas[name], afterSchemas[name], before, after, 'response', `schema ${name}`),
    );
  }
  for (const name of Object.keys(afterSchemas)) {
    if (!(name in beforeSchemas)) additive.push(`schema ${name} was added`);
  }

  return { breaking, additive };
}

if (update) {
  const schema = generateSchema();
  writeFileSync(baselinePath, `${JSON.stringify(schema, null, 2)}\n`, 'utf8');
  console.log(`OpenAPI baseline updated: ${path.relative(root, baselinePath)}`);
  process.exit(0);
}

if (!existsSync(baselinePath)) {
  console.error(`OpenAPI baseline not found: ${baselinePath}`);
  console.error('Generate it with: python services/api/scripts/export_openapi.py --output docs/api/openapi.json');
  process.exit(1);
}

const baseline = JSON.parse(readFileSync(baselinePath, 'utf8'));
let current;
try {
  current = generateSchema();
} catch (error) {
  console.error('Could not generate the current OpenAPI schema.');
  console.error(error.message);
  process.exit(1);
}

const { breaking, additive } = diffContracts(baseline, current);

if (asJson) {
  console.log(JSON.stringify({ breaking, additive }, null, 2));
} else {
  console.log('OpenAPI contract check');
  console.log(`  baseline: ${path.relative(root, baselinePath)}`);
  console.log(`  breaking changes: ${breaking.length}`);
  console.log(`  additive changes: ${additive.length}`);
  for (const change of breaking) console.log(`  BREAKING  ${change}`);
  for (const change of additive.slice(0, 20)) console.log(`  additive  ${change}`);
  if (additive.length > 20) console.log(`  ... ${additive.length - 20} more additive changes`);
}

if (breaking.length > 0) {
  console.error('');
  console.error('Breaking OpenAPI changes detected. If this is intentional, refresh the baseline:');
  console.error('  node scripts/check-openapi-contract.mjs --update');
  process.exit(1);
}
console.log('');
console.log('OK: no breaking OpenAPI changes.');
