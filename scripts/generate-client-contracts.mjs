#!/usr/bin/env node
/**
 * Generate typed client contracts for the Vue and Flutter clients from the
 * committed OpenAPI schema. Generated types coexist with the thin hand-written
 * gateways; they never make authorization decisions.
 *
 * Usage:
 *   node scripts/generate-client-contracts.mjs          # write generated files
 *   node scripts/generate-client-contracts.mjs --check  # fail on drift
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const schemaPath = path.join(root, 'docs/api/openapi.json');
const tsOutput = path.join(root, 'apps/web/src/api/generated/contracts.ts');
const dartOutput = path.join(root, 'apps/flutter_kairo/lib/core/api/generated/contracts.dart');
const check = process.argv.includes('--check');

const schema = JSON.parse(readFileSync(schemaPath, 'utf8'));
const schemas = schema.components?.schemas ?? {};

const HTTP_METHODS = ['get', 'post', 'put', 'patch', 'delete'];

function refName(ref) {
  return ref.split('/').pop();
}

function sanitizeIdentifier(name) {
  const cleaned = name.replace(/[^A-Za-z0-9_]/g, '_');
  return /^[0-9]/.test(cleaned) ? `_${cleaned}` : cleaned;
}

function quoteTsProperty(name) {
  return /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(name) ? name : JSON.stringify(name);
}

function tsType(input, doc) {
  if (!input) return 'unknown';
  if (input.$ref) return sanitizeIdentifier(refName(input.$ref));
  if (input.anyOf || input.oneOf) {
    const parts = (input.anyOf ?? input.oneOf).map((entry) => tsType(entry, doc));
    return [...new Set(parts)].join(' | ');
  }
  if (input.allOf) {
    return input.allOf.map((entry) => tsType(entry, doc)).join(' & ');
  }
  if (Array.isArray(input.enum)) {
    return input.enum.map((value) => JSON.stringify(value)).join(' | ');
  }
  const type = Array.isArray(input.type) ? input.type[0] : input.type;
  switch (type) {
    case 'string':
      return input.format === 'binary' ? 'Blob' : 'string';
    case 'integer':
    case 'number':
      return 'number';
    case 'boolean':
      return 'boolean';
    case 'null':
      return 'null';
    case 'array':
      return `Array<${tsType(input.items, doc)}>`;
    case 'object': {
      if (input.properties) {
        const required = new Set(input.required ?? []);
        const entries = Object.entries(input.properties)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([key, property]) => {
            const optional = required.has(key) ? '' : '?';
            return `${quoteTsProperty(key)}${optional}: ${tsType(property, doc)}`;
          });
        return `{ ${entries.join('; ')} }`;
      }
      if (input.additionalProperties && typeof input.additionalProperties === 'object') {
        return `Record<string, ${tsType(input.additionalProperties, doc)}>`;
      }
      return 'Record<string, unknown>';
    }
    default:
      return 'unknown';
  }
}

const DART_RESERVED = new Set([
  'abstract', 'as', 'assert', 'async', 'await', 'base', 'break', 'case', 'catch',
  'class', 'const', 'continue', 'covariant', 'default', 'deferred', 'do', 'dynamic',
  'else', 'enum', 'export', 'extends', 'extension', 'external', 'factory', 'false',
  'final', 'finally', 'for', 'function', 'get', 'hide', 'if', 'implements', 'import',
  'in', 'interface', 'is', 'late', 'library', 'mixin', 'new', 'null', 'of', 'on',
  'operator', 'part', 'required', 'rethrow', 'return', 'sealed', 'set', 'show',
  'static', 'super', 'switch', 'sync', 'this', 'throw', 'true', 'try', 'typedef',
  'var', 'void', 'when', 'while', 'with', 'yield',
]);

function dartIdentifier(name) {
  const cleaned = sanitizeIdentifier(name);
  if (DART_RESERVED.has(cleaned)) return `${cleaned}_`;
  return cleaned;
}

function unwrapNullable(input) {
  if (!input) return { schema: input, nullable: false };
  const alternatives = input.anyOf ?? input.oneOf;
  if (alternatives) {
    const nonNull = alternatives.filter((entry) => entry.type !== 'null');
    const nullable = nonNull.length !== alternatives.length;
    if (nonNull.length === 1) return { schema: nonNull[0], nullable };
    return { schema: input, nullable };
  }
  return { schema: input, nullable: Boolean(input.nullable) };
}

function isClassSchema(input) {
  if (!input || input.$ref) return false;
  const type = Array.isArray(input.type) ? input.type[0] : input.type;
  return type === 'object' && Boolean(input.properties);
}

function dartBaseType(input) {
  if (!input) return 'dynamic';
  if (input.$ref) return sanitizeIdentifier(refName(input.$ref));
  if (input.anyOf || input.oneOf || input.allOf) return 'dynamic';
  if (Array.isArray(input.enum)) return 'String';
  const type = Array.isArray(input.type) ? input.type[0] : input.type;
  switch (type) {
    case 'string':
      return input.format === 'binary' ? 'List<int>' : 'String';
    case 'integer':
      return 'int';
    case 'number':
      return 'num';
    case 'boolean':
      return 'bool';
    case 'array':
      return `List<${dartTypeName(input.items)}>`;
    case 'object':
      return 'Map<String, dynamic>';
    default:
      return 'dynamic';
  }
}

function dartTypeName(input) {
  const { schema: inner } = unwrapNullable(input);
  if (!inner) return 'dynamic';
  if (inner.$ref) return sanitizeIdentifier(refName(inner.$ref));
  if (inner.anyOf || inner.oneOf || inner.allOf) return 'dynamic';
  const type = Array.isArray(inner.type) ? inner.type[0] : inner.type;
  switch (type) {
    case 'string':
      return inner.format === 'binary' ? 'List<int>' : 'String';
    case 'integer':
      return 'int';
    case 'number':
      return 'num';
    case 'boolean':
      return 'bool';
    case 'array':
      return `List<${dartTypeName(inner.items)}>`;
    case 'object':
      return 'Map<String, dynamic>';
    default:
      return 'dynamic';
  }
}

function dartFromJson(input, expression) {
  const { schema: inner, nullable } = unwrapNullable(input);
  if (!inner) return expression;
  if (inner.$ref) {
    const name = sanitizeIdentifier(refName(inner.$ref));
    const target = schemas[refName(inner.$ref)];
    if (isClassSchema(target)) {
      return `${expression} == null ? null : ${name}.fromJson(${expression} as Map<String, dynamic>)`;
    }
    return dartFromJson(target, expression);
  }
  const type = Array.isArray(inner.type) ? inner.type[0] : inner.type;
  if (Array.isArray(inner.enum)) return `${expression} as String?`;
  switch (type) {
    case 'string':
      return inner.format === 'binary' ? `${expression} as List<int>?` : `${expression} as String?`;
    case 'integer':
      return `${expression} as int?`;
    case 'number':
      return `${expression} as num?`;
    case 'boolean':
      return `${expression} as bool?`;
    case 'array':
      return `(${expression} as List<dynamic>?)?.map((dynamic item) => ${dartArrayItem(inner.items)}).toList()`;
    case 'object':
      return `${expression} as Map<String, dynamic>?`;
    default:
      return expression;
  }
}

function dartArrayItem(input) {
  const { schema: inner } = unwrapNullable(input);
  if (!inner) return 'item';
  if (inner.$ref) {
    const name = sanitizeIdentifier(refName(inner.$ref));
    const target = schemas[refName(inner.$ref)];
    if (isClassSchema(target)) return `${name}.fromJson(item as Map<String, dynamic>)`;
    return dartArrayItem(target);
  }
  const type = Array.isArray(inner.type) ? inner.type[0] : inner.type;
  switch (type) {
    case 'string':
      return 'item as String';
    case 'integer':
      return 'item as int';
    case 'number':
      return 'item as num';
    case 'boolean':
      return 'item as bool';
    case 'array':
      return '(item as List<dynamic>)';
    case 'object':
      return 'item as Map<String, dynamic>';
    default:
      return 'item';
  }
}

function dartToJsonExpr(input, fieldName) {
  const { schema: inner } = unwrapNullable(input);
  if (!inner) return fieldName;
  if (inner.$ref) {
    const target = schemas[refName(inner.$ref)];
    if (isClassSchema(target)) return `${fieldName}!.toJson()`;
    return dartToJsonExpr(target, fieldName);
  }
  const type = Array.isArray(inner.type) ? inner.type[0] : inner.type;
  if (type === 'array') {
    const { schema: item } = unwrapNullable(inner.items);
    const itemRef = item?.$ref ? schemas[refName(item.$ref)] : null;
    if (itemRef && isClassSchema(itemRef)) {
      return `${fieldName}!.map((item) => item.toJson()).toList()`;
    }
  }
  return fieldName;
}

function renderTypeScript() {
  const lines = [
    '// AUTO-GENERATED from docs/api/openapi.json — do not edit by hand.',
    '// Regenerate with: node scripts/generate-client-contracts.mjs',
    '',
  ];
  for (const name of Object.keys(schemas).sort()) {
    const schemaEntry = schemas[name];
    const interfaceName = sanitizeIdentifier(name);
    if (schemaEntry.type === 'object' && schemaEntry.properties) {
      const required = new Set(schemaEntry.required ?? []);
      lines.push(`export interface ${interfaceName} {`);
      for (const [key, property] of Object.entries(schemaEntry.properties).sort(([a], [b]) => a.localeCompare(b))) {
        const optional = required.has(key) ? '' : '?';
        lines.push(`  ${quoteTsProperty(key)}${optional}: ${tsType(property, schema)};`);
      }
      lines.push('}', '');
    } else if (Array.isArray(schemaEntry.enum)) {
      lines.push(`export type ${interfaceName} = ${tsType(schemaEntry, schema)};`, '');
    } else if (schemaEntry.$ref) {
      lines.push(`export type ${interfaceName} = ${tsType(schemaEntry, schema)};`, '');
    } else {
      lines.push(`export type ${interfaceName} = ${tsType(schemaEntry, schema)};`, '');
    }
  }

  lines.push('export interface ApiOperations {');
  for (const route of Object.keys(schema.paths).sort()) {
    for (const method of HTTP_METHODS) {
      const operation = schema.paths[route]?.[method];
      if (!operation) continue;
      const requestSchema = operation.requestBody?.content?.['application/json']?.schema;
      const responseSchema =
        operation.responses?.['200']?.content?.['application/json']?.schema ??
        operation.responses?.['201']?.content?.['application/json']?.schema;
      const requestType = requestSchema ? tsType(requestSchema, schema) : 'undefined';
      const responseType = responseSchema ? tsType(responseSchema, schema) : 'undefined';
      lines.push(
        `  '${method.toUpperCase()} ${route}': { request: ${requestType}; response: ${responseType} };`,
      );
    }
  }
  lines.push('}', '');
  return lines.join('\n');
}

function renderDart() {
  const lines = [
    '// AUTO-GENERATED from docs/api/openapi.json — do not edit by hand.',
    '// Regenerate with: node scripts/generate-client-contracts.mjs',
    '// dart format off',
    '',
    '// ignore_for_file: prefer_const_constructors, sort_constructors_first, always_use_package_imports, non_constant_identifier_names, camel_case_types',
    '',
  ];
  for (const name of Object.keys(schemas).sort()) {
    const schemaEntry = schemas[name];
    const className = sanitizeIdentifier(name);
    if (isClassSchema(schemaEntry)) {
      const properties = Object.entries(schemaEntry.properties).sort(([a], [b]) => a.localeCompare(b));
      const constructorArgs = properties
        .map(([key, property]) => `this.${dartIdentifier(key)}`)
        .join(', ');
      lines.push(`class ${className} {`);
      lines.push(`  const ${className}({${constructorArgs}});`);
      lines.push('');
      lines.push(`  factory ${className}.fromJson(Map<String, dynamic> json) => ${className}(`);
      for (const [key, property] of properties) {
        lines.push(
          `        ${dartIdentifier(key)}: ${dartFromJson(property, `json['${key}']`)},`,
        );
      }
      lines.push('      );');
      lines.push('');
      for (const [key, property] of properties) {
        const { schema: inner } = unwrapNullable(property);
        const base = dartBaseType(inner);
        const fieldType = base === 'dynamic' ? base : `${base}?`;
        lines.push(`  final ${fieldType} ${dartIdentifier(key)};`);
      }
      lines.push('');
      lines.push('  Map<String, dynamic> toJson() => <String, dynamic>{');
      for (const [key, property] of properties) {
        lines.push(
          `        if (${dartIdentifier(key)} != null) '${key}': ${dartToJsonExpr(property, dartIdentifier(key))},`,
        );
      }
      lines.push('      };');
      lines.push('}', '');
    } else {
      lines.push(`typedef ${className} = ${dartBaseType(schemaEntry)};`, '');
    }
  }

  lines.push('const Map<String, String> apiOperationIds = <String, String>{');
  for (const route of Object.keys(schema.paths).sort()) {
    for (const method of HTTP_METHODS) {
      const operation = schema.paths[route]?.[method];
      if (!operation) continue;
      const operationId = operation.operationId ?? '';
      lines.push(`  '${method.toUpperCase()} ${route}': '${operationId}',`);
    }
  }
  lines.push('};', '');
  return lines.join('\n');
}

const rendered = [
  { path: tsOutput, content: renderTypeScript() },
  { path: dartOutput, content: renderDart() },
];

if (check) {
  let failed = false;
  for (const file of rendered) {
    const current = existsSync(file.path) ? readFileSync(file.path, 'utf8') : null;
    if (current !== file.content) {
      failed = true;
      console.error(`Generated contract is out of date: ${path.relative(root, file.path)}`);
    }
  }
  if (failed) {
    console.error('Regenerate with: node scripts/generate-client-contracts.mjs');
    process.exit(1);
  }
  console.log('OK: generated client contracts match the committed OpenAPI schema.');
  process.exit(0);
}

for (const file of rendered) {
  mkdirSync(path.dirname(file.path), { recursive: true });
  writeFileSync(file.path, file.content, 'utf8');
  console.log(`Wrote ${path.relative(root, file.path)}`);
}
