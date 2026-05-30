import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

const variants = {
  PASS: {
    bg: 'bg-emerald-100',
    text: 'text-emerald-800',
    icon: CheckCircle,
    border: 'border-emerald-200',
  },
  FAIL: {
    bg: 'bg-rose-100',
    text: 'text-rose-800',
    icon: XCircle,
    border: 'border-rose-200',
  },
  WARNING: {
    bg: 'bg-amber-100',
    text: 'text-amber-800',
    icon: AlertTriangle,
    border: 'border-amber-200',
  },
}

export default function StatusBadge({ status, size = 'sm', showIcon = true }) {
  const variant = variants[status] || variants.WARNING
  const Icon = variant.icon

  const sizeClasses = {
    xs: 'px-1.5 py-0.5 text-xs',
    sm: 'px-2.5 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  }

  const iconSizes = { xs: 'w-3 h-3', sm: 'w-3.5 h-3.5', md: 'w-4 h-4', lg: 'w-5 h-5' }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold border ${variant.bg} ${variant.text} ${variant.border} ${sizeClasses[size]}`}
    >
      {showIcon && <Icon className={iconSizes[size]} />}
      {status}
    </span>
  )
}
