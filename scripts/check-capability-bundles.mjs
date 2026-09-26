#!/usr/bin/env node

/**
 * Capability bundle guard (Roadmap V2 Sprint 109).
 *
 * The web client's transitional fallback bundles must stay in sync with the
 * backend role catalog. This script regenerates the expected TypeScript map
 * from `services/api/app/core/capabilities.py` and
 * `services/api/app/modules/tenancy/role_catalog.py` and compares it with the
 * checked-in `apps/web/src/config/capabilityBundles.ts`.
 *
 * Usage:
 *   node scripts/check-capability-bundles.mjs           # verify (CI)
 *   node scripts/check-capability-bundles.mjs --write   # regenerate
 */

import { readFileSync, writeFileSync } from 'fs'
import { join } from 'path'

const ROOT = join(import.meta.dirname, '..')
const CAPABILITIES_PY = join(ROOT, 'services', 'api', 'app', 'core', 'capabilities.py')
const ROLE_CATALOG_PY = join(ROOT, 'services', 'api', 'app', 'modules', 'tenancy', 'role_catalog.py')
const TARGET_TS = join(ROOT, 'apps', 'web', 'src', 'config', 'capabilityBundles.ts')

function parseCapabilityConstants(source) {
  const constants = {}
  for (const match of source.matchAll(/^(CAP_[A-Z0-9_]+) = "([^"]+)"/gm)) {
    constants[match[1]] = match[2]
  }
  return constants
}

function parseCapabilityOrder(source) {
  const tuple = source.match(/CAPABILITY_ORDER = \(([\s\S]*?)\n\)/)
  if (!tuple) throw new Error('CAPABILITY_ORDER not found')
  return [...tuple[1].matchAll(/CAP_[A-Z0-9_]+/g)].map((match) => match[0])
}

function parseLegacyExclusions(source) {
  const exclusions = source.match(/CAPABILITY_ORDER\s*\n\s*if capability not in \{([^}]*)\}/)
  if (!exclusions) throw new Error('legacy capability exclusions not found')
  return new Set([...exclusions[1].matchAll(/CAP_[A-Z0-9_]+/g)].map((match) => match[0]))
}

function parseRoleDefinitions(source) {
  const roles = []
  const blocks = source.split('RoleDefinition(').slice(1)
  for (const block of blocks) {
    const code = block.match(/code="([a-z_]+)"/)
    const capabilities = block.match(/capabilities=\(([\s\S]*?)\n\s*\),/)
    if (!code || !capabilities) continue
    roles.push({
      code: code[1],
      capabilities: [...capabilities[1].matchAll(/CAP_[A-Z0-9_]+/g)].map((match) => match[0]),
    })
  }
  return roles
}

function buildBundles() {
  const capabilitiesSource = readFileSync(CAPABILITIES_PY, 'utf8')
  const roleCatalogSource = readFileSync(ROLE_CATALOG_PY, 'utf8')
  const constants = parseCapabilityConstants(capabilitiesSource)
  const order = parseCapabilityOrder(capabilitiesSource)
  const exclusions = parseLegacyExclusions(capabilitiesSource)
  const roles = parseRoleDefinitions(roleCatalogSource)

  const toValues = (symbols) =>
    order
      .filter((symbol) => symbols.includes(symbol))
      .map((symbol) => constants[symbol] ?? symbol)

  const bundles = {}
  for (const role of roles) {
    bundles[role.code] = toValues(role.capabilities)
  }
  bundles.admin = order
    .filter((symbol) => !exclusions.has(symbol))
    .map((symbol) => constants[symbol] ?? symbol)
  return bundles
}

function render(bundles) {
  const lines = [
    '/**',
    ' * Generated from services/api/app/modules/tenancy/role_catalog.py and',
    ' * services/api/app/core/capabilities.py. Do not edit by hand.',
    ' *',
    ' * Transitional fallback only: authoritative effective capabilities come',
    ' * from the API (`/auth/me` and tenant memberships). This drift-checked map',
    ' * keeps older payloads accurate. Regenerate with',
    ' * `node scripts/check-capability-bundles.mjs --write`.',
    ' */',
    'export const ROLE_CAPABILITY_BUNDLES: Record<string, readonly string[]> = {',
  ]
  for (const [role, capabilities] of Object.entries(bundles)) {
    lines.push(`  ${role}: [`)
    for (const capability of capabilities) {
      lines.push(`    '${capability}',`)
    }
    lines.push('  ],')
  }
  lines.push('}')
  lines.push('')
  return lines.join('\n')
}

const expected = render(buildBundles())
const write = process.argv.includes('--write')

if (write) {
  writeFileSync(TARGET_TS, expected, 'utf8')
  console.log(`Wrote ${TARGET_TS}`)
} else {
  let actual = ''
  try {
    actual = readFileSync(TARGET_TS, 'utf8')
  } catch {
    actual = ''
  }
  if (actual !== expected) {
    console.error('Capability fallback bundles are out of sync with the backend role catalog.')
    console.error('Run: node scripts/check-capability-bundles.mjs --write')
    process.exit(1)
  }
  console.log('Capability fallback bundles match the backend role catalog.')
}
