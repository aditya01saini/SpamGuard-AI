import { Link } from 'react-router-dom'
import { useApi } from '../hooks/useApi.js'
import { getAnalytics } from '../services/api.js'
import StatCard from '../components/StatCard.jsx'
import { ClassBadge, RiskBadge } from '../components/StatusBadge.jsx'
import { fmtDate, truncate, pct } from '../utils/format.js'
import {
  Activity, MailWarning, ShieldCheck, AlertTriangle, Gauge,
  ScanSearch, PieChart, ArrowRight, Loader2,
} from 'lucide-react'
import {
  ResponsiveContainer, PieChart as RPie, Pie, Cell, Tooltip, BarChart,
  Bar, XAxis, YAxis, CartesianGrid, Legend,
} from 'recharts'

// Colors for the "Detection distribution" donut, keyed by the SAME display
// names used in pieData below (Safe / Spam / Phishing). They must match,
// otherwise <Cell fill={...}> receives undefined and the SVG falls back to black.
const DETECTION_COLORS = {
  Safe: '#34d399',      // green
  Spam: '#f87171',      // red
  Phishing: '#fbbf24',  // yellow / orange
}
const RISK_COLORS = { LOW: '#34d399', MEDIUM: '#fbbf24', HIGH: '#fb923c', CRITICAL: '#f87171' }

export default function Dashboard() {
  const { data, loading, error } = useApi(() => getAnalytics(), [])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-400" />
      </div>
    )
  }

  const cc = data?.classification_counts || {}
  const rc = data?.risk_counts || {}
  const total = data?.total_scans || 0

  const pieData = [
    { name: 'Safe', value: cc.SAFE || 0, fill: DETECTION_COLORS.Safe },
    { name: 'Spam', value: cc.SPAM || 0, fill: DETECTION_COLORS.Spam },
    { name: 'Phishing', value: cc['POSSIBLE PHISHING'] || 0, fill: DETECTION_COLORS.Phishing },
  ].filter((d) => d.value > 0)

  const riskData = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((k) => ({
    name: k, count: rc[k] || 0,
  }))

  const recent = data?.trend?.slice(-8)?.reverse() || []

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="panel relative overflow-hidden p-6">
        <div className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-indigo-600/20 blur-3xl" />
        <div className="relative flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Security Overview</h1>
            <p className="mt-1 text-sm text-slate-400">
              Real-time spam, phishing &amp; threat detection analytics across all scans.
            </p>
          </div>
          <Link to="/analyze" className="btn-primary shrink-0">
            <ScanSearch className="h-4 w-4" /> New Scan
          </Link>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard icon={Activity} label="Total Scans" value={total} tone="indigo" />
        <StatCard icon={ShieldCheck} label="Safe" value={cc.SAFE || 0} tone="emerald" />
        <StatCard icon={MailWarning} label="Spam" value={cc.SPAM || 0} tone="amber" />
        <StatCard icon={AlertTriangle} label="Phishing" value={cc['POSSIBLE PHISHING'] || 0} tone="red" />
        <StatCard icon={Gauge} label="Avg Risk" value={data?.average_risk_score ?? 0} tone="slate" />
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-5">
          <div className="mb-4 flex items-center gap-2">
            <PieChart className="h-4 w-4 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Detection distribution</h3>
          </div>
          {pieData.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <RPie>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={3}>
                  {pieData.map((d) => (
                    <Cell key={d.name} fill={d.fill} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend />
              </RPie>
            </ResponsiveContainer>
          ) : (
            <EmptyCharts />
          )}
        </div>

        <div className="panel p-5">
          <div className="mb-4 flex items-center gap-2">
            <Gauge className="h-4 w-4 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Risk distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={riskData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis allowDecimals={false} stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: '#ffffff08' }} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {riskData.map((d) => (
                  <Cell key={d.name} fill={RISK_COLORS[d.name]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent scans */}
      <div className="panel p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Recent scans</h3>
          <Link to="/history" className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300">
            View all <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {recent.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500">
                  <th className="pb-2.5 pr-4 font-medium">Subject</th>
                  <th className="pb-2.5 pr-4 font-medium">Classification</th>
                  <th className="pb-2.5 pr-4 font-medium">Risk</th>
                  <th className="pb-2.5 pr-4 font-medium">Confidence</th>
                  <th className="pb-2.5 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((s) => (
                  <tr key={s.timestamp + s.classification} className="border-b border-slate-800/60 last:border-0">
                    <td className="py-3 pr-4 text-slate-300">{truncate(s.subject || '(no subject)', 40)}</td>
                    <td className="py-3 pr-4"><ClassBadge value={s.classification} /></td>
                    <td className="py-3 pr-4">
                      <span className="font-mono text-slate-300">{s.risk_score}</span>
                    </td>
                    <td className="py-3 pr-4 font-mono text-slate-400">{pct(s.confidence, 0)}</td>
                    <td className="py-3 text-slate-500">{fmtDate(s.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-sm text-slate-500">
            No scans yet. <Link to="/analyze" className="text-indigo-400 hover:underline">Run your first scan →</Link>
          </div>
        )}
      </div>
    </div>
  )
}

function EmptyCharts() {
  return <div className="flex h-64 items-center justify-center text-sm text-slate-500">No data yet</div>
}

const tooltipStyle = {
  backgroundColor: '#1e293b',
  border: '1px solid #334155',
  borderRadius: '8px',
  color: '#e2e8f0',
  fontSize: '12px',
}
