export function memberErrorMessage(err: unknown): string {
  const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
  if (detail) return detail
  if (err instanceof Error && err.message) return err.message
  return 'An unexpected error occurred'
}
