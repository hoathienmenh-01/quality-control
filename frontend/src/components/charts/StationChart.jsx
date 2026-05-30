import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const MOCK_DATA = [
  { station: 'Station A', pass: 120, fail: 8 },
  { station: 'Station B', pass: 95, fail: 12 },
  { station: 'Station C', pass: 110, fail: 5 },
  { station: 'Station D', pass: 85, fail: 15 },
]

export default function StationChart({ data = MOCK_DATA, height = 300 }) {
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
