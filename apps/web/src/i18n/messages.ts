import { fr } from './fr'
import { en } from './en'
import { de } from './de'

export type SupportedLocale = 'fr' | 'en' | 'de'

type MessageDictionary = Record<SupportedLocale, Record<string, string>>

/**
 * Feature-scoped catalogs (Roadmap V2 Sprint 108).
 *
 * Product copy lives in `i18n/<locale>/<feature>.json` and is composed here;
 * `scripts/check-i18n-parity.mjs` enforces identical FR/EN/DE key sets in CI.
 */
export const messages: MessageDictionary = { fr, en, de }
