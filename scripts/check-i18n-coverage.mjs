#!/usr/bin/env node

/**
 * Translation Coverage Check for Sprint 67
 * 
 * Scans Vue template files for potential hardcoded English strings that should
 * be using i18n keys via the localeStore.t() helper.
 * 
 * This script is a heuristic check and may produce false positives. It is intended
 * as a development aid, not a strict linter.
 * 
 * Usage: node scripts/check-i18n-coverage.mjs
 */

import { existsSync, readFileSync, readdirSync, statSync } from 'fs'
import { join } from 'path'

const SRC_DIR = join(import.meta.dirname, '..', 'apps', 'web', 'src')
const SCAN_DIRS = [join(SRC_DIR, 'views'), join(SRC_DIR, 'features')]
const I18N_DIR = join(SRC_DIR, 'i18n')

// Patterns that suggest hardcoded English text in templates
const HARDCODED_PATTERNS = [
  // Common UI words in angle brackets (between tags)
  />([A-Z][a-z]+(?:\s+[a-z]+){0,3})</g,
  // aria-label with hardcoded English
  /aria-label="([A-Z][a-z]+(?:\s+[a-z]+){0,5})"/g,
  // placeholder with hardcoded English
  /placeholder="([A-Z][a-z]+(?:\s+[a-z]+){0,5})"/g,
]

// Exclude patterns that are clearly not hardcoded text
const EXCLUDE_PATTERNS = [
  /^\d+$/,           // Numbers
  /^[A-Z]{2,}$/,     // Acronyms (CSS, HTML, etc.)
  /^[a-z_-]+$/,      // CSS classes, IDs
  /^{{.*}}$/,        // Vue expressions
  /^https?:\/\//,    // URLs
  /^[a-z]+\./,       // File extensions
]

function walkDir(dir, files = []) {
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry)
    if (statSync(fullPath).isDirectory()) {
      walkDir(fullPath, files)
    } else if (entry.endsWith('.vue')) {
      files.push(fullPath)
    }
  }
  return files
}

function checkFile(filePath) {
  const content = readFileSync(filePath, 'utf-8')
  const templateMatch = content.match(/<template>([\s\S]*?)<\/template>/)
  if (!templateMatch) return []

  const template = templateMatch[1]
  const issues = []

  for (const pattern of HARDCODED_PATTERNS) {
    let match
    while ((match = pattern.exec(template)) !== null) {
      const text = match[1].trim()
      if (text.length > 2 && text.length < 60) {
        const isExcluded = EXCLUDE_PATTERNS.some(ep => ep.test(text))
        if (!isExcluded) {
          const line = template.substring(0, match.index).split('\n').length
          issues.push({ line, text: text.substring(0, 40) })
        }
      }
    }
  }

  return issues
}

function main() {
  console.log('🌐 Translation Coverage Check\n')

  const vueFiles = SCAN_DIRS.filter((dir) => existsSync(dir)).flatMap((dir) => walkDir(dir))
  console.log(`Scanning ${vueFiles.length} Vue files...\n`)

  let totalIssues = 0
  const filesWithIssues = []

  for (const file of vueFiles) {
    const issues = checkFile(file)
    if (issues.length > 0) {
      const relPath = file.replace(SRC_DIR, 'src')
      filesWithIssues.push({ path: relPath, issues })
      totalIssues += issues.length
    }
  }

  if (filesWithIssues.length === 0) {
    console.log('✅ No obvious hardcoded strings detected.')
    console.log('   All Vue views appear to use i18n keys via t() or localeStore.t().\n')
  } else {
    console.log(`⚠️  Found ${totalIssues} potential hardcoded strings in ${filesWithIssues.length} files:\n`)
    for (const { path, issues } of filesWithIssues) {
      console.log(`  ${path}`)
      for (const { line, text } of issues.slice(0, 5)) {
        console.log(`    Line ${line}: "${text}"`)
      }
      if (issues.length > 5) {
        console.log(`    ... and ${issues.length - 5} more`)
      }
      console.log()
    }
    console.log('💡 Review these manually. Some may be false positives (CSS classes, IDs, etc.)')
    console.log('   Replace confirmed hardcoded strings with t() or localeStore.t() calls.\n')
  }

  // Report the feature-scoped catalog size (Roadmap V2 Sprint 108).
  try {
    let totalKeys = 0
    const localeDir = join(I18N_DIR, 'fr')
    for (const file of readdirSync(localeDir)) {
      if (!file.endsWith('.json')) continue
      totalKeys += Object.keys(JSON.parse(readFileSync(join(localeDir, file), 'utf-8'))).length
    }
    console.log(`📊 i18n/fr catalogs contain ${totalKeys} keys (parity enforced by check-i18n-parity.mjs).`)
  } catch (err) {
    console.log('⚠️  Could not read the feature catalogs for a key count.')
  }

  process.exit(filesWithIssues.length > 10 ? 1 : 0)
}

main()
