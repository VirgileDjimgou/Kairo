import { ref } from 'vue'
import {
  listExpenseCategories,
  type ExpenseCategoryResponse,
} from '@/api/contributions.api'

const categories = ref<ExpenseCategoryResponse[]>([])
let pending: Promise<void> | null = null

/**
 * Shared tenant expense categories. The finance workspace, the ledger and the
 * budget plan all display the same codes, so one module-level cache avoids
 * duplicate requests and keeps custom names available to the formatters.
 */
export function useExpenseCategories() {
  async function ensureLoaded(force = false): Promise<void> {
    if (!force && categories.value.length > 0) return
    if (pending) return pending
    pending = listExpenseCategories()
      .then((rows) => {
        categories.value = rows
      })
      .finally(() => {
        pending = null
      })
    return pending
  }

  function nameFor(code: string): string {
    return categories.value.find((category) => category.code === code)?.name ?? ''
  }

  return { categories, ensureLoaded, nameFor }
}
