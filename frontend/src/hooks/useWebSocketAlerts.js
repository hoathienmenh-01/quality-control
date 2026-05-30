/**
 * useWebSocketAlerts — Hook để nhận real-time alerts qua WebSocket
 */

import { useEffect, useRef, useState, useCallback } from 'react'
import wsService from '../services/websocket'

/**
 * Hook kết nối WebSocket và trả về alerts real-time
 * @param {Object} options
 * @param {Function} options.onAlert - Callback khi có alert mới
 * @param {boolean} options.autoConnect - Tự động kết nối (default: true)
 * @returns {{ isConnected: boolean, toasts: Array, dismissToast: Function }}
 */
export function useWebSocketAlerts({ onAlert, autoConnect = true } = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [toasts, setToasts] = useState([])
  const toastIdRef = useRef(0)

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  useEffect(() => {
    if (!autoConnect) return

    const unsubscribe = wsService.subscribe((data) => {
      if (data.type === 'connected') {
        setIsConnected(true)
        return
      }
      if (data.type === 'disconnected') {
        setIsConnected(false)
        return
      }

      // Alert received
      if (data.type === 'alert') {
        const toastId = ++toastIdRef.current
        const toast = {
          id: toastId,
          severity: data.severity,
          title: data.title,
          message: data.message,
          station_id: data.station_id,
          timestamp: data.created_at || new Date().toISOString(),
        }

        setToasts((prev) => [...prev.slice(-4), toast]) // Giữ tối đa 5 toast

        // Tự động dismiss sau 10s (critical) hoặc 7s (warning)
        const duration = data.severity === 'critical' ? 10000 : 7000
        setTimeout(() => dismissToast(toastId), duration)

        // Gọi callback nếu có
        if (onAlert) onAlert(data)
      }
    })

    wsService.connect()

    return () => {
      unsubscribe()
    }
  }, [autoConnect, onAlert, dismissToast])

  return { isConnected, toasts, dismissToast }
}

export default useWebSocketAlerts
