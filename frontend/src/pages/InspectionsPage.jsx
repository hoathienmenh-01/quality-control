import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Filter, Download, ChevronDown, X } from 'lucide-react'
import { useInspectionStore } from '../stores/inspectionStore'
import DataTable from '../components/DataTable'
import StatusBadge from '../components/StatusBadge'
import { formatDateTime, formatInferenceTime, downloadBlob } from '../utils/helpers'
import { exportAPI } from '../services/api'

export default function InspectionsPage() {
  const navigate = useNavigate()
  const { inspections, filters, setFilters, getFilteredInspections } = useInspectionStore()
  const [showFilters, setShowFilters] = useState(false)
  const [exporting, setExporting] = useState(false)

  const filtered = getFilteredInspections()
  const stations = [...new Set(inspections.map((i) => i.station))].sort()

  const handleExport = async (format) => {
    setExporting(true)
    try {
      const fn = format === 'excel' ? exportAPI.excel : format === 'csv' ? exportAPI.csv : exportAPI.sql
      const response = await fn(filters)
      const ext = format === 'excel' ? 'xlsx' : format
      downloadBlob(response.data, `inspections.${ext}`)
    } catch {
      // Silent fail for mock
    } finally {
      setExporting(false)
    }
  }

  const columns = [
    {
      key: 'id',
      label: '#',
      width: '60px',
      render: (val) => <span className="text-gray-400 font-mono text-xs">#{val}</span>,
    },
    {
      key: 'serial_number',
      label: 'Serial Number',
      width: '150px',
      render: (val) => <span className="font-mono text-sm font-medium text-gray-900">{val}</span>,
    },
    { key: 'batch_number', label: 'Batch', width: '120px' },
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
      width: '90px',
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
          <h1 className="text-3xl font-bold text-gray-900">Kiểm tra</h1>
          <p className="text-gray-600 mt-1">
            {filtered.length} kết quả
            {(filters.search || filters.result || filters.station) && ' (đã lọc)'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters((s) => !s)}
            className={`btn flex items-center gap-2 ${showFilters ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Filter className="w-4 h-4" />
            Bộ lọc
          </button>
          <button
            onClick={() => handleExport('excel')}
            disabled={exporting}
            className="btn btn-success flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            {exporting ? 'Đang xuất...' : 'Export'}
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="card !p-0">
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ search: e.target.value })}
                placeholder="Tìm theo serial, batch, station..."
                className="input !pl-10"
              />
            </div>
            {filters.search && (
              <button
                onClick={() => setFilters({ search: '' })}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="p-4 border-b border-gray-100 bg-gray-50 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Kết quả</label>
                <select
                  value={filters.result}
                  onChange={(e) => setFilters({ result: e.target.value })}
                  className="input"
                >
                  <option value="">Tất cả</option>
                  <option value="PASS">PASS</option>
                  <option value="FAIL">FAIL</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Station</label>
                <select
                  value={filters.station}
                  onChange={(e) => setFilters({ station: e.target.value })}
                  className="input"
                >
                  <option value="">Tất cả</option>
                  {stations.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Từ ngày</label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => setFilters({ dateFrom: e.target.value })}
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Đến ngày</label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => setFilters({ dateTo: e.target.value })}
                  className="input"
                />
              </div>
            </div>
            <div className="mt-3 flex justify-end">
              <button
                onClick={() =>
                  setFilters({ search: '', result: '', station: '', dateFrom: '', dateTo: '' })
                }
                className="btn btn-secondary text-sm"
              >
                Xóa bộ lọc
              </button>
            </div>
          </div>
        )}

        {/* Data Table */}
        <DataTable
          columns={columns}
          data={filtered}
          pageSize={15}
          onRowClick={(row) => navigate(`/inspections/${row.id}`)}
        />
      </div>
    </div>
  )
}
