import { FileText } from 'lucide-react'

export default function TemplatesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
        <p className="text-gray-600 mt-1">Quản lý template sản phẩm</p>
      </div>
      <div className="card">
        <div className="text-gray-400 text-center py-12">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Chưa có template nào</p>
        </div>
      </div>
    </div>
  )
}
