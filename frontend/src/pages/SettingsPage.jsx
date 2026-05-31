import { useState, useEffect } from 'react'
import {
  Settings,
  Camera,
  Bell,
  Database,
  Shield,
  Save,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Wifi,
  Server,
} from 'lucide-react'
import { cameraAPI } from '../services/api'

const SECTIONS = [
  { key: 'camera', label: 'Camera', icon: Camera },
  { key: 'alerts', label: 'Cảnh báo', icon: Bell },
  { key: 'system', label: 'Hệ thống', icon: Server },
]

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('camera')
  const [saved, setSaved] = useState(false)

  // Camera settings
  const [cameraSettings, setCameraSettings] = useState({
    resolution: '1920x1080',
    fps: 30,
    autoCapture: false,
    cameraId: 0,
  })

  // Alert settings
  const [alertSettings, setAlertSettings] = useState({
    telegramEnabled: false,
    telegramBotToken: '',
    telegramChatId: '',
    consecutiveFailThreshold: 5,
    alertThresholdRate: 10,
  })

  // System info
  const [systemInfo, setSystemInfo] = useState({
    connected: false,
    cameraStatus: 'Chưa kết nối',
    lastCapture: null,
  })

  // Load camera status
  useEffect(() => {
    cameraAPI.status().then((res) => {
      setSystemInfo((s) => ({
        ...s,
        connected: res.data.connected,
        cameraStatus: res.data.connected ? 'Đã kết nối' : 'Chưa kết nối',
        lastCapture: res.data.last_capture,
      }))
      setCameraSettings((s) => ({
        ...s,
        cameraId: res.data.camera_id,
        resolution: `${res.data.resolution[0]}x${res.data.resolution[1]}`,
      }))
    }).catch(() => {})
  }, [])

  const handleSave = () => {
    // Save to localStorage for persistence
    localStorage.setItem('qc_camera_settings', JSON.stringify(cameraSettings))
    localStorage.setItem('qc_alert_settings', JSON.stringify(alertSettings))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const cs = localStorage.getItem('qc_camera_settings')
      if (cs) setCameraSettings(JSON.parse(cs))
      const as = localStorage.getItem('qc_alert_settings')
      if (as) setAlertSettings(JSON.parse(as))
    } catch {}
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cài đặt</h1>
          <p className="text-gray-600 mt-1">Cấu hình hệ thống kiểm tra chất lượng</p>
        </div>
        <button
          onClick={handleSave}
          className="btn btn-primary flex items-center gap-2"
        >
          {saved ? (
            <>
              <CheckCircle className="w-4 h-4" />
              Đã lưu
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Lưu cài đặt
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar navigation */}
        <div className="space-y-1">
          {SECTIONS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveSection(key)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                activeSection === key
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Icon className="w-5 h-5" />
              {label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Camera Settings */}
          {activeSection === 'camera' && (
            <div className="space-y-6">
              <div className="card">
                <div className="flex items-center gap-3 mb-6">
                  <Camera className="w-6 h-6 text-primary-600" />
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Cấu hình Camera</h2>
                    <p className="text-sm text-gray-500">Điều chỉnh thông số camera chụp sản phẩm</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm text-gray-600">Trạng thái</span>
                    <span className={`badge ${systemInfo.connected ? 'badge-pass' : 'badge-fail'}`}>
                      {systemInfo.cameraStatus}
                    </span>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Camera ID
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={cameraSettings.cameraId}
                      onChange={(e) =>
                        setCameraSettings({ ...cameraSettings, cameraId: Number(e.target.value) })
                      }
                      className="input"
                    />
                    <p className="text-xs text-gray-400 mt-1">Số thứ tự camera (0 = webcam mặc định)</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Độ phân giải
                    </label>
                    <select
                      value={cameraSettings.resolution}
                      onChange={(e) =>
                        setCameraSettings({ ...cameraSettings, resolution: e.target.value })
                      }
                      className="input"
                    >
                      <option value="640x480">640 × 480 (VGA)</option>
                      <option value="1280x720">1280 × 720 (HD)</option>
                      <option value="1920x1080">1920 × 1080 (Full HD)</option>
                      <option value="2560x1440">2560 × 1440 (2K)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      FPS
                    </label>
                    <select
                      value={cameraSettings.fps}
                      onChange={(e) =>
                        setCameraSettings({ ...cameraSettings, fps: Number(e.target.value) })
                      }
                      className="input"
                    >
                      <option value="15">15 FPS</option>
                      <option value="24">24 FPS</option>
                      <option value="30">30 FPS</option>
                      <option value="60">60 FPS</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <input
                      type="checkbox"
                      id="auto-capture"
                      checked={cameraSettings.autoCapture}
                      onChange={(e) =>
                        setCameraSettings({ ...cameraSettings, autoCapture: e.target.checked })
                      }
                      className="w-4 h-4 text-primary-600 rounded"
                    />
                    <div>
                      <label htmlFor="auto-capture" className="text-sm font-medium text-gray-700">
                        Tự động chụp khi phát hiện sản phẩm
                      </label>
                      <p className="text-xs text-gray-400">
                        Kích hoạt chế độ chụp tự động trên conveyor
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Alert Settings */}
          {activeSection === 'alerts' && (
            <div className="space-y-6">
              <div className="card">
                <div className="flex items-center gap-3 mb-6">
                  <Bell className="w-6 h-6 text-primary-600" />
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Cài đặt cảnh báo</h2>
                    <p className="text-sm text-gray-500">Cấu hình Telegram và ngưỡng cảnh báo</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <input
                      type="checkbox"
                      id="telegram-enabled"
                      checked={alertSettings.telegramEnabled}
                      onChange={(e) =>
                        setAlertSettings({ ...alertSettings, telegramEnabled: e.target.checked })
                      }
                      className="w-4 h-4 text-primary-600 rounded"
                    />
                    <div>
                      <label htmlFor="telegram-enabled" className="text-sm font-medium text-gray-700">
                        Bật thông báo Telegram
                      </label>
                      <p className="text-xs text-gray-400">
                        Gửi cảnh báo real-time qua Telegram khi sản phẩm lỗi
                      </p>
                    </div>
                  </div>

                  {alertSettings.telegramEnabled && (
                    <div className="space-y-4 pl-7 animate-fade-in">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Bot Token
                        </label>
                        <input
                          type="password"
                          value={alertSettings.telegramBotToken}
                          onChange={(e) =>
                            setAlertSettings({ ...alertSettings, telegramBotToken: e.target.value })
                          }
                          placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                          className="input"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                          Lấy từ @BotFather trên Telegram
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Chat ID
                        </label>
                        <input
                          type="text"
                          value={alertSettings.telegramChatId}
                          onChange={(e) =>
                            setAlertSettings({ ...alertSettings, telegramChatId: e.target.value })
                          }
                          placeholder="-1001234567890"
                          className="input"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                          ID nhóm hoặc cá nhân nhận thông báo
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="border-t pt-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Ngưỡng cảnh báo</h3>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Số lỗi liên tiếp để cảnh báo khẩn cấp
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="100"
                          value={alertSettings.consecutiveFailThreshold}
                          onChange={(e) =>
                            setAlertSettings({
                              ...alertSettings,
                              consecutiveFailThreshold: Number(e.target.value),
                            })
                          }
                          className="input w-32"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                          Cảnh báo critical khi có N sản phẩm lỗi liên tiếp tại cùng trạm
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Tỷ lệ lỗi cảnh báo (%)
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="100"
                          value={alertSettings.alertThresholdRate}
                          onChange={(e) =>
                            setAlertSettings({
                              ...alertSettings,
                              alertThresholdRate: Number(e.target.value),
                            })
                          }
                          className="input w-32"
                        />
                        <p className="text-xs text-gray-400 mt-1">
                          Cảnh báo khi tỷ lệ lỗi vượt quá ngưỡng trong 50 inspection gần nhất
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* System Settings */}
          {activeSection === 'system' && (
            <div className="space-y-6">
              <div className="card">
                <div className="flex items-center gap-3 mb-6">
                  <Server className="w-6 h-6 text-primary-600" />
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Thông tin hệ thống</h2>
                    <p className="text-sm text-gray-500">Trạng thái các thành phần</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <InfoRow label="Phiên bản" value="v1.0.0" />
                  <InfoRow label="Backend" value="FastAPI + Python" />
                  <InfoRow label="Frontend" value="React + Vite" />
                  <InfoRow label="Database" value="PostgreSQL" />
                  <InfoRow label="CV Engine" value="OpenCV" />
                  <InfoRow
                    label="WebSocket"
                    value="Đã kết nối"
                    status="ok"
                  />
                  <InfoRow
                    label="Lần chụp cuối"
                    value={systemInfo.lastCapture || 'Chưa có'}
                  />
                </div>
              </div>

              <div className="card">
                <div className="flex items-center gap-3 mb-6">
                  <Shield className="w-6 h-6 text-primary-600" />
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Bảo mật</h2>
                    <p className="text-sm text-gray-500">Cấu hình bảo mật hệ thống</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <InfoRow label="Xác thực" value="JWT (bcrypt)" status="ok" />
                  <InfoRow label="Rate Limiting" value="5 lần / 5 phút" status="ok" />
                  <InfoRow label="Input Validation" value="Bật" status="ok" />
                  <InfoRow label="Audit Logging" value="Bật" status="ok" />
                  <InfoRow label="CORS" value="Hạn chế origins" status="ok" />
                  <InfoRow label="Security Headers" value="Bật" status="ok" />
                </div>
              </div>

              <div className="card border-amber-200 bg-amber-50">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-semibold text-amber-800">Lưu ý</h3>
                    <p className="text-sm text-amber-700 mt-1">
                      Cài đặt được lưu vào localStorage trình duyệt. Để thay đổi cấu hình backend,
                      chỉnh sửa file <code className="bg-amber-100 px-1 rounded">.env</code> trên server.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value, status }) {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <span className="text-sm text-gray-600">{label}</span>
      <div className="flex items-center gap-2">
        {status === 'ok' && <CheckCircle className="w-4 h-4 text-emerald-500" />}
        <span className="text-sm font-medium text-gray-900">{value}</span>
      </div>
    </div>
  )
}
