/**
 * Format số thành chuỗi có dấu phân cách
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return num.toLocaleString('vi-VN')
}

/**
 * Format timestamp thành chuỗi dễ đọc
 */
export function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format thời gian inference
 */
export function formatInferenceTime(ms) {
  if (ms < 1000) return `${Math.round(ms)}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

/**
 * Lấy màu cho kết quả PASS/FAIL
 */
export function getResultColor(result) {
  switch (result) {
    case 'PASS':
      return 'text-emerald-600 bg-emerald-50'
    case 'FAIL':
      return 'text-rose-600 bg-rose-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

/**
 * Download file từ blob
 */
export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
