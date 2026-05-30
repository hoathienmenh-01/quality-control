import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle, XCircle, Clock, Camera } from 'lucide-react'
import { useInspectionStore } from '../stores/inspectionStore'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import { formatDateTime, formatInferenceTime } from '../utils/helpers'

export default function InspectionDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { selectedInspection, isLoading, fetchInspectionById } = useInspectionStore()

  useEffect(() => {
    fetchInspectionById(id)
  }, [id, fetchInspectionById])

  if (isLoading) return <LoadingSpinner text="Đang tải chi tiết..." />
  if (!selectedInspection) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500 text-lg">Không tìm thấy kết quả kiểm tra #{id}</p>
        <button onClick={() => navigate('/inspections')} className="btn btn-primary mt-4">
          Quay lại danh sách
        </button>
      </div>
    )
  }

  const insp = selectedInspection
  const checks = insp.checks || {
    component: 'PASS',
    qr: 'PASS',
    sn: 'PASS',
    anten: 'PASS',
  }

  const checkLabels = {
    component: { label: 'Kiểm tra linh kiện', icon: '🔧' },
    qr: { label: 'Đọc mã QR', icon: '📱' },
    sn: { label: 'Đối chiếu Serial Number', icon: '🔢' },
    anten: { label: 'Kiểm tra Anten', icon: '📡' },
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/inspections')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chi tiết kiểm tra #{insp.id}</h1>
          <p className="text-gray-600 mt-0.5">Serial: {insp.serial_number}</p>
        </div>
        <div className="ml-auto">
          <StatusBadge status={insp.result} size="lg" />
        </div>
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card !py-4">
          <p className="text-xs text-gray-500">Serial Number</p>
          <p className="font-mono font-semibold text-gray-900 mt-1">{insp.serial_number}</p>
        </div>
        <div className="card !py-4">
          <p className="text-xs text-gray-500">Batch</p>
          <p className="font-semibold text-gray-900 mt-1">{insp.batch_number}</p>
        </div>
        <div className="card !py-4">
          <p className="text-xs text-gray-500">Station</p>
          <p className="font-semibold text-gray-900 mt-1">{insp.station}</p>
        </div>
        <div className="card !py-4">
          <p className="text-xs text-gray-500">Thời gian suy luận</p>
          <p className="font-semibold text-gray-900 mt-1">{formatInferenceTime(insp.inference_time)}</p>
        </div>
      </div>

      {/* Images */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Camera className="w-4 h-4" /> Ảnh gốc
          </h3>
          <div className="aspect-video bg-gray-100 rounded-xl flex items-center justify-center border-2 border-dashed border-gray-300">
            <div className="text-center text-gray-400">
              <Camera className="w-10 h-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Ảnh gốc sản phẩm</p>
            </div>
          </div>
        </div>
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Camera className="w-4 h-4" /> Ảnh chú thích
          </h3>
          <div className="aspect-video bg-gray-100 rounded-xl flex items-center justify-center border-2 border-dashed border-gray-300">
            <div className="text-center text-gray-400">
              <Camera className="w-10 h-10 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Ảnh với bounding box</p>
            </div>
          </div>
        </div>
      </div>

      {/* Check Results */}
      <div className="card">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Kết quả kiểm tra chi tiết</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(checks).map(([key, status]) => {
            const info = checkLabels[key] || { label: key, icon: '✅' }
            const pass = status === 'PASS'
            return (
              <div
                key={key}
                className={`flex items-center gap-4 p-4 rounded-xl border-2 transition-colors ${
                  pass
                    ? 'border-emerald-200 bg-emerald-50/50'
                    : 'border-rose-200 bg-rose-50/50'
                }`}
              >
                <div className="text-2xl">{info.icon}</div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{info.label}</p>
                  <p className={`text-sm ${pass ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {pass ? 'Đạt yêu cầu' : 'Không đạt yêu cầu'}
                  </p>
                </div>
                {pass ? (
                  <CheckCircle className="w-6 h-6 text-emerald-500" />
                ) : (
                  <XCircle className="w-6 h-6 text-rose-500" />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Defects */}
      {insp.defects && insp.defects.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Chi tiết lỗi phát hiện</h2>
          <div className="space-y-2">
            {insp.defects.map((defect, i) => (
              <div
                key={i}
                className="flex items-center gap-3 p-3 bg-rose-50 rounded-lg border border-rose-200"
              >
                <XCircle className="w-5 h-5 text-rose-500 flex-shrink-0" />
                <span className="text-sm text-rose-800">{defect}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="card">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Timeline</h2>
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Camera className="w-4 h-4 text-blue-600" />
              </div>
              <div className="w-0.5 h-8 bg-gray-200 mt-1" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Chụp ảnh sản phẩm</p>
              <p className="text-sm text-gray-500">{formatDateTime(insp.timestamp)}</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <Clock className="w-4 h-4 text-purple-600" />
              </div>
              <div className="w-0.5 h-8 bg-gray-200 mt-1" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Phân tích AI ({formatInferenceTime(insp.inference_time)})</p>
              <p className="text-sm text-gray-500">Kiểm tra linh kiện, QR, SN, Anten</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  insp.result === 'PASS' ? 'bg-emerald-100' : 'bg-rose-100'
                }`}
              >
                {insp.result === 'PASS' ? (
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                ) : (
                  <XCircle className="w-4 h-4 text-rose-600" />
                )}
              </div>
            </div>
            <div>
              <p className="font-medium text-gray-900">
                Kết quả: <StatusBadge status={insp.result} size="xs" />
              </p>
              <p className="text-sm text-gray-500">Kiểm tra hoàn tất</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
