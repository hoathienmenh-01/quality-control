/**
 * AlertToast — Hiển thị cảnh báo real-time dạng toast popup
 */

import { useEffect, useState } from 'react'

const SEVERITY_CONFIG = {
  critical: {
    bg: 'bg-red-600',
    border: 'border-red-800',
    icon: '🔴',
    pulse: true,
  },
  warning: {
    bg: 'bg-yellow-500',
    border: 'border-yellow-700',
    icon: '🟡',
    pulse: false,
  },
  info: {
    bg: 'bg-blue-500',
    border: 'border-blue-700',
    icon: 'ℹ️',
    pulse: false,
  },
}

function AlertToast({ toast, onDismiss }) {
  const [isExiting, setIsExiting] = useState(false)
  const config = SEVERITY_CONFIG[toast.severity] || SEVERITY_CONFIG.info

  const handleDismiss = () => {
    setIsExiting(true)
    setTimeout(() => onDismiss(toast.id), 300)
  }

  return (
    <div
      className={`
        ${config.bg} ${config.border} ${config.pulse ? 'animate-pulse-slow' : ''}
        border-l-4 rounded-lg shadow-2xl p-4 mb-3 min-w-[340px] max-w-[420px]
        transform transition-all duration-300 ease-out
        ${isExiting ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
      `}
      role="alert"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <span className="text-xl mt-0.5 flex-shrink-0">{config.icon}</span>
          <div className="flex-1 min-w-0">
            <p className="font-bold text-white text-sm leading-tight">
              {toast.title}
            </p>
            <p className="text-white/90 text-xs mt-1 whitespace-pre-line leading-relaxed">
              {toast.message}
            </p>
            {toast.station_id && (
              <span className="inline-block mt-2 px-2 py-0.5 bg-black/20 rounded text-xs text-white/80">
                📍 {toast.station_id}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={handleDismiss}
          className="text-white/70 hover:text-white ml-2 flex-shrink-0 text-lg leading-none"
        >
          ×
        </button>
      </div>
    </div>
  )
}

/**
 * AlertToastContainer — Container hiển thị tất cả toast alerts
 */
export function AlertToastContainer({ toasts, onDismiss }) {
  if (!toasts || toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col items-end">
      {toasts.map((toast) => (
        <AlertToast key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

export default AlertToastContainer
