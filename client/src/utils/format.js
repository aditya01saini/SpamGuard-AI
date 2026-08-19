export const pct = (value, digits = 1) => {
  if (value == null) return '—'
  return `${(Number(value) * 100).toFixed(digits)}%`
}

export const fmtDate = (iso) => {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export const truncate = (str, n = 80) =>
  str && str.length > n ? `${str.slice(0, n)}…` : str
