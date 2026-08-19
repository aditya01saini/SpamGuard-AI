import { riskColor, RISK_META } from '../utils/risk.js'

// SVG semi-circular gauge showing the 0-100 risk score.
export default function RiskGauge({ score }) {
  const clamped = Math.max(0, Math.min(100, Number(score) || 0))
  const color = riskColor(clamped)
  const meta = RISK_META[levelOf(clamped)] || RISK_META.LOW

  // Semi-circle arc math
  const radius = 80
  const circumference = Math.PI * radius
  const filled = (clamped / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <svg width="200" height="110" viewBox="0 0 200 110">
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#1e293b"
            strokeWidth="14"
            strokeLinecap="round"
          />
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={color}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={`${filled} ${circumference}`}
            style={{ transition: 'stroke-dasharray 0.8s ease' }}
          />
        </svg>
        <div className="absolute inset-x-0 bottom-0 text-center">
          <div className="text-4xl font-bold text-white">{clamped}</div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">/ 100</div>
        </div>
      </div>
      <span className={`mt-1 rounded-full border px-3 py-1 text-xs font-bold ${meta.color} ${meta.bg} ${meta.border}`}>
        {meta.label}
      </span>
    </div>
  )
}

function levelOf(score) {
  if (score <= 25) return 'LOW'
  if (score <= 50) return 'MEDIUM'
  if (score <= 75) return 'HIGH'
  return 'CRITICAL'
}
