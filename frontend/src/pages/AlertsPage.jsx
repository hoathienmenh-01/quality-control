import { useState } from 'react'
import { Bell, AlertTriangle, AlertCircle, Info, CheckCircle, Eye, Check } from 'lucide-react'
import { useAlertStore } from '../stores/alertStore'
import Modal from '../components/Modal'
import DataTable from '../components/DataTable'
import { formatDateTime } from '../utils/helpers'

const severityConfig = {
  critical: {
    icon: AlertTriangle,
    bg: 'bg-rose-100',
    text: 'text-rose-700',
    border: 'border-rose-200',
    label: 'Nghiêm trọng',
  },
  warning: {
    icon: AlertCircle,
    bg: 'bg-amber-100',
    text: 'text-amber-700',
    border: 'border-amber-200',
    label: 'Cảnh báo',
  },
  info: {
    icon: Info,
    bg: 'bg-blue-100',
    text: 'text-blue-700',
    border: 'border-blue-200',
    label: 'Thông tin',
  },
}

export default function AlertsPage() {
  const { filterSeverity, setFilterSeverity, markRead, resolve, getFilteredAlerts } = useAlertStore()
  const [selectedAlert, setSelectedAlert] = useState(null)

  const filtered = getFilteredAlerts()
  const unreadCount = filtered.filter((a) => !a.read).length

  const columns = [
    {
      key: 'severity',
      label: 'Mức độ',
      width: '130px',
      render: (val) => {
        const cfg = severityConfig[val] || severityConfig.info
        const Icon = cfg.icon
        return (
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${cfg.bg} ${cfg.text}`}>
            <Icon className="w-3.5 h-3.5" />
            {cfg.label}
          </span>
        )
      },
    },
    {
      key: 'message',
      label: 'Nội dung',
      render: (val, row) => (
        <div>
          <p className={`text-sm ${row.read ? 'text-gray-600' : 'font-semibold text-gray-900'}`}>{val}</p>
          {row.station && <p className="text-xs text-gray-400 mt-0.5">{row.station}</p>}
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Thời gian',
      width: '140px',
      render: (val) => <span className="text-xs text-gray-500">{formatDateTime(val)}</span>,
    },
    {
      key: 'status',
      label: 'Trạng thái',
      width: '120px',
      sortable: false,
      render: (_, row) => (
        <div className="flex items-center gap-2">
          {row.resolved ? (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">
              <CheckCircle className="w-3 h-3" />
              Đã xử lý
            </span>
          ) : row.read ? (
            <span className="text-xs text-gray-400">Đã đọc</span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
              Mới
            </span>
          )}
        </div>
      ),
    },
    {
      key: 'actions',
      label: '',
      sortable: false,
      width: '80px',
      render: (_, row) => (
        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          <button onClick={() => setSelectedAlert(row)} className="p-1.5 hover:bg-gray-100 rounded-lg" title="Chi tiết">
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          {!row.resolved && (
            <button
              onClick={() => resolve(row.id)}
              className="p-1.5 hover:bg-gray-100 rounded-lg"
              title="Đánh dấu đã xử lý"
            >
              <Check className="w-4 h-4 text-emerald-500" />
            </button>
          )}
        </div>
      ),
    },
  ]

  const handleRowClick = (row) => {
    if (!row.read) markRead(row.id)
    setSelectedAlert(row)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cảnh báo</h1>
          <p className="text-gray-600 mt-1">
            {unreadCount > 0 ? `${unreadCount} cảnh báo mới` : 'Tất cả đã đọc'}
          </p>
        </div>
      </div>

      {/* Severity Filter */}
      <div className="flex items-center gap-2">
        {[
          { value: '', label: 'Tất cả' },
          { value: 'critical', label: 'Nghiêm trọng', color: 'rose' },
          { value: 'warning', label: 'Cảnh báo', color: 'amber' },
          { value: 'info', label: 'Thông tin', color: 'blue' },
        ].map((item) => (
          <button
            key={item.value}
            onClick={() => setFilterSeverity(item.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterSeverity === item.value
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Alerts Table */}
      <div className="card !p-0">
        <DataTable columns={columns} data={filtered} pageSize={10} onRowClick={handleRowClick} />
      </div>

      {/* Alert Detail Modal */}
      <Modal isOpen={!!selectedAlert} onClose={() => setSelectedAlert(null)} title="Chi tiết cảnh báo" size="md">
        {selectedAlert && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {(() => {
                const cfg = severityConfig[selectedAlert.severity] || severityConfig.info
                const Icon = cfg.icon
                return (
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${cfg.bg}`}>
                    <Icon className={`w-6 h-6 ${cfg.text}`} />
                  </div>
                )
              })()}
              <div>
                <p className="text-sm text-gray-500">{severityConfig[selectedAlert.severity]?.label}</p>
                <p className="text-sm text-gray-400">{formatDateTime(selectedAlert.created_at)}</p>
              </div>
            </div>
            <div>
              <p className="font-semibold text-gray-900">{selectedAlert.message}</p>
            </div>
            {selectedAlert.station && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Station</p>
                <p className="font-medium">{selectedAlert.station}</p>
              </div>
            )}
            <div className="flex items-center gap-3">
              {!selectedAlert.read && (
                <button onClick={() => markRead(selectedAlert.id)} className="btn btn-secondary flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  Đánh dấu đã đọc
                </button>
              )}
              {!selectedAlert.resolved && (
                <button onClick={() => resolve(selectedAlert.id)} className="btn btn-success flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Đánh dấu đã xử lý
                </button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
