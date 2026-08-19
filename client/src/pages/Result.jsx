import { useMemo } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { useApi } from '../hooks/useApi.js'
import { getScan, reportUrl } from '../services/api.js'
import { ClassBadge, RiskBadge, SeverityBadge } from '../components/StatusBadge.jsx'
import RiskGauge from '../components/RiskGauge.jsx'
import { pct, fmtDate } from '../utils/format.js'
import { CLASS_META } from '../utils/risk.js'
import {
  AlertTriangle, BrainCircuit, Download, FileText, Globe, Hash,
  KeyRound, Link2, Loader2, Sparkles, ShieldAlert, BarChart3,
} from 'lucide-react'

export default function Result() {
  const { id } = useParams()
  const { state } = useLocation()
  const { data, loading, error } = useApi(
    () => getScan(id),
    [id]
  )

  // Prefer freshly-returned result from navigation, else the fetched one.
  const result = useMemo(() => (data && !state?.result ? data : state?.result || data), [data, state])

  if (loading && !result) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-400" />
      </div>
    )
  }

  if (error && !result) {
    return (
      <div className="panel p-8 text-center text-red-300">
        <p>Could not load this scan.</p>
        <p className="mt-1 text-sm text-slate-400">{error}</p>
      </div>
    )
  }

  if (!result) return null

  const clsMeta = CLASS_META[result.classification] || CLASS_META.SAFE
  const ai = result.ai_analysis || {}
  const stats = result.statistics || {}
  const info = result.email_info || {}

  return (
    <div className="space-y-6">
      {/* Verdict banner */}
      <div className={`panel animate-fade-up overflow-hidden border ${clsMeta.border}`}>
        <div className="flex flex-col items-center gap-5 p-6 md:flex-row md:justify-between">
          <div className="flex items-center gap-4">
            <div className={`flex h-16 w-16 items-center justify-center rounded-2xl ${clsMeta.bg}`}>
              <ShieldAlert className={`h-8 w-8 ${clsMeta.color}`} />
            </div>
            <div>
              <div className={`text-3xl font-extrabold tracking-tight ${clsMeta.color}`}>
                {result.classification}
              </div>
              <div className="mt-1 text-sm text-slate-400">
                {result.classification_reason}
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                <ClassBadge value={result.classification} />
                <RiskBadge value={result.risk_level} />
                <span className="kbd-chip">Model: {result.model_name}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="rounded-xl bg-slate-800/50 px-5 py-3">
              <div className="text-[11px] uppercase tracking-wider text-slate-400">Confidence</div>
              <div className="text-2xl font-bold text-white">{pct(result.confidence)}</div>
            </div>
            <div className="rounded-xl bg-slate-800/50 px-5 py-3">
              <div className="text-[11px] uppercase tracking-wider text-slate-400">Risk Score</div>
              <div className="text-2xl font-bold text-white">{result.risk_score}/100</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left column */}
        <div className="space-y-6 lg:col-span-2">
          {/* Probabilities */}
          <Section title="Detection probabilities" icon={BarChart3}>
            <div className="space-y-3">
              <ProbBar label="Spam probability" value={result.spam_probability} color="#fbbf24" />
              <ProbBar label="Safe probability" value={result.safe_probability} color="#34d399" />
              <ProbBar label="Phishing probability" value={result.phishing_probability} color="#f87171" />
            </div>
            <p className="mt-3 text-xs text-slate-500">
              Probabilities come from the ML model (spam/safe) and the rule-based
              phishing engine (phishing) — kept separate for transparency.
            </p>
          </Section>

          {/* Why / threat indicators */}
          <Section title="Why this verdict?" icon={AlertTriangle}>
            {result.threat_indicators?.length ? (
              <ul className="space-y-2.5">
                {result.threat_indicators.map((ti, i) => (
                  <li key={i} className="flex items-start gap-3 rounded-xl bg-slate-800/40 p-3">
                    <SeverityBadge value={ti.severity} />
                    <div>
                      <div className="text-sm font-semibold text-slate-200">{ti.indicator}</div>
                      <div className="text-xs text-slate-400">{ti.description}</div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyNote text="No threat indicators detected." />
            )}
          </Section>

          {/* URLs */}
          <Section title="URL analysis" icon={Link2}>
            {result.urls?.length ? (
              <div className="space-y-2.5">
                {result.urls.map((u, i) => (
                  <div key={i} className="rounded-xl bg-slate-800/40 p-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs text-indigo-300 break-all">{u.url}</span>
                      <SeverityBadge value={u.severity} />
                      {u.is_https
                        ? <span className="text-[11px] text-emerald-400">HTTPS</span>
                        : <span className="text-[11px] text-amber-400">HTTP</span>}
                    </div>
                    {u.risk_indicators?.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {u.risk_indicators.map((ri, j) => (
                          <li key={j} className="flex items-start gap-2 text-xs text-slate-400">
                            <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-slate-500" />
                            <span><span className="text-slate-300">{ri.indicator}:</span> {ri.description}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyNote text="No URLs found in the email." />
            )}
          </Section>

          {/* Suspicious keywords */}
          <Section title="Suspicious keywords" icon={KeyRound}>
            {result.suspicious_keywords?.length ? (
              <div className="flex flex-wrap gap-2">
                {result.suspicious_keywords.map((k, i) => (
                  <span key={i} className="kbd-chip !text-amber-300 !border-amber-500/30">{k}</span>
                ))}
              </div>
            ) : (
              <EmptyNote text="No suspicious keywords detected." />
            )}
          </Section>

          {/* AI analysis */}
          <Section title="AI Analysis (Mistral)" icon={Sparkles}>
            {ai.available ? (
              <div className="space-y-4">
                <AIField label="Summary" text={ai.summary} />
                <AIField label="Explanation" text={ai.explanation} />
                <AIField label="Threat analysis" text={ai.threat_analysis} />
              </div>
            ) : (
              <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-slate-400">
                <div className="mb-1 font-semibold text-amber-300">AI explanation unavailable</div>
                {ai.reason || 'Mistral API is not configured.'}
                <div className="mt-2 text-xs text-slate-500">
                  ML classification and rule-based indicators remain valid.
                </div>
              </div>
            )}
          </Section>
        </div>

        {/* Right column */}
        <div className="space-y-6">
          <Section title="Risk score" icon={AlertTriangle}>
            <RiskGauge score={result.risk_score} />
            <div className="mt-4 space-y-2">
              {(result.risk_breakdown || []).map((b, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">{b.component}</span>
                  <span className="font-mono font-semibold text-slate-200">{b.points} pts</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Email statistics" icon={Hash}>
            <div className="grid grid-cols-2 gap-2.5">
              <Stat label="Words" value={stats.word_count} />
              <Stat label="Characters" value={stats.character_count} />
              <Stat label="Sentences" value={stats.sentence_count} />
              <Stat label="URLs" value={stats.url_count} />
              <Stat label="Suspicious keywords" value={stats.suspicious_keyword_count} />
              <Stat label="Threat indicators" value={stats.threat_indicator_count} />
              <Stat label="Contains HTML" value={stats.has_html ? 'Yes' : 'No'} />
              <Stat label="Attachments" value={stats.has_attachments ? 'Yes' : 'No'} />
            </div>
          </Section>

          <Section title="Email info" icon={FileText}>
            <dl className="space-y-1.5 text-xs">
              <InfoRow label="Subject" value={info.subject || '—'} />
              <InfoRow label="Sender" value={info.sender || '—'} />
              <InfoRow label="To" value={info.to || '—'} />
              <InfoRow label="Date" value={info.date || '—'} />
              <InfoRow label="Scanned" value={fmtDate(result.timestamp)} />
            </dl>
          </Section>

          <div className="panel border-emerald-500/30 bg-emerald-500/5 p-4">
            <div className="mb-1.5 flex items-center gap-2 text-sm font-semibold text-emerald-300">
              <ShieldAlert className="h-4 w-4" /> Recommended action
            </div>
            <p className="text-sm leading-relaxed text-slate-300">{result.recommendation}</p>
          </div>

          <a
            href={reportUrl(id)}
            className="btn-primary w-full"
            target="_blank"
            rel="noreferrer"
          >
            <Download className="h-4 w-4" /> Download PDF Report
          </a>
        </div>
      </div>
    </div>
  )
}

/* --- sub-components --- */

function Section({ title, icon: Icon, children }) {
  return (
    <div className="panel animate-fade-up p-5">
      <div className="mb-4 flex items-center gap-2">
        <Icon className="h-4 w-4 text-indigo-400" />
        <h3 className="text-sm font-semibold text-white">{title}</h3>
      </div>
      {children}
    </div>
  )
}

function ProbBar({ label, value, color }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="font-mono font-semibold text-slate-200">{pct(value)}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${(value || 0) * 100}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

function AIField({ label, text }) {
  return (
    <div>
      <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-indigo-300">{label}</div>
      <p className="text-sm leading-relaxed text-slate-300">{text}</p>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-800/50 px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-slate-500">{label}</div>
      <div className="text-sm font-semibold text-slate-200">{value}</div>
    </div>
  )
}

function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="shrink-0 text-slate-500">{label}</dt>
      <dd className="truncate text-right text-slate-300">{value}</dd>
    </div>
  )
}

function EmptyNote({ text }) {
  return <p className="text-sm text-slate-500">{text}</p>
}
