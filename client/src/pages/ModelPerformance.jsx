import { useApi } from '../hooks/useApi.js'
import { getModelInfo } from '../services/api.js'
import { BrainCircuit, Loader2, Database, FlaskConical } from 'lucide-react'
import { pct } from '../utils/format.js'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'

const tooltipStyle = { backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0', fontSize: 12 }

export default function ModelPerformance() {
  const { data, loading, error } = useApi(() => getModelInfo(), [])

  if (loading) {
    return <div className="flex h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-indigo-400" /></div>
  }
  if (error) {
    return <div className="panel p-6 text-center text-red-300">{error}</div>
  }

  if (!data?.loaded) {
    return (
      <div className="panel p-10 text-center">
        <BrainCircuit className="mx-auto h-10 w-10 text-slate-600" />
        <p className="mt-3 text-slate-400">
          ML model is not loaded on the server. Run{' '}
          <code className="rounded bg-slate-800 px-1.5 py-0.5 text-xs text-indigo-300">python server/ml/train_model.py</code>
        </p>
      </div>
    )
  }

  const metrics = data.metrics || {}
  const models = metrics.models || []
  const ds = metrics.dataset || {}

  const comparison = models.map((m) => ({
    name: m.model.replace('Multinomial Naive Bayes', 'Naive Bayes'),
    Accuracy: +(m.accuracy * 100).toFixed(2),
    Precision: +(m.precision * 100).toFixed(2),
    Recall: +(m.recall * 100).toFixed(2),
    'F1 Score': +(m.f1_score * 100).toFixed(2),
  }))

  const best = models.find((m) => m.model === metrics.best_model)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="panel flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-600/15">
            <BrainCircuit className="h-7 w-7 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">{metrics.best_model}</h1>
            <p className="text-sm text-slate-400">Selected as the production model</p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="kbd-chip"><Database className="mr-1 h-3 w-3" /> {ds.rows?.toLocaleString()} emails</span>
          <span className="kbd-chip">Spam: {ds.spam?.toLocaleString()}</span>
          <span className="kbd-chip">Ham: {ds.ham?.toLocaleString()}</span>
        </div>
      </div>

      {/* Best model metric cards */}
      {best && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <MetricCard label="Accuracy" value={pct(best.accuracy)} />
          <MetricCard label="Precision" value={pct(best.precision)} />
          <MetricCard label="Recall" value={pct(best.recall)} />
          <MetricCard label="F1 Score" value={pct(best.f1_score)} />
        </div>
      )}

      {/* Model comparison */}
      <div className="panel p-5">
        <div className="mb-4 flex items-center gap-2">
          <FlaskConical className="h-4 w-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-white">Model comparison (%)</h3>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={comparison} barSize={28}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#64748b" fontSize={12} interval={0} />
            <YAxis domain={[90, 100]} stroke="#64748b" fontSize={12} />
            <Tooltip contentStyle={tooltipStyle} cursor={{ fill: '#ffffff08' }} />
            <Legend />
            <Bar dataKey="Accuracy" fill="#6366f1" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Precision" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Recall" fill="#a78bfa" radius={[4, 4, 0, 0]} />
            <Bar dataKey="F1 Score" fill="#34d399" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Confusion matrices */}
      <div className="grid gap-6 lg:grid-cols-2">
        {models.map((m) => (
          <div key={m.model} className="panel p-5">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">{m.model}</h3>
              {m.model === metrics.best_model && (
                <span className="rounded-full bg-indigo-600/20 px-2 py-0.5 text-[10px] font-bold text-indigo-300">BEST</span>
              )}
            </div>
            <ConfusionMatrix cm={m.confusion_matrix} />
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-400">
              <span>Precision: <span className="font-mono text-slate-200">{pct(m.precision)}</span></span>
              <span>Recall: <span className="font-mono text-slate-200">{pct(m.recall)}</span></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function MetricCard({ label, value }) {
  return (
    <div className="panel p-5 text-center">
      <div className="text-xs font-medium uppercase tracking-wider text-slate-400">{label}</div>
      <div className="mt-1.5 text-3xl font-bold text-white">{value}</div>
    </div>
  )
}

function ConfusionMatrix({ cm }) {
  if (!cm || cm.length !== 2) return null
  const [[tn, fp], [fn, tp]] = cm
  const cell = 'flex h-14 w-full items-center justify-center rounded-lg font-mono text-lg'
  return (
    <div className="grid grid-cols-[auto_1fr_1fr] gap-1.5 text-center">
      <div />
      <div className="text-xs text-slate-500">Pred. Safe</div>
      <div className="text-xs text-slate-500">Pred. Spam</div>
      <div className="flex items-center text-xs text-slate-500">Actual Safe</div>
      <div className={`${cell} bg-emerald-500/10 text-emerald-300`}>{tn}</div>
      <div className={`${cell} bg-red-500/10 text-red-300`}>{fp}</div>
      <div className="flex items-center text-xs text-slate-500">Actual Spam</div>
      <div className={`${cell} bg-red-500/10 text-red-300`}>{fn}</div>
      <div className={`${cell} bg-emerald-500/10 text-emerald-300`}>{tp}</div>
    </div>
  )
}
