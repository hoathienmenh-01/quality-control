import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, ClipboardList, FileText, BarChart3, Bell, Settings,
  Camera, ChevronLeft, ChevronRight,
} from 'lucide-react'

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/inspections', icon: ClipboardList, label: 'Kiểm tra' },
  { path: '/templates', icon: FileText, label: 'Templates' },
  { path: '/reports', icon: BarChart3, label: 'Báo cáo' },
  { path: '/alerts', icon: Bell, label: 'Cảnh báo' },
  { path: '/camera', icon: Camera, label: 'Camera' },
  { path: '/settings', icon: Settings, label: 'Cài đặt' },
]

export default function Sidebar({ collapsed = false, onToggle }) {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  return (
    <aside
      className={`bg-gradient-to-b from-gray-900 to-gray-800 fixed left-0 top-16 bottom-0 overflow-y-auto transition-all duration-300 z-20 ${
        collapsed ? 'w-[72px]' : 'w-64'
      }`}
    >
      <nav className="p-3 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)
          return (
            <Link
              key={item.path}
              to={item.path}
              title={collapsed ? item.label : undefined}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative ${
                active
                  ? 'bg-white/10 text-white shadow-lg shadow-primary-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {/* Active indicator bar */}
              {active && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary-400 rounded-r-full shadow-lg shadow-primary-400/50 transition-all duration-300" />
              )}

              <Icon className={`w-5 h-5 flex-shrink-0 ${active ? 'text-primary-300' : ''}`} />
              {!collapsed && (
                <>
                  <span className="font-medium">{item.label}</span>
                  {active && (
                    <div className="ml-auto w-2 h-2 bg-primary-400 rounded-full shadow-lg shadow-primary-400/50" />
                  )}
                </>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={onToggle}
        className="absolute bottom-4 left-1/2 -translate-x-1/2 p-2 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </aside>
  )
}
