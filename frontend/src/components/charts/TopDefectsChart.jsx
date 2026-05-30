import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const COLORS = ['#f43f5e', '#fb7185', '#fda4af', '#fecdd3', '#ffe4e6', '#fff1f2']

export default function TopDefectsChart({ data, height = 300 }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-[200px] text-gray-400">
        <p className="text-sm">Chưa có dữ liệu lỗi phổ biến</p>
      </div>
    )
  }
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 12, fill: '#6b7280' }} tickLine={false} />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fontSize: 12, fill: '#374151' }}
          tickLine={false}
          axisLine={false}
          width={120}
        />
        <Tooltip
          formatter={(value) => [`${value} lỗi`, 'Số lượng']}
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
          }}
        />
        <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={24}>
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
