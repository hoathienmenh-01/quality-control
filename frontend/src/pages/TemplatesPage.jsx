import { useState } from 'react'
import { Search, Plus, Edit3, Trash2, Eye, FileText, X } from 'lucide-react'
import { useTemplateStore } from '../stores/templateStore'
import Modal from '../components/Modal'
import DataTable from '../components/DataTable'
import { formatDateTime } from '../utils/helpers'

export default function TemplatesPage() {
  const { templates, searchQuery, setSearchQuery, createTemplate, updateTemplate, deleteTemplate, getFilteredTemplates } = useTemplateStore()
  const [showCreate, setShowCreate] = useState(false)
  const [editing, setEditing] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [previewing, setPreviewing] = useState(null)

  const [form, setForm] = useState({
    name: '',
    product_type: '',
    description: '',
    checks: ['component', 'qr', 'sn', 'anten'],
    active: true,
  })

  const filtered = getFilteredTemplates()

  const resetForm = () => {
    setForm({ name: '', product_type: '', description: '', checks: ['component', 'qr', 'sn', 'anten'], active: true })
    setEditing(null)
  }

  const handleCreate = async () => {
    if (!form.name.trim()) return
    await createTemplate(form)
    setShowCreate(false)
    resetForm()
  }

  const handleUpdate = async () => {
    if (!editing || !form.name.trim()) return
    await updateTemplate(editing.id, form)
    setEditing(null)
    resetForm()
  }

  const handleDelete = async () => {
    if (!deleting) return
    await deleteTemplate(deleting.id)
    setDeleting(null)
  }

  const openEdit = (template) => {
    setForm({
      name: template.name,
      product_type: template.product_type,
      description: template.description || '',
      checks: template.checks || [],
      active: template.active,
    })
    setEditing(template)
  }

  const toggleCheck = (check) => {
    setForm((f) => ({
      ...f,
      checks: f.checks.includes(check) ? f.checks.filter((c) => c !== check) : [...f.checks, check],
    }))
  }

  const allChecks = [
    { key: 'component', label: 'Linh kiện' },
    { key: 'qr', label: 'QR Code' },
    { key: 'sn', label: 'Serial Number' },
    { key: 'anten', label: 'Anten' },
  ]

  const columns = [
    {
      key: 'name',
      label: 'Tên template',
      render: (val, row) => (
        <div>
          <p className="font-semibold text-gray-900">{val}</p>
          <p className="text-xs text-gray-500">{row.product_type}</p>
        </div>
      ),
    },
    {
      key: 'description',
      label: 'Mô tả',
      render: (val) => <span className="text-gray-600 text-sm">{val || '—'}</span>,
    },
    {
      key: 'checks',
      label: 'Kiểm tra',
      sortable: false,
      render: (val) => (
        <div className="flex gap-1 flex-wrap">
          {(val || []).map((c) => (
            <span key={c} className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
              {c}
            </span>
          ))}
        </div>
      ),
    },
    {
      key: 'active',
      label: 'Trạng thái',
      width: '100px',
      render: (val) => (
        <span className={`badge ${val ? 'badge-pass' : 'badge-fail'}`}>
          {val ? 'Hoạt động' : 'Tắt'}
        </span>
      ),
    },
    {
      key: 'updated_at',
      label: 'Cập nhật',
      width: '140px',
      render: (val) => <span className="text-gray-500 text-xs">{formatDateTime(val)}</span>,
    },
    {
      key: 'actions',
      label: '',
      sortable: false,
      width: '120px',
      render: (_, row) => (
        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          <button onClick={() => setPreviewing(row)} className="p-1.5 hover:bg-gray-100 rounded-lg" title="Xem">
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          <button onClick={() => openEdit(row)} className="p-1.5 hover:bg-gray-100 rounded-lg" title="Sửa">
            <Edit3 className="w-4 h-4 text-blue-500" />
          </button>
          <button onClick={() => setDeleting(row)} className="p-1.5 hover:bg-gray-100 rounded-lg" title="Xóa">
            <Trash2 className="w-4 h-4 text-rose-500" />
          </button>
        </div>
      ),
    },
  ]

  const TemplateForm = ({ onSubmit, submitLabel }) => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Tên template *</label>
        <input
          type="text"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="input"
          placeholder="Nhập tên template"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Loại sản phẩm</label>
        <input
          type="text"
          value={form.product_type}
          onChange={(e) => setForm({ ...form, product_type: e.target.value })}
          className="input"
          placeholder="VD: PCB Board, WiFi Module"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Mô tả</label>
        <textarea
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          className="input min-h-[80px]"
          placeholder="Mô tả template..."
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Kiểm tra áp dụng</label>
        <div className="flex flex-wrap gap-2">
          {allChecks.map((c) => (
            <button
              key={c.key}
              onClick={() => toggleCheck(c.key)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                form.checks.includes(c.key)
                  ? 'bg-primary-100 text-primary-700 border border-primary-300'
                  : 'bg-gray-100 text-gray-500 border border-gray-200'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="template-active"
          checked={form.active}
          onChange={(e) => setForm({ ...form, active: e.target.checked })}
          className="w-4 h-4 text-primary-600 rounded"
        />
        <label htmlFor="template-active" className="text-sm text-gray-700">
          Kích hoạt
        </label>
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button
          onClick={() => {
            resetForm()
            setShowCreate(false)
            setEditing(null)
          }}
          className="btn btn-secondary"
        >
          Hủy
        </button>
        <button onClick={onSubmit} className="btn btn-primary">
          {submitLabel}
        </button>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
          <p className="text-gray-600 mt-1">{templates.length} template</p>
        </div>
        <button
          onClick={() => {
            resetForm()
            setShowCreate(true)
          }}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Thêm template
        </button>
      </div>

      {/* Search + Table */}
      <div className="card !p-0">
        <div className="p-4 border-b border-gray-100">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm template..."
              className="input !pl-10"
            />
          </div>
        </div>
        <DataTable columns={columns} data={filtered} pageSize={10} />
      </div>

      {/* Create Modal */}
      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Thêm template mới">
        <TemplateForm onSubmit={handleCreate} submitLabel="Tạo mới" />
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={!!editing} onClose={() => { setEditing(null); resetForm() }} title="Chỉnh sửa template">
        <TemplateForm onSubmit={handleUpdate} submitLabel="Cập nhật" />
      </Modal>

      {/* Delete Confirmation */}
      <Modal isOpen={!!deleting} onClose={() => setDeleting(null)} title="Xác nhận xóa" size="sm">
        <div className="text-center py-4">
          <div className="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trash2 className="w-8 h-8 text-rose-500" />
          </div>
          <p className="text-gray-700 mb-1">Bạn có chắc muốn xóa template?</p>
          <p className="font-semibold text-gray-900">"{deleting?.name}"</p>
          <div className="flex justify-center gap-3 mt-6">
            <button onClick={() => setDeleting(null)} className="btn btn-secondary">
              Hủy
            </button>
            <button onClick={handleDelete} className="btn btn-danger">
              Xóa
            </button>
          </div>
        </div>
      </Modal>

      {/* Preview Modal */}
      <Modal isOpen={!!previewing} onClose={() => setPreviewing(null)} title="Xem template" size="lg">
        {previewing && (
          <div className="space-y-4">
            <div className="aspect-video bg-gray-100 rounded-xl flex items-center justify-center border-2 border-dashed border-gray-300">
              <div className="text-center text-gray-400">
                <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Ảnh template</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Tên</p>
                <p className="font-semibold">{previewing.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Loại sản phẩm</p>
                <p className="font-semibold">{previewing.product_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Mô tả</p>
                <p>{previewing.description || '—'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Kiểm tra</p>
                <div className="flex gap-1 flex-wrap mt-1">
                  {(previewing.checks || []).map((c) => (
                    <span key={c} className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
