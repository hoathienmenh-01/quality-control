import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function StationChart({ data, height = 300 }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px] text-gray-400">
        <p className="text-sm">Chưa có dữ liệu trạm</p>
      </div>
    )
  }
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="station" tick={{ fontSize: 12, fill: '#6b7280' }} tickLine={false} />
        <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
          }}
        />
        <Legend />
        <Bar dataKey="pass" fill="#10b981" radius={[4, 4, 0, 0]} name="PASS" />
        <Bar dataKey="fail" fill="#f43f5e" radius={[4, 4, 0, 0]} name="FAIL" />
      </BarChart>
    </ResponsiveContainer>
  )
}
