import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Package, CheckCircle, XCircle, Activity, Camera, Download, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import { useDashboardStore } from '../stores/dashboardStore'
import { useInspectionStore } from '../stores/inspectionStore'
import DefectTrendChart from '../components/charts/DefectTrendChart'
import PassRateChart from '../components/charts/PassRateChart'
import TopDefectsChart from '../components/charts/TopDefectsChart'
import StationChart from '../components/charts/StationChart'
import DailyStatsChart from '../components/charts/DailyStatsChart'
import StatusBadge from '../components/StatusBadge'
import DataTable from '../components/DataTable'
import { formatDateTime, formatInferenceTime } from '../utils/helpers'

export default function DashboardPage() {
  const { stats } = useDashboardStore()
  const { inspections } = useInspectionStore()
  const navigate = useNavigate()
  const [refreshing, setRefreshing] = useState(false)

  const recentInspections = inspections.slice(0, 10)

  const handleRefresh = () => {
    setRefreshing(true)
    setTimeout(() => setRefreshing(false), 1000)
  }

  const statCards = [
    {
      title: 'Tổng kiểm tra',
      value: stats.total_inspected,
      icon: Package,
      color: 'blue',
      change: '+12%',
      trend: 'up',
    },
    {
      title: 'Đạt (PASS)',
      value: stats.total_passed,
      icon: CheckCircle,
      color: 'green',
      change: '+8%',
      trend: 'up',
    },
    {
      title: 'Lỗi (FAIL)',
      value: stats.total_failed,
      icon: XCircle,
      color: 'red',
      change: '-3%',
      trend: 'down',
    },
    {
      title: 'Tỷ lệ đạt',
      value: `${stats.pass_rate}%`,
      icon: Activity,
      color: 'purple',
      change: '+1.2%',
      trend: 'up',
    },
  ]

  const recentColumns = [
    { key: 'serial_number', label: 'Serial', width: '140px' },
    { key: 'station', label: 'Station', width: '100px' },
    {
      key: 'result',
      label: 'Kết quả',
      width: '100px',
      render: (val) => <StatusBadge status={val} size="xs" />,
    },
    {
      key: 'inference_time',
      label: 'Thời gian',
      width: '100px',
      render: (val) => <span className="text-gray-500 text-xs">{formatInferenceTime(val)}</span>,
    },
    {
      key: 'timestamp',
      label: 'Thời điểm',
      width: '160px',
      render: (val) => <span className="text-gray-500 text-xs">{formatDateTime(val)}</span>,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Tổng quan hệ thống kiểm tra chất lượng</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleRefresh} className="btn btn-secondary flex items-center gap-2">
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Làm mới
          </button>
          <button onClick={() => navigate('/camera')} className="btn btn-primary flex items-center gap-2">
            <Camera className="w-4 h-4" />
            Chụp ảnh
          </button>
          <button onClick={() => navigate('/reports')} className="btn btn-success flex items-center gap-2">
            <Download className="w-4 h-4" />
            Xuất báo cáo
          </button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon
          const colors = {
            blue: 'bg-blue-50 text-blue-600',
            green: 'bg-emerald-50 text-emerald-600',
            red: 'bg-rose-50 text-rose-600',
            purple: 'bg-purple-50 text-purple-600',
          }
          return (
            <div key={card.title} className="card hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value.toLocaleString()}</p>
                  <div className="flex items-center gap-1 mt-1">
                    {card.trend === 'up' ? (
                      <TrendingUp className="w-3 h-3 text-emerald-500" />
                    ) : (
                      <TrendingDown className="w-3 h-3 text-rose-500" />
                    )}
                    <span
                      className={`text-xs font-medium ${
                        card.trend === 'up' ? 'text-emerald-600' : 'text-rose-600'
                      }`}
                    >
                      {card.change}
                    </span>
                  </div>
                </div>
                <div className={`p-3 rounded-xl ${colors[card.color]}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Xu hướng lỗi (30 ngày)</h2>
          <DefectTrendChart />
        </div>
        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Tỷ lệ PASS / FAIL</h2>
          <PassRateChart passCount={stats.total_passed} failCount={stats.total_failed} />
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Top loại lỗi hôm nay</h2>
          <TopDefectsChart />
        </div>
        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-4">So sánh các Station</h2>
          <StationChart />
        </div>
      </div>

      {/* Daily Stats */}
      <div className="card">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Sản lượng & tỷ lệ đạt hàng ngày</h2>
        <DailyStatsChart />
      </div>

      {/* Recent Inspections */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Kiểm tra gần đây</h2>
          <button
            onClick={() => navigate('/inspections')}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Xem tất cả →
          </button>
        </div>
        <DataTable
          columns={recentColumns}
          data={recentInspections}
          pageSize={10}
          onRowClick={(row) => navigate(`/inspections/${row.id}`)}
        />
      </div>
    </div>
  )
}
