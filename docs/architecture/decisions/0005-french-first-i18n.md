# ADR-005: French-First Internationalization With Three Locales

Status: Accepted

## Context

The association operates in French, with English and German stakeholders.

## Decision

The UI contract is French-first, English-second, German-third. All user-facing
strings live in feature-scoped i18n catalogs
(`apps/web/src/i18n/<locale>/<feature>.json`, composed by `messages.ts`) with
keys present in all three locales; templates use `localeStore.t('key')`, and
user-visible enum values are resolved through mapping keys. Backend enum
identifiers are not translated.

## Consequences

- Key parity across FR/EN/DE is enforced by `scripts/check-i18n-parity.mjs`
  (CI, blocking) plus the Playwright localization pack; the advisory
  `scripts/check-i18n-coverage.mjs` reports potential hardcoded strings.
- Roadmap V2 S108 delivered the feature-scoped split (11 feature catalogs,
  exact FR/EN/DE parity) and removed the inline locale ternaries from the
  finance and dashboard feature modules; the locale contract itself did not
  change and existing language selection still persists through
  `localeStore`.
