import { BarChart3, Download } from 'lucide-react'

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Báo cáo</h1>
        <p className="text-gray-600 mt-1">Xem và xuất báo cáo kiểm tra</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="card hover:shadow-md transition-shadow text-left">
          <Download className="w-8 h-8 text-emerald-500 mb-3" />
          <h3 className="font-bold text-gray-900">Export Excel</h3>
          <p className="text-sm text-gray-600">Xuất báo cáo dạng Excel</p>
        </button>
        <button className="card hover:shadow-md transition-shadow text-left">
          <Download className="w-8 h-8 text-blue-500 mb-3" />
          <h3 className="font-bold text-gray-900">Export CSV</h3>
          <p className="text-sm text-gray-600">Xuất dữ liệu dạng CSV</p>
        </button>
        <button className="card hover:shadow-md transition-shadow text-left">
          <Download className="w-8 h-8 text-purple-500 mb-3" />
          <h3 className="font-bold text-gray-900">Export SQL</h3>
          <p className="text-sm text-gray-600">Xuất database dump</p>
        </button>
      </div>
    </div>
  )
}
