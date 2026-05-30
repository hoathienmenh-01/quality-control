import { useState } from 'react'
import { Package, CheckCircle, XCircle, Activity } from 'lucide-react'

export default function DashboardPage() {
  const [stats] = useState({
    total_inspected: 1250,
    total_passed: 1180,
    total_failed: 70,
    pass_rate: 94.4,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Tổng quan hệ thống kiểm tra chất lượng</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Tổng kiểm tra" value={stats.total_inspected} icon={Package} color="blue" />
        <StatCard title="Đạt (PASS)" value={stats.total_passed} icon={CheckCircle} color="green" />
        <StatCard title="Lỗi (FAIL)" value={stats.total_failed} icon={XCircle} color="red" />
        <StatCard title="Tỷ lệ đạt" value={`${stats.pass_rate}%`} icon={Activity} color="purple" />
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Xu hướng lỗi (30 ngày)</h2>
        <div className="h-64 flex items-center justify-center text-gray-400">
          Biểu đồ sẽ được cập nhật khi có dữ liệu
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Kiểm tra gần đây</h2>
        <div className="text-gray-400 text-center py-8">
          Chưa có dữ liệu kiểm tra
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-emerald-50 text-emerald-600',
    red: 'bg-rose-50 text-rose-600',
    purple: 'bg-purple-50 text-purple-600',
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}
