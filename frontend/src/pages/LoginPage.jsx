import { useState } from 'react'
import { Lock, Mail, Eye, EyeOff, LogIn, Shield } from 'lucide-react'
import { useAuthStore } from '../services/authStore'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const login = useAuthStore((s) => s.login)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Vui lòng nhập email và mật khẩu')
      return
    }
    setIsLoading(true)
    setError('')
    const result = await login(email, password)
    if (!result.success) {
      setError(result.error)
    }
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo / Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">QC System</h1>
          <p className="text-gray-500 mt-1">Hệ thống kiểm tra chất lượng sản phẩm</p>
        </div>

        {/* Login Card */}
        <div className="card shadow-xl border-0">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="text-center mb-2">
              <h2 className="text-lg font-semibold text-gray-900">Đăng nhập</h2>
              <p className="text-sm text-gray-500">Nhập thông tin tài khoản</p>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@company.com"
                  className="input pl-10"
                  autoComplete="email"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mật khẩu</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input pl-10 pr-10"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full flex items-center justify-center gap-2 py-2.5"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  Đăng nhập
                </>
              )}
            </button>

            <p className="text-xs text-center text-gray-400">
              Liên hệ quản trị viên nếu chưa có tài khoản
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
