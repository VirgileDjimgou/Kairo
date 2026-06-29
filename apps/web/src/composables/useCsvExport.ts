import { ref } from 'vue'

export function useCsvExport() {
  const exporting = ref(false)

  async function exportCsv(fetchFn: () => Promise<Blob>, filename: string): Promise<void> {
    exporting.value = true
    try {
      const blob = await fetchFn()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } finally {
      exporting.value = false
    }
  }

  return { exportCsv, exporting }
}
