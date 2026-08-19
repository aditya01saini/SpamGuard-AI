import { useApi } from '../hooks/useApi.js'
import { getAnalytics, getModelInfo } from '../services/api.js'
import { Loader2, TrendingUp, PieChart as PieIcon, BarChart3 } from 'lucide-react'
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line,
} from 'recharts'

const CLASS_COLORS = { SAFE: '#34d399', SPAM: '#fbbf24', 'POSSIBLE PHISHING': '#f87171' }
const RISK_COLORS = { LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#fb923c', CRITICAL: '#f87171' }
const tooltipStyle = { backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }

export default function Analytics() {
  const { data, loading, error } = useApi(() => getAnalytics(), [])
  const model = useApi(() => getModelInfo(), [])

  if (loading) {
    return <div className="flex h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-indigo-400" /></div>
  }

  const cc = data?.classification_counts || {}
  const rc = data?.risk_counts || {}
  const trend = (data?.trend || []).map((t, i) => ({
    index: i + 1,
    risk: t.risk_score,
    classification: t.classification,
  }))

  const pieData = ['SAFE', 'SPAM', 'POSSIBLE PHISHING'].map((k) => ({
    name: k, value: cc[k] || 0,
  })).filter((d) => d.value > 0)

  const riskData = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((k) => ({
    name: k, count: rc[k] || 0,
  }))

  const bestModel = model.data?.metrics?.best_model || '—'

  return (
    <div className="space-y-6">
      {error && <div className="panel p-4 text-red-300">{error}</div>}

      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard icon={PieIcon} title="Spam vs Safe vs Phishing">
          {pieData.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={3}>
                  {pieData.map((d) => <Cell key={d.name} fill={CLASS_COLORS[d.name]} stroke="transparent" />)}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <Empty />}
        </ChartCard>

        <ChartCard icon={BarChart3} title="Risk level distribution">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={riskData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis allowDecimals={false} stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: '#ffffff08' }} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {riskData.map((d) => <Cell key={d.name} fill={RISK_COLORS[d.name]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard icon={TrendingUp} title="Historical scan risk trend">
        {trend.length ? (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="index" stroke="#64748b" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="risk" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : <Empty />}
      </ChartCard>

      <div className="panel p-5">
        <h3 className="mb-3 text-sm font-semibold text-white">Model summary</h3>
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <span className="kbd-chip">Best model: <span className="ml-1 text-indigo-300">{bestModel}</span></span>
          <span className="text-slate-400">Detailed metrics are available on the</span>
          <a href="/model" className="text-indigo-400 hover:underline">Model Performance page →</a>
        </div>
      </div>
    </div>
  )
}

function ChartCard({ icon: Icon, title, children }) {
  return (
    <div className="panel p-5">
      <div className="mb-4 flex items-center gap-2">
        <Icon className="h-4 w-4 text-indigo-400" />
        <h3 className="text-sm font-semibold text-white">{title}</h3>
      </div>
      {children}
    </div>
  )
}

function Empty() {
  return <div className="flex h-64 items-center justify-center text-sm text-slate-500">No data yet</div>
}
