// Shared helpers for classification & risk styling.

export const RISK_META = {
  LOW: { color: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', hex: '#34d399', label: 'LOW RISK' },
  MEDIUM: { color: 'text-amber-400', bg: 'bg-amber-500/15', border: 'border-amber-500/30', hex: '#fbbf24', label: 'MEDIUM RISK' },
  HIGH: { color: 'text-orange-400', bg: 'bg-orange-500/15', border: 'border-orange-500/30', hex: '#fb923c', label: 'HIGH RISK' },
  CRITICAL: { color: 'text-red-400', bg: 'bg-red-500/15', border: 'border-red-500/30', hex: '#f87171', label: 'CRITICAL RISK' },
}

export const CLASS_META = {
  SAFE: { color: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', hex: '#34d399' },
  SPAM: { color: 'text-amber-400', bg: 'bg-amber-500/15', border: 'border-amber-500/30', hex: '#fbbf24' },
  'POSSIBLE PHISHING': { color: 'text-red-400', bg: 'bg-red-500/15', border: 'border-red-500/30', hex: '#f87171' },
}

export const severityMeta = (sev) => {
  switch (sev) {
    case 'HIGH': return { color: 'text-red-400', bg: 'bg-red-500/15' }
    case 'MEDIUM': return { color: 'text-amber-400', bg: 'bg-amber-500/15' }
    case 'LOW': return { color: 'text-slate-400', bg: 'bg-slate-500/15' }
    default: return { color: 'text-slate-400', bg: 'bg-slate-500/15' }
  }
}

export const riskColor = (score) => {
  if (score <= 25) return '#34d399'
  if (score <= 50) return '#fbbf24'
  if (score <= 75) return '#fb923c'
  return '#f87171'
}
