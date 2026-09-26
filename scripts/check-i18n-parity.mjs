#!/usr/bin/env node

/**
 * FR/EN/DE catalog parity guard (Roadmap V2 Sprint 108).
 *
 * The product catalogs live in `apps/web/src/i18n/<locale>/<feature>.json`.
 * This guard fails CI when:
 *   - a locale is missing a feature file another locale has;
 *   - a locale is missing a key another locale has;
 *   - a key has an empty or whitespace-only value.
 *
 * Usage: node scripts/check-i18n-parity.mjs [--json]
 */

import { existsSync, readFileSync, readdirSync } from 'fs'
import { join } from 'path'

const LOCALES = ['fr', 'en', 'de']
const I18N_DIR = join(import.meta.dirname, '..', 'apps', 'web', 'src', 'i18n')
const jsonOutput = process.argv.includes('--json')

function loadLocale(locale) {
  const dir = join(I18N_DIR, locale)
  const catalogs = {}
  if (!existsSync(dir)) return catalogs
  for (const file of readdirSync(dir)) {
    if (!file.endsWith('.json')) continue
    const feature = file.slice(0, -'.json'.length)
    catalogs[feature] = JSON.parse(readFileSync(join(dir, file), 'utf-8'))
  }
  return catalogs
}

function main() {
  const catalogsByLocale = Object.fromEntries(LOCALES.map((locale) => [locale, loadLocale(locale)]))
  const problems = []

  const reference = LOCALES[0]
  const referenceFeatures = Object.keys(catalogsByLocale[reference]).sort()
  for (const locale of LOCALES.slice(1)) {
    const features = Object.keys(catalogsByLocale[locale]).sort()
    for (const feature of referenceFeatures) {
      if (!features.includes(feature)) {
        problems.push(`[${locale}] missing catalog file for feature "${feature}" (present in ${reference})`)
      }
    }
    for (const feature of features) {
      if (!referenceFeatures.includes(feature)) {
        problems.push(`[${locale}] has extra catalog file "${feature}" not present in ${reference}`)
      }
    }
  }

  let totalKeys = 0
  const featureReport = {}
  for (const feature of referenceFeatures) {
    const referenceKeys = Object.keys(catalogsByLocale[reference][feature] ?? {}).sort()
    featureReport[feature] = { keys: referenceKeys.length }
    totalKeys += referenceKeys.length
    for (const locale of LOCALES) {
      const catalog = catalogsByLocale[locale][feature]
      if (!catalog) continue
      const keys = Object.keys(catalog)
      const missing = referenceKeys.filter((key) => !(key in catalog))
      const extra = keys.filter((key) => !referenceKeys.includes(key))
      for (const key of missing.slice(0, 10)) problems.push(`[${locale}/${feature}] missing key "${key}"`)
      if (missing.length > 10) problems.push(`[${locale}/${feature}] ... and ${missing.length - 10} more missing keys`)
      for (const key of extra.slice(0, 10)) problems.push(`[${locale}/${feature}] extra key "${key}"`)
      if (extra.length > 10) problems.push(`[${locale}/${feature}] ... and ${extra.length - 10} more extra keys`)
    }
  }

  for (const locale of LOCALES) {
    for (const [feature, catalog] of Object.entries(catalogsByLocale[locale])) {
      for (const [key, value] of Object.entries(catalog)) {
        if (typeof value !== 'string' || value.trim().length === 0) {
          problems.push(`[${locale}/${feature}] "${key}" has an empty value`)
        }
      }
    }
  }

  if (jsonOutput) {
    console.log(JSON.stringify({ locales: LOCALES, totalKeys, features: featureReport, problems }, null, 2))
  } else {
    console.log('Translation parity check (FR/EN/DE feature catalogs)\n')
    for (const [feature, report] of Object.entries(featureReport)) {
      console.log(`  ${feature.padEnd(12)} ${report.keys} keys`)
    }
    console.log(`\nTotal: ${totalKeys} keys per locale across ${referenceFeatures.length} feature catalogs.`)
    if (problems.length) {
      console.log(`\nFAILED: ${problems.length} parity problem(s):`)
      for (const problem of problems) console.log(`  - ${problem}`)
    } else {
      console.log('OK: FR, EN and DE catalogs are in exact key parity.')
    }
  }

  if (problems.length) process.exitCode = 1
}

main()
