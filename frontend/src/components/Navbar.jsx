import { useState, useRef, useEffect } from 'react'
import { Settings, User, Search, Bell, X, Menu } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Navbar({ onToggleSidebar }) {
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [notifOpen, setNotifOpen] = useState(false)
  const searchRef = useRef(null)
  const notifRef = useRef(null)
  const navigate = useNavigate()

  // Close dropdowns on outside click
  useEffect(() => {
    const handler = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const MOCK_NOTIFICATIONS = [
    { id: 1, text: 'Phát hiện lỗi tại Station B', time: '5 phút trước', read: false },
    { id: 2, text: 'Batch #1234 kiểm tra xong', time: '15 phút trước', read: false },
    { id: 3, text: 'Camera đã kết nối lại', time: '1 giờ trước', read: true },
  ]

  const unreadCount = MOCK_NOTIFICATIONS.filter((n) => !n.read).length

  return (
    <nav className="bg-white/80 backdrop-blur-xl border-b border-gray-200 fixed w-full z-30 top-0">
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={onToggleSidebar}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-800 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">QC</span>
            </div>
            <span className="text-xl font-bold text-gray-900 hidden sm:block">Quality Control</span>
          </div>

          <div className="flex items-center space-x-2">
            {/* Search */}
            {searchOpen ? (
              <div className="flex items-center bg-gray-100 rounded-lg overflow-hidden" ref={searchRef}>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Tìm kiếm serial, batch..."
                  className="bg-transparent px-3 py-2 text-sm focus:outline-none w-48"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Escape') setSearchOpen(false)
                    if (e.key === 'Enter' && searchQuery) {
                      navigate(`/inspections?q=${encodeURIComponent(searchQuery)}`)
                      setSearchOpen(false)
                    }
                  }}
                />
                <button onClick={() => setSearchOpen(false)} className="p-2 text-gray-400 hover:text-gray-600">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setSearchOpen(true)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Search className="w-5 h-5" />
              </button>
            )}

            {/* Notifications */}
            <div className="relative" ref={notifRef}>
              <button
                onClick={() => setNotifOpen((o) => !o)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors relative"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-rose-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>

              {notifOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden animate-fade-in">
                  <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">Thông báo</h3>
                    <span className="text-xs text-primary-600 cursor-pointer hover:underline">
                      Đánh dấu đã đọc
                    </span>
                  </div>
                  <div className="max-h-64 overflow-y-auto divide-y divide-gray-50">
                    {MOCK_NOTIFICATIONS.map((n) => (
                      <div
                        key={n.id}
                        className={`px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors ${
                          !n.read ? 'bg-primary-50/30' : ''
                        }`}
                      >
                        <p className="text-sm text-gray-800">{n.text}</p>
                        <p className="text-xs text-gray-400 mt-1">{n.time}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Settings className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <User className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
