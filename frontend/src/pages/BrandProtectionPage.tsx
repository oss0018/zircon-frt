import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Shield, Plus, Play, Trash2, Eye,
  Loader2, ExternalLink, X, Download,
} from 'lucide-react'
import clsx from 'clsx'
import { brandApi, type BrandWatch, type BrandAlert } from '../api/brand'

// ── Similarity Gauge ──────────────────────────────────────────────────────────
function SimilarityGauge({ score }: { score: number }) {
  const color = score >= 85 ? '#ef4444' : score >= 70 ? '#f59e0b' : '#22c55e'
  const pct = Math.min(100, Math.max(0, score))
  const r = 28
  const circ = 2 * Math.PI * r
  const dash = (pct / 100) * circ

  return (
    <div className="relative w-16 h-16 flex items-center justify-center">
      <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
        <circle cx="32" cy="32" r={r} fill="none" stroke="#1e2332" strokeWidth="6" />
        <circle cx="32" cy="32" r={r} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" />
      </svg>
      <span className="absolute text-xs font-bold" style={{ color }}>{Math.round(pct)}%</span>
    </div>
  )
}

// ── Add Brand Modal ───────────────────────────────────────────────────────────
function AddBrandModal({ onClose, onSave }: { onClose: () => void; onSave: (w: BrandWatch) => void }) {
  const { t } = useTranslation()
  const [form, setForm] = useState({
    name: '',
    original_url: '',
    keywords: '',
    description: '',
    similarity_threshold: 70,
    scan_schedule: 'daily',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSave = async () => {
    if (!form.name.trim() || !form.original_url.trim()) { setError(t('brand.requiredFields')); return }
    setSaving(true)
    setError('')
    try {
      const res = await brandApi.createWatch({
        name: form.name.trim(),
        original_url: form.original_url.trim(),
        keywords: form.keywords ? form.keywords.split(',').map((k) => k.trim()).filter(Boolean) : [],
        description: form.description.trim() || undefined,
        similarity_threshold: form.similarity_threshold,
        scan_schedule: form.scan_schedule,
      })
      onSave(res.data)
    } catch {
      setError(t('common.error'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-bg-secondary border border-bg-border rounded-2xl w-full max-w-lg space-y-4 p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-text-primary font-semibold text-lg">{t('brand.addBrand')}</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary"><X className="w-5 h-5" /></button>
        </div>

        {error && <div className="bg-accent-red/10 border border-accent-red/30 text-accent-red text-sm rounded-lg px-3 py-2">{error}</div>}

        <div className="space-y-3">
          <div>
            <label className="text-text-muted text-xs block mb-1">{t('brand.brandName')} *</label>
            <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="My Brand" className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green" />
          </div>
          <div>
            <label className="text-text-muted text-xs block mb-1">{t('brand.originalUrl')} *</label>
            <input value={form.original_url} onChange={(e) => setForm((f) => ({ ...f, original_url: e.target.value }))}
              placeholder="https://mybrand.com" className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green" />
          </div>
          <div>
            <label className="text-text-muted text-xs block mb-1">{t('brand.keywords')} ({t('brand.commaSeparated')})</label>
            <input value={form.keywords} onChange={(e) => setForm((f) => ({ ...f, keywords: e.target.value }))}
              placeholder="brand, trademark, product" className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green" />
          </div>
          <div>
            <label className="text-text-muted text-xs block mb-1">{t('brand.description')}</label>
            <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={2} className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green resize-none" />
          </div>
          <div>
            <label className="text-text-muted text-xs block mb-1">{t('brand.similarityThreshold')}: {form.similarity_threshold}%</label>
            <input type="range" min={0} max={100} value={form.similarity_threshold}
              onChange={(e) => setForm((f) => ({ ...f, similarity_threshold: Number(e.target.value) }))}
              className="w-full accent-accent-green" />
          </div>
          <div>
            <label className="text-text-muted text-xs block mb-1">{t('monitoring.schedule')}</label>
            <select value={form.scan_schedule} onChange={(e) => setForm((f) => ({ ...f, scan_schedule: e.target.value }))}
              className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green">
              <option value="hourly">{t('monitoring.scheduleHourly')}</option>
              <option value="daily">{t('monitoring.scheduleDaily')}</option>
              <option value="weekly">{t('monitoring.scheduleWeekly')}</option>
            </select>
          </div>
        </div>

        <div className="flex gap-2 pt-1">
          <button onClick={handleSave} disabled={saving} className="flex-1 py-2 bg-accent-green text-bg-primary text-sm font-medium rounded-lg hover:bg-accent-green/90 transition-colors disabled:opacity-50">
            {saving ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : t('brand.addBrand')}
          </button>
          <button onClick={onClose} className="px-4 py-2 border border-bg-border text-text-secondary text-sm rounded-lg hover:bg-white/5">{t('common.cancel')}</button>
        </div>
      </div>
    </div>
  )
}

// ── Alert Status Badge ────────────────────────────────────────────────────────
function AlertBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    new: 'bg-accent-red/10 text-accent-red border-accent-red/30',
    reviewed: 'bg-accent-green/10 text-accent-green border-accent-green/30',
    dismissed: 'bg-bg-border text-text-muted border-bg-border',
  }
  return <span className={clsx('px-2 py-0.5 rounded text-xs border', styles[status] || styles.new)}>{status}</span>
}

// ── Brand Detail View ─────────────────────────────────────────────────────────
function BrandDetailView({ watch, onBack }: { watch: BrandWatch; onBack: () => void }) {
  const { t } = useTranslation()
  const [alerts, setAlerts] = useState<BrandAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [exporting, setExporting] = useState<string | null>(null)

  useEffect(() => {
    brandApi.listAlerts(watch.id).then((r) => { setAlerts(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [watch.id])

  const handleScan = async () => {
    setScanning(true)
    try {
      await brandApi.triggerScan(watch.id)
    } finally {
      setTimeout(() => setScanning(false), 2000)
    }
  }

  const handleStatusUpdate = async (alertId: number, status: string) => {
    const res = await brandApi.updateAlertStatus(alertId, status)
    setAlerts((prev) => prev.map((a) => (a.id === alertId ? res.data : a)))
  }

  const exportAlerts = async (fmt: string) => {
    setExporting(fmt)
    try {
      const token = localStorage.getItem('token') || sessionStorage.getItem('token') || ''
      const url = `/api/v1/export/brand/${watch.id}/alerts?fmt=${fmt}`
      const resp = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      if (!resp.ok) throw new Error(`Export failed: ${resp.status}`)
      const blob = await resp.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `brand_alerts_${watch.name}.${fmt}`
      a.click()
    } catch (err) {
      console.error('Export error:', err)
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={onBack} className="text-text-muted hover:text-text-primary text-sm">&larr; {t('common.back')}</button>
        <h2 className="text-xl font-bold text-text-primary">{watch.name}</h2>
        <a href={watch.original_url} target="_blank" rel="noopener noreferrer" className="text-text-muted hover:text-accent-cyan">
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        <button onClick={handleScan} disabled={scanning} className="flex items-center gap-2 px-4 py-2 bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/30 rounded-lg text-sm hover:bg-accent-cyan/20 transition-colors disabled:opacity-50">
          {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {t('brand.deepScan')}
        </button>
        <span className="text-text-muted text-xs">{t('brand.lastScan')}: {watch.last_scan ? new Date(watch.last_scan).toLocaleString() : t('monitoring.neverChecked')}</span>
        {alerts.length > 0 && (
          <div className="flex items-center gap-2 ml-auto">
            <span className="text-text-muted text-xs flex items-center gap-1">
              <Download className="w-3.5 h-3.5" />
              {t('export.exportAlerts')}:
            </span>
            {(['csv', 'json', 'pdf'] as const).map((fmt) => (
              <button
                key={fmt}
                onClick={() => exportAlerts(fmt)}
                disabled={exporting !== null}
                className="px-3 py-1 text-xs border border-bg-border text-text-secondary rounded-lg hover:border-accent-cyan/50 hover:text-accent-cyan transition-colors disabled:opacity-50"
              >
                {exporting === fmt ? t('export.exporting') : t(`export.export${fmt.charAt(0).toUpperCase() + fmt.slice(1)}`)}
              </button>
            ))}
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-accent-green" /></div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-12 text-text-muted">{t('brand.noAlerts')}</div>
      ) : (
        <div className="bg-bg-secondary border border-bg-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-bg-border">
              <tr className="text-text-muted text-xs">
                <th className="text-left px-4 py-3">{t('brand.foundDomain')}</th>
                <th className="text-left px-4 py-3">{t('brand.similarity')}</th>
                <th className="text-left px-4 py-3">{t('brand.sources')}</th>
                <th className="text-left px-4 py-3">{t('brand.alertStatus')}</th>
                <th className="text-left px-4 py-3">{t('files.date')}</th>
                <th className="text-left px-4 py-3">{t('files.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id} className="border-b border-bg-border/50 hover:bg-white/5 transition-colors">
                  <td className="px-4 py-3 font-mono text-text-primary">{alert.found_domain}</td>
                  <td className="px-4 py-3">
                    <SimilarityGauge score={alert.similarity_score} />
                  </td>
                  <td className="px-4 py-3 text-text-secondary text-xs">{alert.detection_sources?.join(', ') || '—'}</td>
                  <td className="px-4 py-3"><AlertBadge status={alert.status} /></td>
                  <td className="px-4 py-3 text-text-muted text-xs">{new Date(alert.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      {alert.status === 'new' && (
                        <>
                          <button onClick={() => handleStatusUpdate(alert.id, 'reviewed')} className="text-xs text-accent-green hover:underline">{t('brand.markReviewed')}</button>
                          <button onClick={() => handleStatusUpdate(alert.id, 'dismissed')} className="text-xs text-text-muted hover:underline">{t('brand.dismiss')}</button>
                        </>
                      )}
                      {alert.status !== 'new' && (
                        <button onClick={() => handleStatusUpdate(alert.id, 'new')} className="text-xs text-text-muted hover:underline">{t('brand.reopen')}</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// ── Brand Card ────────────────────────────────────────────────────────────────
function BrandCard({
  watch,
  onView,
  onScan,
  onDelete,
  scanning,
}: {
  watch: BrandWatch
  onView: () => void
  onScan: () => void
  onDelete: () => void
  scanning: boolean
}) {
  const { t } = useTranslation()
  return (
    <div className="bg-bg-secondary border border-bg-border rounded-xl p-5 space-y-4 hover:border-accent-green/30 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-text-primary font-semibold">{watch.name}</h3>
          <a href={watch.original_url} target="_blank" rel="noopener noreferrer" className="text-text-muted text-xs hover:text-accent-cyan flex items-center gap-1 mt-0.5">
            {watch.original_url}
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
        <SimilarityGauge score={watch.similarity_threshold} />
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-bg-primary rounded-lg p-2">
          <div className="text-text-primary font-bold text-lg">{watch.alert_count}</div>
          <div className="text-text-muted text-xs">{t('brand.total')}</div>
        </div>
        <div className="bg-accent-red/5 rounded-lg p-2">
          <div className="text-accent-red font-bold text-lg">{watch.new_alert_count}</div>
          <div className="text-text-muted text-xs">{t('brand.new')}</div>
        </div>
        <div className="bg-accent-green/5 rounded-lg p-2">
          <div className="text-accent-green font-bold text-lg">{watch.alert_count - watch.new_alert_count}</div>
          <div className="text-text-muted text-xs">{t('brand.reviewed')}</div>
        </div>
      </div>

      <div className="text-text-muted text-xs">
        {t('brand.lastScan')}: {watch.last_scan ? new Date(watch.last_scan).toLocaleString() : t('monitoring.neverChecked')}
      </div>

      <div className="flex gap-2">
        <button onClick={onView} className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-accent-green/10 text-accent-green text-xs rounded-lg hover:bg-accent-green/20 transition-colors">
          <Eye className="w-3.5 h-3.5" />{t('brand.viewDetails')}
        </button>
        <button onClick={onScan} disabled={scanning} className="flex items-center justify-center gap-1.5 px-3 py-2 bg-accent-cyan/10 text-accent-cyan text-xs rounded-lg hover:bg-accent-cyan/20 transition-colors disabled:opacity-50">
          {scanning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
        </button>
        <button onClick={onDelete} className="flex items-center justify-center px-3 py-2 text-text-muted hover:text-accent-red transition-colors">
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function BrandProtectionPage() {
  const { t } = useTranslation()
  const [watches, setWatches] = useState<BrandWatch[]>([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [selected, setSelected] = useState<BrandWatch | null>(null)
  const [scanning, setScanning] = useState<number | null>(null)

  useEffect(() => {
    brandApi.listWatches().then((r) => { setWatches(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleScan = async (id: number) => {
    setScanning(id)
    try {
      await brandApi.triggerScan(id)
    } finally {
      setTimeout(() => setScanning(null), 2000)
    }
  }

  const handleDelete = async (id: number) => {
    await brandApi.deleteWatch(id)
    setWatches((prev) => prev.filter((w) => w.id !== id))
  }

  if (selected) {
    return (
      <div className="p-6">
        <BrandDetailView watch={selected} onBack={() => setSelected(null)} />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">{t('brand.title')}</h1>
          <p className="text-text-muted text-sm mt-1">{t('brand.subtitle')}</p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 px-4 py-2 bg-accent-green text-bg-primary text-sm font-medium rounded-lg hover:bg-accent-green/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          {t('brand.addBrand')}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-accent-green" /></div>
      ) : watches.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <Shield className="w-16 h-16 text-text-muted mb-4" />
          <h3 className="text-text-primary font-medium mb-2">{t('brand.noWatches')}</h3>
          <p className="text-text-muted text-sm mb-6">{t('brand.noWatchesDesc')}</p>
          <button onClick={() => setShowAdd(true)} className="flex items-center gap-2 px-4 py-2 bg-accent-green text-bg-primary text-sm font-medium rounded-lg hover:bg-accent-green/90">
            <Plus className="w-4 h-4" />{t('brand.addBrand')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {watches.map((watch) => (
            <BrandCard
              key={watch.id}
              watch={watch}
              onView={() => setSelected(watch)}
              onScan={() => handleScan(watch.id)}
              onDelete={() => handleDelete(watch.id)}
              scanning={scanning === watch.id}
            />
          ))}
        </div>
      )}

      {showAdd && (
        <AddBrandModal
          onClose={() => setShowAdd(false)}
          onSave={(w) => { setWatches((prev) => [w, ...prev]); setShowAdd(false) }}
        />
      )}
    </div>
  )
}
