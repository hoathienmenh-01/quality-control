import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function DefectTrendChart({ data, height = 300 }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px] text-gray-400">
        <p className="text-sm">Chưa có dữ liệu xu hướng lỗi</p>
      </div>
    )
  }
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12, fill: '#6b7280' }}
          tickLine={false}
          axisLine={{ stroke: '#e5e7eb' }}
        />
        <YAxis
          tick={{ fontSize: 12, fill: '#6b7280' }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="defects"
          stroke="#f43f5e"
          strokeWidth={2.5}
          dot={{ fill: '#f43f5e', r: 3 }}
          activeDot={{ r: 5 }}
          name="Lỗi"
        />
        <Line
          type="monotone"
          dataKey="inspections"
          stroke="#3b82f6"
          strokeWidth={2.5}
          dot={{ fill: '#3b82f6', r: 3 }}
          activeDot={{ r: 5 }}
          name="Kiểm tra"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
