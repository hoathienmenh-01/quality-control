import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const MOCK_DATA = Array.from({ length: 30 }, (_, i) => {
  const d = new Date()
  d.setDate(d.getDate() - (29 - i))
  return {
    date: d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }),
    defects: Math.floor(Math.random() * 15) + 2,
    inspections: Math.floor(Math.random() * 50) + 30,
  }
})

export default function DefectTrendChart({ data = MOCK_DATA, height = 300 }) {
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
