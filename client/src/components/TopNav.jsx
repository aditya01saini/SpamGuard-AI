import { Menu } from 'lucide-react'

export default function TopNav({ title, onMenu }) {
  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-slate-800 bg-slate-950/80 px-4 py-3 backdrop-blur-xl md:px-6">
      <button onClick={onMenu} className="text-slate-300 hover:text-white lg:hidden">
        <Menu className="h-5 w-5" />
      </button>
      <div className="text-sm font-semibold text-slate-200">{title}</div>
      <div className="ml-auto flex items-center gap-2">
        <span className="hidden items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-300 sm:inline-flex">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          ML model online
        </span>
      </div>
    </header>
  )
}
