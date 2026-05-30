import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, ClipboardList, FileText, BarChart3, Bell, Settings, Camera } from 'lucide-react'

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/inspections', icon: ClipboardList, label: 'Kiểm tra' },
  { path: '/templates', icon: FileText, label: 'Templates' },
  { path: '/reports', icon: BarChart3, label: 'Báo cáo' },
  { path: '/alerts', icon: Bell, label: 'Cảnh báo' },
  { path: '/settings', icon: Settings, label: 'Cài đặt' },
]

export default function Sidebar() {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  return (
    <aside className="w-64 bg-gradient-to-b from-gray-900 to-gray-800 fixed left-0 top-16 bottom-0 overflow-y-auto">
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive(item.path)
                  ? 'bg-white/10 text-white shadow-lg shadow-primary-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
              {isActive(item.path) && (
                <div className="ml-auto w-2 h-2 bg-primary-400 rounded-full shadow-lg shadow-primary-400/50" />
              )}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
