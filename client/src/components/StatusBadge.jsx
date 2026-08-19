import { CLASS_META, RISK_META } from '../utils/risk.js'

export function ClassBadge({ value }) {
  const meta = CLASS_META[value] || CLASS_META.SAFE
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${meta.color} ${meta.bg} ${meta.border}`}>
      {value}
    </span>
  )
}

export function RiskBadge({ value }) {
  const meta = RISK_META[value] || RISK_META.LOW
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${meta.color} ${meta.bg} ${meta.border}`}>
      {meta.label}
    </span>
  )
}

export function SeverityBadge({ value }) {
  const colors = {
    HIGH: 'text-red-400 bg-red-500/15 border-red-500/30',
    MEDIUM: 'text-amber-400 bg-amber-500/15 border-amber-500/30',
    LOW: 'text-slate-400 bg-slate-500/15 border-slate-500/30',
    NONE: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  }
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold ${colors[value] || colors.LOW}`}>
      {value}
    </span>
  )
}
