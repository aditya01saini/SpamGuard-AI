import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ScanSearch, Upload, Trash2, Sparkles, FileText, Loader2, ShieldCheck, X } from 'lucide-react'
import { analyzeEmail, analyzeUpload } from '../services/api.js'
import { SAMPLE_EMAILS } from '../services/sampleEmails.js'

export default function Analyzer() {
  const navigate = useNavigate()
  const fileRef = useRef(null)

  const [subject, setSubject] = useState('')
  const [sender, setSender] = useState('')
  const [body, setBody] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [stage, setStage] = useState('')

  const clearAll = () => {
    setSubject(''); setSender(''); setBody(''); setFile(null); setError('')
    if (fileRef.current) fileRef.current.value = ''
  }

  const loadSample = (sample) => {
    setSubject(sample.subject)
    setSender(sample.sender)
    setBody(sample.body)
    setFile(null)
    if (fileRef.current) fileRef.current.value = ''
    setError('')
  }

  const runAnalyze = async () => {
    setError('')
    if (!file && !subject.trim() && !body.trim()) {
      setError('Please paste an email or upload a .txt/.eml file first.')
      return
    }
    setLoading(true)
    try {
      let result
      if (file) {
        setStage('Uploading & parsing email…')
        result = await analyzeUpload(file)
      } else {
        setStage('Running ML classification…')
        result = await analyzeEmail({ subject, sender, body })
      }
      setStage('Analyzing threats…')
      navigate(`/result/${result._id}`, { state: { result } })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      setStage('')
    }
  }

  const onFileChange = (e) => {
    const f = e.target.files?.[0]
    setError('')
    if (f) {
      const ext = f.name.split('.').pop().toLowerCase()
      if (!['txt', 'eml'].includes(ext)) {
        setError('Unsupported file type. Please upload a .txt or .eml file.')
        setFile(null)
        e.target.value = ''
        return
      }
      setFile(f)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Input panel */}
      <div className="panel animate-fade-up p-5 lg:col-span-2">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Analyze an email</h2>
          <button onClick={clearAll} className="btn-ghost !py-1.5 !px-3 text-xs">
            <Trash2 className="h-3.5 w-3.5" /> Clear
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Subject</label>
              <input
                className="input"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Email subject line"
              />
            </div>
            <div>
              <label className="label">Sender</label>
              <input
                className="input"
                value={sender}
                onChange={(e) => setSender(e.target.value)}
                placeholder="sender@example.com"
              />
            </div>
          </div>

          <div>
            <label className="label">Email body</label>
            <textarea
              className="input min-h-[220px] font-mono text-[13px] leading-relaxed"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Paste the full email content here…"
            />
          </div>

          {/* Upload */}
          <div>
            <label className="label">Or upload an email file (.txt / .eml)</label>
            <input
              ref={fileRef}
              type="file"
              accept=".txt,.eml"
              onChange={onFileChange}
              className="hidden"
              id="email-upload"
            />
            <label
              htmlFor="email-upload"
              className="flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-slate-700 bg-slate-900/40 px-4 py-3.5 text-sm text-slate-400 transition-colors hover:border-indigo-500/50 hover:text-slate-200"
            >
              <Upload className="h-4 w-4" />
              {file ? (
                <span className="inline-flex items-center gap-2 text-slate-200">
                  <FileText className="h-4 w-4 text-indigo-400" />
                  {file.name}
                  <span className="text-xs text-slate-500">
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                </span>
              ) : (
                'Click to select a file (max 5 MB)'
              )}
            </label>
            {file && (
              <button
                onClick={() => { setFile(null); if (fileRef.current) fileRef.current.value = '' }}
                className="mt-2 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-red-400"
              >
                <X className="h-3.5 w-3.5" /> Remove file
              </button>
            )}
          </div>

          {error && (
            <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          <button onClick={runAnalyze} disabled={loading} className="btn-primary w-full !py-3.5">
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                {stage || 'Analyzing…'}
              </>
            ) : (
              <>
                <ScanSearch className="h-4 w-4" /> Analyze Email
              </>
            )}
          </button>
        </div>
      </div>

      {/* Samples panel */}
      <div className="space-y-4">
        <div className="panel animate-fade-up p-5">
          <div className="mb-3 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Sample emails</h3>
          </div>
          <div className="space-y-2">
            {SAMPLE_EMAILS.map((s) => (
              <button
                key={s.id}
                onClick={() => loadSample(s)}
                className="panel-hover flex w-full items-center justify-between rounded-xl border border-slate-800 bg-slate-900/50 px-3 py-2.5 text-left text-sm text-slate-300 transition-colors hover:text-white"
              >
                <span className="truncate pr-2">{s.label}</span>
                <span className="shrink-0 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  {s.tag}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="panel p-5">
          <div className="flex items-start gap-3">
            <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />
            <p className="text-xs leading-relaxed text-slate-400">
              Emails are analyzed by a trained ML model plus rule-based phishing
              detection and, when configured, Mistral AI. Nothing you submit is
              used to train the model.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
