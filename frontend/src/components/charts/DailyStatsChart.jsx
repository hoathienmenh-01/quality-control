import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

function EmptyPlaceholder({ message = 'Chưa có dữ liệu' }) {
  return (
    <div className="flex items-center justify-center h-full min-h-[200px] text-gray-400">
      <div className="text-center">
        <svg className="mx-auto h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
        </svg>
        <p className="text-sm">{message}</p>
      </div>
    </div>
  )
}

export default function DailyStatsChart({ data, height = 300 }) {
  if (!data || data.length === 0) {
    return <EmptyPlaceholder />
  }
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorPassRate" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#6b7280' }} tickLine={false} />
        <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
          }}
        />
        <Legend />
        <Area
          type="monotone"
          dataKey="volume"
          stroke="#3b82f6"
          strokeWidth={2}
          fill="url(#colorVolume)"
          name="Sản lượng"
        />
        <Area
          type="monotone"
          dataKey="passRate"
          stroke="#10b981"
          strokeWidth={2}
          fill="url(#colorPassRate)"
          name="Tỷ lệ đạt (%)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
