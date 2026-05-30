import { Bell } from 'lucide-react'

export default function AlertsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Cảnh báo</h1>
        <p className="text-gray-600 mt-1">Danh sách cảnh báo từ hệ thống</p>
      </div>
      <div className="card">
        <div className="text-gray-400 text-center py-12">
          <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Không có cảnh báo nào</p>
        </div>
      </div>
    </div>
  )
}
