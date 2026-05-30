import { useState } from 'react'
import { Download, FileSpreadsheet, FileText, Database, Calendar, MapPin, Eye, Loader2 } from 'lucide-react'
import DataTable from '../components/DataTable'
import { formatDateTime, downloadBlob } from '../utils/helpers'
import { exportAPI } from '../services/api'

// Mock preview data
const MOCK_PREVIEW = Array.from({ length: 8 }, (_, i) => ({
  id: i + 1,
  serial_number: `SN-${String(2024000 + i).padStart(7, '0')}`,
  batch_number: `BATCH-001`,
  station: `Station ${String.fromCharCode(65 + (i % 4))}`,
  result: Math.random() > 0.15 ? 'PASS' : 'FAIL',
  timestamp: new Date(Date.now() - i * 600000).toISOString(),
}))

export default function ReportsPage() {
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [station, setStation] = useState('')
  const [showPreview, setShowPreview] = useState(false)
  const [exporting, setExporting] = useState(null) // 'excel' | 'csv' | 'sql' | null
  const [progress, setProgress] = useState(0)

  const stations = ['Station A', 'Station B', 'Station C', 'Station D']

  const params = {
    ...(dateFrom && { date_from: dateFrom }),
    ...(dateTo && { date_to: dateTo }),
    ...(station && { station }),
  }

  const handleExport = async (format) => {
    setExporting(format)
    setProgress(0)

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 90) {
          clearInterval(interval)
          return 90
        }
        return p + 10
      })
    }, 200)

    try {
      const fn = format === 'excel' ? exportAPI.excel : format === 'csv' ? exportAPI.csv : exportAPI.sql
      const response = await fn(params)
      const ext = format === 'excel' ? 'xlsx' : format
      downloadBlob(response.data, `qc-report.${ext}`)
      setProgress(100)
    } catch {
      setProgress(100)
    } finally {
      clearInterval(interval)
      setTimeout(() => {
        setExporting(null)
        setProgress(0)
      }, 1500)
    }
  }

  const previewColumns = [
    { key: 'serial_number', label: 'Serial', render: (v) => <span className="font-mono text-xs">{v}</span> },
    { key: 'batch_number', label: 'Batch' },
    { key: 'station', label: 'Station' },
    {
      key: 'result',
      label: 'Kết quả',
      render: (v) => (
        <span className={`badge ${v === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>{v}</span>
      ),
    },
    {
      key: 'timestamp',
      label: 'Thời điểm',
      render: (v) => <span className="text-xs text-gray-500">{formatDateTime(v)}</span>,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Báo cáo</h1>
        <p className="text-gray-600 mt-1">Xem trước và xuất báo cáo kiểm tra</p>
      </div>

      {/* Filters */}
      <div className="card">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Bộ lọc báo cáo</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1.5">
              <Calendar className="w-4 h-4" /> Từ ngày
            </label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1.5">
              <Calendar className="w-4 h-4" /> Đến ngày
            </label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1.5">
              <MapPin className="w-4 h-4" /> Station
            </label>
            <select value={station} onChange={(e) => setStation(e.target.value)} className="input">
              <option value="">Tất cả</option>
              {stations.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={() => setShowPreview(true)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <Eye className="w-4 h-4" />
            Xem trước dữ liệu
          </button>
          <button
            onClick={() => {
              setDateFrom('')
              setDateTo('')
              setStation('')
              setShowPreview(false)
            }}
            className="btn btn-secondary"
          >
            Xóa bộ lọc
          </button>
        </div>
      </div>

      {/* Preview */}
      {showPreview && (
        <div className="card animate-fade-in">
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Xem trước dữ liệu ({MOCK_PREVIEW.length} bản ghi)
          </h2>
          <DataTable columns={previewColumns} data={MOCK_PREVIEW} pageSize={5} />
        </div>
      )}

      {/* Export Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            format: 'excel',
            title: 'Export Excel',
            desc: 'Xuất báo cáo dạng .xlsx với định dạng đẹp',
            icon: FileSpreadsheet,
            color: 'text-emerald-500',
            bg: 'hover:border-emerald-300',
          },
          {
            format: 'csv',
            title: 'Export CSV',
            desc: 'Xuất dữ liệu thô dạng CSV để phân tích',
            icon: FileText,
            color: 'text-blue-500',
            bg: 'hover:border-blue-300',
          },
          {
            format: 'sql',
            title: 'Export SQL',
            desc: 'Xuất database dump dạng SQL',
            icon: Database,
            color: 'text-purple-500',
            bg: 'hover:border-purple-300',
          },
        ].map((item) => {
          const Icon = item.icon
          const isExporting = exporting === item.format
          return (
            <button
              key={item.format}
              onClick={() => handleExport(item.format)}
              disabled={!!exporting}
              className={`card text-left transition-all ${item.bg} ${
                isExporting ? 'ring-2 ring-primary-500' : ''
              } disabled:opacity-60 disabled:cursor-not-allowed`}
            >
              <Icon className={`w-8 h-8 ${item.color} mb-3`} />
              <h3 className="font-bold text-gray-900">{item.title}</h3>
              <p className="text-sm text-gray-600 mt-1">{item.desc}</p>

              {isExporting && (
                <div className="mt-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                    <span className="text-sm text-primary-600 font-medium">
                      {progress < 100 ? 'Đang xuất...' : 'Hoàn thành!'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
