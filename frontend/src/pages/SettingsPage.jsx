import { Settings, Camera, Bell, Database } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Cài đặt</h1>
        <p className="text-gray-600 mt-1">Cấu hình hệ thống</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Camera className="w-6 h-6 text-primary-600" />
            <h2 className="text-lg font-bold text-gray-900">Camera</h2>
          </div>
          <p className="text-gray-600 text-sm">Cấu hình camera, độ phân giải</p>
        </div>
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Bell className="w-6 h-6 text-primary-600" />
            <h2 className="text-lg font-bold text-gray-900">Thông báo</h2>
          </div>
          <p className="text-gray-600 text-sm">Cài đặt Telegram, email alerts</p>
        </div>
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Database className="w-6 h-6 text-primary-600" />
            <h2 className="text-lg font-bold text-gray-900">Database</h2>
          </div>
          <p className="text-gray-600 text-sm">Quản lý database, backup</p>
        </div>
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <Settings className="w-6 h-6 text-primary-600" />
            <h2 className="text-lg font-bold text-gray-900">Hệ thống</h2>
          </div>
          <p className="text-gray-600 text-sm">Cấu hình chung, ngưỡng cảnh báo</p>
        </div>
      </div>
    </div>
  )
}
