import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

const COLORS = ['#10b981', '#f43f5e']

export default function PassRateChart({ passCount = 450, failCount = 30 }) {
  const data = [
    { name: 'PASS', value: passCount },
    { name: 'FAIL', value: failCount },
  ]

  const total = passCount + failCount
  const passRate = total > 0 ? ((passCount / total) * 100).toFixed(1) : 0

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
            strokeWidth={0}
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, name) => [`${value} sản phẩm`, name]}
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '12px',
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center">
          <p className="text-3xl font-bold text-gray-900">{passRate}%</p>
          <p className="text-xs text-gray-500">Tỷ lệ đạt</p>
        </div>
      </div>
    </div>
  )
}
