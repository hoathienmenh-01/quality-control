import { useState, useEffect, useRef } from 'react'
import { Camera, CameraOff, Wifi, WifiOff, Settings, Aperture, RefreshCw } from 'lucide-react'
import { cameraAPI } from '../services/api'

export default function CameraPage() {
  const [connected, setConnected] = useState(false)
  const [capturing, setCapturing] = useState(false)
  const [lastCapture, setLastCapture] = useState(null)
  const [settings, setSettings] = useState({
    resolution: '1920x1080',
    fps: 30,
    autoCapture: false,
  })
  const [showSettings, setShowSettings] = useState(false)
  const canvasRef = useRef(null)

  // Simulate camera feed with canvas animation
  useEffect(() => {
    if (!connected || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    canvas.width = 640
    canvas.height = 480

    let frame = 0
    const interval = setInterval(() => {
      frame++
      // Simulated camera noise pattern
      const imageData = ctx.createImageData(640, 480)
      for (let i = 0; i < imageData.data.length; i += 4) {
        const px = (i / 4) % 640
        const py = Math.floor(i / 4 / 640)
        const noise = Math.random() * 30
        // Create a gradient background with some structure
        const base = 40 + Math.sin(px / 50 + frame / 20) * 20 + Math.cos(py / 30 + frame / 15) * 15
        imageData.data[i] = base + noise + 20     // R
        imageData.data[i + 1] = base + noise + 10 // G
        imageData.data[i + 2] = base + noise + 30 // B
        imageData.data[i + 3] = 255               // A
      }
      ctx.putImageData(imageData, 0, 0)

      // Draw crosshair
      ctx.strokeStyle = 'rgba(255,255,255,0.3)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(320, 0)
      ctx.lineTo(320, 480)
      ctx.moveTo(0, 240)
      ctx.lineTo(640, 240)
      ctx.stroke()

      // Draw timestamp
      ctx.fillStyle = 'rgba(255,255,255,0.7)'
      ctx.font = '12px monospace'
      ctx.fillText(new Date().toLocaleTimeString(), 10, 20)
      ctx.fillText(`FPS: ${settings.fps}`, 10, 36)
    }, 1000 / 15) // ~15fps for demo

    return () => clearInterval(interval)
  }, [connected, settings.fps])

  const handleConnect = async () => {
    if (connected) {
      setConnected(false)
      return
    }
    try {
      await cameraAPI.connect({ resolution: settings.resolution, fps: settings.fps })
    } catch {}
    setConnected(true)
  }

  const handleCapture = async () => {
    setCapturing(true)
    try {
      await cameraAPI.capture()
    } catch {}
    setLastCapture(new Date().toLocaleTimeString())
    setCapturing(false)
  }

  const resolutions = ['640x480', '1280x720', '1920x1080', '2560x1440']
  const fpsOptions = [15, 24, 30, 60]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Camera</h1>
          <p className="text-gray-600 mt-1">Quản lý camera và chụp ảnh sản phẩm</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings((s) => !s)}
            className={`btn flex items-center gap-2 ${showSettings ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Settings className="w-4 h-4" />
            Cài đặt
          </button>
          <button
            onClick={handleConnect}
            className={`btn flex items-center gap-2 ${connected ? 'btn-danger' : 'btn-success'}`}
          >
            {connected ? (
              <>
                <WifiOff className="w-4 h-4" />
                Ngắt kết nối
              </>
            ) : (
              <>
                <Wifi className="w-4 h-4" />
                Kết nối
              </>
            )}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Camera Preview */}
        <div className="lg:col-span-2 card !p-0 overflow-hidden">
          <div className="aspect-video bg-gray-900 relative">
            {connected ? (
              <canvas ref={canvasRef} className="w-full h-full object-contain" />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-center">
                  <CameraOff className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 text-lg">Camera chưa kết nối</p>
                  <p className="text-gray-500 text-sm mt-1">Nhấn "Kết nối" để bắt đầu</p>
                </div>
              </div>
            )}

            {/* Connection indicator */}
            <div className="absolute top-4 left-4 flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-gray-500'}`} />
              <span className="text-white text-sm font-medium">
                {connected ? 'Đang kết nối' : 'Ngắt kết nối'}
              </span>
            </div>

            {/* Capture flash */}
            {capturing && (
              <div className="absolute inset-0 bg-white animate-pulse" style={{ animationDuration: '0.2s' }} />
            )}
          </div>

          {/* Controls */}
          <div className="p-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={handleCapture}
                disabled={!connected || capturing}
                className="btn btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Aperture className="w-5 h-5" />
                {capturing ? 'Đang chụp...' : 'Chụp ảnh'}
              </button>
              {lastCapture && (
                <span className="text-sm text-gray-500">
                  Chụp lần cuối: {lastCapture}
                </span>
              )}
            </div>
            <button
              onClick={() => setConnected((c) => !c)}
              disabled
              className="btn btn-secondary flex items-center gap-2 opacity-50"
            >
              <RefreshCw className="w-4 h-4" />
              Tự động chụp
            </button>
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          {/* Connection Status */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Trạng thái kết nối</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Camera</span>
                <span className={`badge ${connected ? 'badge-pass' : 'badge-fail'}`}>
                  {connected ? 'Đã kết nối' : 'Chưa kết nối'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Độ phân giải</span>
                <span className="text-sm font-medium">{settings.resolution}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">FPS</span>
                <span className="text-sm font-medium">{settings.fps}</span>
              </div>
            </div>
          </div>

          {/* Settings */}
          {showSettings && (
            <div className="card animate-fade-in">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Cài đặt Camera</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Độ phân giải</label>
                  <select
                    value={settings.resolution}
                    onChange={(e) => setSettings({ ...settings, resolution: e.target.value })}
                    className="input"
                  >
                    {resolutions.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">FPS</label>
                  <select
                    value={settings.fps}
                    onChange={(e) => setSettings({ ...settings, fps: Number(e.target.value) })}
                    className="input"
                  >
                    {fpsOptions.map((f) => (
                      <option key={f} value={f}>
                        {f} FPS
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="auto-capture"
                    checked={settings.autoCapture}
                    onChange={(e) => setSettings({ ...settings, autoCapture: e.target.checked })}
                    className="w-4 h-4 text-primary-600 rounded"
                  />
                  <label htmlFor="auto-capture" className="text-sm text-gray-700">
                    Tự động chụp khi phát hiện sản phẩm
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Quick Tips */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Hướng dẫn</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <span className="text-primary-600 font-bold">1.</span>
                Đảm bảo camera đã kết nối đúng cổng
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 font-bold">2.</span>
                Điều chỉnh góc camera để thấy toàn bộ sản phẩm
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 font-bold">3.</span>
                Nhấn "Chụp ảnh" khi sản phẩm sẵn sàng
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
