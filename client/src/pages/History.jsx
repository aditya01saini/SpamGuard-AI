import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useApi } from '../hooks/useApi.js'
import { getHistory, deleteScan } from '../services/api.js'
import { ClassBadge } from '../components/StatusBadge.jsx'
import { fmtDate, truncate, pct } from '../utils/format.js'
import { Search, Trash2, Eye, Loader2, History as HistoryIcon } from 'lucide-react'

export default function History() {
  const [search, setSearch] = useState('')
  const [classification, setClassification] = useState('')
  const [sort, setSort] = useState('newest')
  const [deleting, setDeleting] = useState(null)

  const { data, loading, error, refetch } = useApi(
    () => getHistory({ classification: classification || undefined, search: search || undefined }),
    [classification]
  )

  const handleDelete = async (id) => {
    setDeleting(id)
    try {
      await deleteScan(id)
      await refetch()
    } finally {
      setDeleting(null)
    }
  }

  let scans = data?.scans || []
  if (sort === 'risk') {
    scans = [...scans].sort((a, b) => b.risk_score - a.risk_score)
  } else if (sort === 'oldest') {
    scans = [...scans].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            className="input !pl-9"
            placeholder="Search by subject or sender…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <select className="input !w-auto" value={classification} onChange={(e) => setClassification(e.target.value)}>
            <option value="">All classifications</option>
            <option value="SAFE">Safe</option>
            <option value="SPAM">Spam</option>
            <option value="POSSIBLE PHISHING">Possible Phishing</option>
          </select>
          <select className="input !w-auto" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="risk">Highest risk</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex h-48 items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-indigo-400" />
        </div>
      ) : error ? (
        <div className="panel p-6 text-center text-red-300">{error}</div>
      ) : scans.length === 0 ? (
        <div className="panel flex flex-col items-center justify-center gap-3 p-10 text-center">
          <HistoryIcon className="h-10 w-10 text-slate-600" />
          <p className="text-slate-400">No scans found.</p>
          <Link to="/analyze" className="btn-primary !px-4 !py-2 text-sm">Analyze an email</Link>
        </div>
      ) : (
        <div className="panel overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3 font-medium">Subject</th>
                  <th className="px-4 py-3 font-medium">Classification</th>
                  <th className="px-4 py-3 font-medium">Risk</th>
                  <th className="px-4 py-3 font-medium">Confidence</th>
                  <th className="px-4 py-3 font-medium">Date</th>
                  <th className="px-5 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {scans.map((s) => (
                  <tr key={s.id} className="border-b border-slate-800/60 transition-colors last:border-0 hover:bg-slate-800/30">
                    <td className="max-w-[240px] px-5 py-3.5">
                      <div className="truncate font-medium text-slate-200">{truncate(s.subject || '(no subject)', 48)}</div>
                      <div className="truncate text-xs text-slate-500">{s.sender || 'unknown sender'}</div>
                    </td>
                    <td className="px-4 py-3.5"><ClassBadge value={s.classification} /></td>
                    <td className="px-4 py-3.5">
                      <span className="font-mono text-slate-300">{s.risk_score}</span>
                      <span className="ml-1 text-[10px] uppercase text-slate-500">{s.risk_level}</span>
                    </td>
                    <td className="px-4 py-3.5 font-mono text-slate-400">{pct(s.confidence, 0)}</td>
                    <td className="px-4 py-3.5 text-slate-500">{fmtDate(s.timestamp)}</td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center justify-end gap-2">
                        <Link to={`/result/${s.id}`} className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-700/60 hover:text-white" title="View details">
                          <Eye className="h-4 w-4" />
                        </Link>
                        <button
                          onClick={() => handleDelete(s.id)}
                          disabled={deleting === s.id}
                          className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-red-500/15 hover:text-red-400 disabled:opacity-50"
                          title="Delete"
                        >
                          {deleting === s.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
