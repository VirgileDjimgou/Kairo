/**
 * Portfolio demo configuration.
 *
 * The public `/demo` entry point lets a visitor explore Kairo with a single
 * click. Accounts are resolved from `VITE_DEMO_ACCOUNTS` (a JSON array) so a
 * deployment can point the demo at its own rotated credentials without a code
 * change. When the variable is absent the documented seed accounts are used.
 *
 * Demo mode is on unless `VITE_DEMO_MODE` is explicitly set to "false".
 */

export interface DemoAccount {
  key: string
  email: string
  password: string
  icon: string
  roleLabelKey: string
  descriptionKey: string
  /** Advanced roles stay collapsed and are aimed at a guided walkthrough. */
  advanced: boolean
}

export const DEMO_TENANT_SLUG = import.meta.env.VITE_DEMO_TENANT_SLUG || 'demo'

export const IS_DEMO_MODE = (import.meta.env.VITE_DEMO_MODE ?? 'true') !== 'false'

const DEFAULT_ACCOUNTS: DemoAccount[] = [
  {
    key: 'member',
    email: 'alice@demo.org',
    password: 'Member123!',
    icon: 'bi-person',
    roleLabelKey: 'demo.role.member',
    descriptionKey: 'demo.roleDesc.member',
    advanced: false,
  },
  {
    key: 'president',
    email: 'president@demo.org',
    password: 'President123!',
    icon: 'bi-bank',
    roleLabelKey: 'demo.role.president',
    descriptionKey: 'demo.roleDesc.president',
    advanced: false,
  },
  {
    key: 'treasurer',
    email: 'treasurer@demo.org',
    password: 'Treasurer123!',
    icon: 'bi-cash-stack',
    roleLabelKey: 'demo.role.treasurer',
    descriptionKey: 'demo.roleDesc.treasurer',
    advanced: false,
  },
  {
    key: 'secretary_general',
    email: 'secretary@demo.org',
    password: 'Secretary123!',
    icon: 'bi-journal-richtext',
    roleLabelKey: 'demo.role.secretary_general',
    descriptionKey: 'demo.roleDesc.secretary_general',
    advanced: false,
  },
  {
    key: 'auditor',
    email: 'auditor@demo.org',
    password: 'Auditor123!',
    icon: 'bi-clipboard-data',
    roleLabelKey: 'demo.role.auditor',
    descriptionKey: 'demo.roleDesc.auditor',
    advanced: false,
  },
  {
    key: 'censor',
    email: 'censor@demo.org',
    password: 'Censor123!',
    icon: 'bi-shield-lock',
    roleLabelKey: 'demo.role.censor',
    descriptionKey: 'demo.roleDesc.censor',
    advanced: false,
  },
  {
    key: 'sports_manager',
    email: 'sports@demo.org',
    password: 'Sports123!',
    icon: 'bi-trophy',
    roleLabelKey: 'demo.role.sports_manager',
    descriptionKey: 'demo.roleDesc.sports_manager',
    advanced: false,
  },
  {
    key: 'vice_president',
    email: 'vice-president@demo.org',
    password: 'VicePresident123!',
    icon: 'bi-diagram-3',
    roleLabelKey: 'demo.role.vice_president',
    descriptionKey: 'demo.roleDesc.vice_president',
    advanced: true,
  },
]

function parseAccountOverride(raw: string | undefined): DemoAccount[] | null {
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw) as unknown
    if (!Array.isArray(parsed)) return null
    const accounts = parsed.filter(
      (item): item is DemoAccount =>
        typeof item === 'object' &&
        item !== null &&
        typeof (item as DemoAccount).key === 'string' &&
        typeof (item as DemoAccount).email === 'string' &&
        typeof (item as DemoAccount).password === 'string',
    )
    return accounts.length > 0 ? accounts : null
  } catch {
    return null
  }
}

/**
 * Demo accounts may be provided either as raw JSON (`VITE_DEMO_ACCOUNTS`) or
 * base64-encoded (`VITE_DEMO_ACCOUNTS_B64`). The base64 form survives Docker
 * build-arg and env-file quoting, so production uses it for rotated passwords.
 */
function resolveAccountsPayload(): string | undefined {
  const encoded = import.meta.env.VITE_DEMO_ACCOUNTS_B64
  if (encoded) {
    try {
      return atob(encoded)
    } catch {
      return undefined
    }
  }
  return import.meta.env.VITE_DEMO_ACCOUNTS
}

export const DEMO_ACCOUNTS: DemoAccount[] =
  parseAccountOverride(resolveAccountsPayload()) ?? DEFAULT_ACCOUNTS

export function primaryDemoAccounts(): DemoAccount[] {
  return DEMO_ACCOUNTS.filter((account) => !account.advanced)
}

export function advancedDemoAccounts(): DemoAccount[] {
  return DEMO_ACCOUNTS.filter((account) => account.advanced)
}
