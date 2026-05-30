/**
 * WebSocket Service — Real-time alert connection
 */

class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Set()
    this.reconnectTimer = null
    this.reconnectDelay = 1000
    this.maxReconnectDelay = 30000
    this.isConnected = false
  }

  /**
   * Kết nối WebSocket server
   * @param {string} url - WebSocket URL (default: ws://host/ws/alerts)
   */
  connect(url) {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    const wsUrl = url || this._getDefaultUrl()
    console.log('[WS] Connecting to', wsUrl)

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('[WS] Connected')
      this.isConnected = true
      this.reconnectDelay = 1000
      this._notify({ type: 'connected' })
      this._startPing()
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'pong') return
        console.log('[WS] Alert received:', data)
        this._notify(data)
      } catch (e) {
        console.warn('[WS] Invalid message:', event.data)
      }
    }

    this.ws.onclose = (event) => {
      console.log('[WS] Disconnected:', event.code, event.reason)
      this.isConnected = false
      this._stopPing()
      this._notify({ type: 'disconnected' })
      this._scheduleReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('[WS] Error:', error)
    }
  }

  /**
   * Ngắt kết nối
   */
  disconnect() {
    this._stopPing()
    clearTimeout(this.reconnectTimer)
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isConnected = false
  }

  /**
   * Đăng ký listener để nhận alert events
   * @param {Function} callback - Hàm gọi khi có alert
   * @returns {Function} unsubscribe function
   */
  subscribe(callback) {
    this.listeners.add(callback)
    return () => this.listeners.delete(callback)
  }

  /**
   * Gửi message đến server (ping)
   */
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }

  // ── Private ──

  _getDefaultUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}/ws/alerts`
  }

  _notify(data) {
    for (const cb of this.listeners) {
      try {
        cb(data)
      } catch (e) {
        console.error('[WS] Listener error:', e)
      }
    }
  }

  _startPing() {
    this._stopPing()
    this.pingInterval = setInterval(() => {
      this.send('ping')
    }, 30000)
  }

  _stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  _scheduleReconnect() {
    clearTimeout(this.reconnectTimer)
    console.log(`[WS] Reconnecting in ${this.reconnectDelay / 1000}s...`)
    this.reconnectTimer = setTimeout(() => {
      this.connect()
    }, this.reconnectDelay)
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay)
  }
}

// Singleton
export const wsService = new WebSocketService()
export default wsService
