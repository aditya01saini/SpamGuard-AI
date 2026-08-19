import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ScanSearch, History, BarChart3, BrainCircuit, ShieldCheck, X } from 'lucide-react'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyze', label: 'Email Analyzer', icon: ScanSearch },
  { to: '/history', label: 'Scan History', icon: History },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/model', label: 'Model Performance', icon: BrainCircuit },
]

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 z-30 bg-black/60 lg:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform border-r border-slate-800 bg-slate-900/80 backdrop-blur-xl transition-transform duration-200 lg:translate-x-0 lg:static ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between px-5 py-5">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 shadow-glow">
                <ShieldCheck className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="text-base font-bold text-white leading-tight">SpamGuard AI</div>
                <div className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
                  Threat Analyzer
                </div>
              </div>
            </div>
            <button onClick={onClose} className="text-slate-400 hover:text-white lg:hidden">
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="mt-2 flex-1 space-y-1 px-3">
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                onClick={onClose}
                className={({ isActive }) =>
                  `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-400 hover:bg-slate-800/70 hover:text-white border border-transparent'
                  }`
                }
              >
                <Icon className="h-[18px] w-[18px]" />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="border-t border-slate-800 p-4">
            <div className="rounded-xl bg-slate-800/50 border border-slate-700/60 p-3 text-xs text-slate-400">
              <div className="mb-1 font-semibold text-slate-300">Hybrid AI engine</div>
              ML classifier + phishing rules + Mistral AI explanation.
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
