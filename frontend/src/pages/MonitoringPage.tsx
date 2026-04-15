import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Activity, Eye, Search, Folder, Clock, Plus, Play, Trash2, RefreshCw,
  CheckCircle, AlertTriangle, XCircle, Loader2, ChevronDown, ChevronRight,
} from 'lucide-react'
import clsx from 'clsx'
import { monitoringApi, type WatchlistItem, type SearchTemplate, type FolderStatus } from '../api/monitoring'

type Tab = 'watchlist' | 'searches' | 'folder' | 'activity'

const TABS: { id: Tab; labelKey: string; Icon: React.FC<{ className?: string }> }[] = [
  { id: 'watchlist', labelKey: 'monitoring.watchlist', Icon: Eye },
  { id: 'searches', labelKey: 'monitoring.savedSearches', Icon: Search },
  { id: 'folder', labelKey: 'monitoring.folderMonitor', Icon: Folder },
  { id: 'activity', labelKey: 'monitoring.activityLog', Icon: Activity },
]

const WATCHLIST_TYPES = ['email', 'domain', 'ip', 'keyword', 'brand']
const DEFAULT_SERVICES: Record<string, string[]> = {
  email: ['hibp', 'intelx', 'hudsonrock'],
  domain: ['virustotal', 'urlhaus', 'securitytrails'],
  ip: ['shodan', 'abuseipdb', 'alienvault_otx'],
  keyword: ['intelx'],
  brand: ['securitytrails', 'virustotal'],
}

function StatusBadge({ active }: { active: boolean }) {
  return active ? (
    <span className="flex items-center gap-1 text-xs text-accent-green"><CheckCircle className="w-3 h-3" /> Active</span>
  ) : (
    <span className="flex items-center gap-1 text-xs text-text-muted"><XCircle className="w-3 h-3" /> Inactive</span>
  )
}

// ── Watchlist Tab ─────────────────────────────────────────────────────────────
function WatchlistTab() {
  const { t } = useTranslation()
  const [items, setItems] = useState<WatchlistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ type: 'email', value: '', schedule: '' })
  const [saving, setSaving] = useState(false)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [checking, setChecking] = useState<number | null>(null)

  useEffect(() => {
    monitoringApi.listWatchlist().then((r) => { setItems(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleAdd = async () => {
    if (!form.value.trim()) return
    setSaving(true)
    try {
      const res = await monitoringApi.createWatchlistItem({
        type: form.type,
        value: form.value.trim(),
        services: DEFAULT_SERVICES[form.type],
        schedule: form.schedule || undefined,
      })
      setItems((prev) => [res.data, ...prev])
      setForm({ type: 'email', value: '', schedule: '' })
      setShowAdd(false)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    await monitoringApi.deleteWatchlistItem(id)
    setItems((prev) => prev.filter((i) => i.id !== id))
  }

  const handleCheck = async (id: number) => {
    setChecking(id)
    try {
      await monitoringApi.checkWatchlistItem(id)
    } finally {
      setTimeout(() => setChecking(null), 1500)
    }
  }

  const handleToggle = async (item: WatchlistItem) => {
    const res = await monitoringApi.updateWatchlistItem(item.id, { is_active: !item.is_active })
    setItems((prev) => prev.map((i) => (i.id === item.id ? res.data : i)))
  }

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-accent-green" /></div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-text-secondary text-sm">{t('monitoring.watchlistDesc')}</p>
        <button
          onClick={() => setShowAdd((v) => !v)}
          className="flex items-center gap-2 px-4 py-2 bg-accent-green/10 text-accent-green border border-accent-green/30 rounded-lg text-sm hover:bg-accent-green/20 transition-colors"
        >
          <Plus className="w-4 h-4" />
          {t('monitoring.addItem')}
        </button>
      </div>

      {showAdd && (
        <div className="bg-bg-secondary border border-bg-border rounded-xl p-4 space-y-3">
          <h3 className="text-text-primary font-medium text-sm">{t('monitoring.addWatchlistItem')}</h3>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-text-muted text-xs block mb-1">{t('monitoring.type')}</label>
              <select
                value={form.type}
                onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
                className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green"
              >
                {WATCHLIST_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="text-text-muted text-xs block mb-1">{t('monitoring.value')}</label>
              <input
                value={form.value}
                onChange={(e) => setForm((f) => ({ ...f, value: e.target.value }))}
                placeholder={form.type === 'email' ? 'user@example.com' : form.type === 'domain' ? 'example.com' : form.type === 'ip' ? '1.2.3.4' : 'keyword'}
                className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green"
              />
            </div>
            <div>
              <label className="text-text-muted text-xs block mb-1">{t('monitoring.schedule')}</label>
              <select
                value={form.schedule}
                onChange={(e) => setForm((f) => ({ ...f, schedule: e.target.value }))}
                className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green"
              >
                <option value="">{t('monitoring.scheduleNone')}</option>
                <option value="hourly">{t('monitoring.scheduleHourly')}</option>
                <option value="daily">{t('monitoring.scheduleDaily')}</option>
                <option value="weekly">{t('monitoring.scheduleWeekly')}</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <button onClick={handleAdd} disabled={saving} className="px-4 py-2 bg-accent-green text-bg-primary text-sm font-medium rounded-lg hover:bg-accent-green/90 transition-colors disabled:opacity-50">
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : t('common.save')}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-4 py-2 border border-bg-border text-text-secondary text-sm rounded-lg hover:bg-white/5 transition-colors">
              {t('common.cancel')}
            </button>
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <div className="text-center py-12 text-text-muted">{t('monitoring.noWatchlistItems')}</div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} className="bg-bg-secondary border border-bg-border rounded-xl overflow-hidden">
              <div className="flex items-center gap-4 px-4 py-3">
                <button onClick={() => setExpanded(expanded === item.id ? null : item.id)} className="text-text-muted hover:text-text-primary">
                  {expanded === item.id ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </button>
                <span className="px-2 py-0.5 bg-accent-cyan/10 text-accent-cyan text-xs rounded font-mono">{item.type}</span>
                <span className="text-text-primary text-sm font-mono flex-1">{item.value}</span>
                <span className="text-text-muted text-xs">{item.last_checked ? new Date(item.last_checked).toLocaleString() : t('monitoring.neverChecked')}</span>
                <StatusBadge active={item.is_active} />
                <div className="flex items-center gap-2">
                  <button onClick={() => handleCheck(item.id)} disabled={checking === item.id} className="p-1.5 text-text-muted hover:text-accent-cyan transition-colors" title={t('monitoring.checkNow')}>
                    {checking === item.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  </button>
                  <button onClick={() => handleToggle(item)} className="p-1.5 text-text-muted hover:text-accent-green transition-colors" title={t('monitoring.toggle')}>
                    <RefreshCw className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDelete(item.id)} className="p-1.5 text-text-muted hover:text-accent-red transition-colors" title={t('common.delete')}>
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {expanded === item.id && (
                <div className="px-10 pb-3 text-xs text-text-secondary space-y-1 border-t border-bg-border/50 pt-2">
                  <div><span className="text-text-muted">{t('monitoring.services')}:</span> {item.services?.join(', ') || '—'}</div>
                  <div><span className="text-text-muted">{t('monitoring.schedule')}:</span> {item.schedule || t('monitoring.scheduleNone')}</div>
                  {item.history && item.history.length > 0 && (
                    <div className="mt-2">
                      <div className="text-text-muted mb-1">{t('monitoring.recentChecks')}:</div>
                      {item.history.slice(0, 3).map((h) => (
                        <div key={h.id} className="flex items-center gap-2">
                          {h.has_findings ? <AlertTriangle className="w-3 h-3 text-yellow-400" /> : <CheckCircle className="w-3 h-3 text-accent-green" />}
                          <span>{new Date(h.checked_at).toLocaleString()}</span>
                          <span className={h.has_findings ? 'text-yellow-400' : 'text-accent-green'}>{h.has_findings ? 'Findings' : 'Clean'}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Saved Searches Tab ────────────────────────────────────────────────────────
function SavedSearchesTab() {
  const { t } = useTranslation()
  const [templates, setTemplates] = useState<SearchTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ name: '', query: '', schedule: '' })
  const [saving, setSaving] = useState(false)
  const [running, setRunning] = useState<number | null>(null)

  useEffect(() => {
    monitoringApi.listSearchTemplates().then((r) => { setTemplates(r.data); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleAdd = async () => {
    if (!form.name.trim() || !form.query.trim()) return
    setSaving(true)
    try {
      const res = await monitoringApi.createSearchTemplate({ name: form.name, query: form.query, schedule: form.schedule || undefined })
      setTemplates((prev) => [res.data, ...prev])
      setForm({ name: '', query: '', schedule: '' })
      setShowAdd(false)
    } finally {
      setSaving(false)
    }
  }

  const handleRun = async (id: number) => {
    setRunning(id)
    try {
      await monitoringApi.runSearchTemplate(id)
    } finally {
      setTimeout(() => setRunning(null), 1500)
    }
  }

  const handleDelete = async (id: number) => {
    await monitoringApi.deleteSearchTemplate(id)
    setTemplates((prev) => prev.filter((t) => t.id !== id))
  }

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-accent-green" /></div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-text-secondary text-sm">{t('monitoring.savedSearchesDesc')}</p>
        <button onClick={() => setShowAdd((v) => !v)} className="flex items-center gap-2 px-4 py-2 bg-accent-green/10 text-accent-green border border-accent-green/30 rounded-lg text-sm hover:bg-accent-green/20 transition-colors">
          <Plus className="w-4 h-4" />{t('monitoring.saveSearch')}
        </button>
      </div>

      {showAdd && (
        <div className="bg-bg-secondary border border-bg-border rounded-xl p-4 space-y-3">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-text-muted text-xs block mb-1">{t('monitoring.searchName')}</label>
              <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="My search..." className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green" />
            </div>
            <div>
              <label className="text-text-muted text-xs block mb-1">{t('monitoring.searchQuery')}</label>
              <input value={form.query} onChange={(e) => setForm((f) => ({ ...f, query: e.target.value }))} placeholder="query AND term" className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green" />
            </div>
            <div>
              <label className="text-text-muted text-xs block mb-1">{t('monitoring.schedule')}</label>
              <select value={form.schedule} onChange={(e) => setForm((f) => ({ ...f, schedule: e.target.value }))} className="w-full bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-green">
                <option value="">{t('monitoring.scheduleNone')}</option>
                <option value="daily">{t('monitoring.scheduleDaily')}</option>
                <option value="weekly">{t('monitoring.scheduleWeekly')}</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={handleAdd} disabled={saving} className="px-4 py-2 bg-accent-green text-bg-primary text-sm font-medium rounded-lg hover:bg-accent-green/90 transition-colors disabled:opacity-50">
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : t('common.save')}
            </button>
            <button onClick={() => setShowAdd(false)} className="px-4 py-2 border border-bg-border text-text-secondary text-sm rounded-lg hover:bg-white/5">{t('common.cancel')}</button>
          </div>
        </div>
      )}

      {templates.length === 0 ? (
        <div className="text-center py-12 text-text-muted">{t('monitoring.noSavedSearches')}</div>
      ) : (
        <div className="space-y-2">
          {templates.map((tmpl) => (
            <div key={tmpl.id} className="flex items-center gap-4 bg-bg-secondary border border-bg-border rounded-xl px-4 py-3">
              <Search className="w-4 h-4 text-accent-cyan shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-text-primary text-sm font-medium">{tmpl.name}</div>
                <div className="text-text-muted text-xs font-mono truncate">{tmpl.query}</div>
              </div>
              {tmpl.schedule && (
                <span className="flex items-center gap-1 text-xs text-text-muted"><Clock className="w-3 h-3" />{tmpl.schedule}</span>
              )}
              <div className="flex items-center gap-2">
                <button onClick={() => handleRun(tmpl.id)} disabled={running === tmpl.id} className="p-1.5 text-text-muted hover:text-accent-cyan transition-colors" title={t('monitoring.runNow')}>
                  {running === tmpl.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                </button>
                <button onClick={() => handleDelete(tmpl.id)} className="p-1.5 text-text-muted hover:text-accent-red transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Folder Monitor Tab ────────────────────────────────────────────────────────
function FolderMonitorTab() {
  const { t } = useTranslation()
  const [status, setStatus] = useState<FolderStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)

  const fetchStatus = () => {
    monitoringApi.getFolderStatus().then((r) => { setStatus(r.data); setLoading(false) }).catch(() => setLoading(false))
  }

  useEffect(() => { fetchStatus() }, [])

  const handleScan = async () => {
    setScanning(true)
    try {
      await monitoringApi.triggerFolderScan()
      setTimeout(() => { fetchStatus(); setScanning(false) }, 2000)
    } catch {
      setScanning(false)
    }
  }

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-accent-green" /></div>
  if (!status) return <div className="text-center py-12 text-text-muted">{t('common.error')}</div>

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-bg-secondary border border-bg-border rounded-xl p-4">
          <div className="text-text-muted text-xs mb-1">{t('monitoring.monitoredDir')}</div>
          <div className="text-text-primary text-sm font-mono">{status.monitored_dir}</div>
        </div>
        <div className="bg-bg-secondary border border-bg-border rounded-xl p-4">
          <div className="text-text-muted text-xs mb-1">{t('monitoring.status')}</div>
          <div className={clsx('text-sm font-medium', status.exists ? 'text-accent-green' : 'text-accent-red')}>
            {status.exists ? t('monitoring.dirExists') : t('monitoring.dirMissing')}
          </div>
        </div>
        <div className="bg-bg-secondary border border-bg-border rounded-xl p-4">
          <div className="text-text-muted text-xs mb-1">{t('monitoring.trackedFiles')}</div>
          <div className="text-text-primary text-2xl font-bold">{status.tracked_files}</div>
        </div>
      </div>

      <div className="flex justify-end">
        <button onClick={handleScan} disabled={scanning} className="flex items-center gap-2 px-4 py-2 bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/30 rounded-lg text-sm hover:bg-accent-cyan/20 transition-colors disabled:opacity-50">
          {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          {t('monitoring.scanNow')}
        </button>
      </div>

      {status.last_known_hashes.length > 0 && (
        <div className="bg-bg-secondary border border-bg-border rounded-xl p-4">
          <h3 className="text-text-primary text-sm font-medium mb-3">{t('monitoring.trackedFilesLabel')}</h3>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {status.last_known_hashes.map((path) => (
              <div key={path} className="text-text-muted text-xs font-mono truncate">{path}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Activity Log Tab ─────────────────────────────────────────────────────────
function ActivityLogTab() {
  const { t } = useTranslation()
  const [history, setHistory] = useState<{ id: number; watchlist_item_id: number; has_findings: boolean; checked_at: string }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    monitoringApi.getHistory(50).then((r) => { setHistory(r.data.history || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-accent-green" /></div>

  return (
    <div className="space-y-2">
      {history.length === 0 ? (
        <div className="text-center py-12 text-text-muted">{t('monitoring.noActivity')}</div>
      ) : (
        history.map((entry) => (
          <div key={entry.id} className="flex items-center gap-4 bg-bg-secondary border border-bg-border rounded-xl px-4 py-3">
            {entry.has_findings ? (
              <AlertTriangle className="w-4 h-4 text-yellow-400 shrink-0" />
            ) : (
              <CheckCircle className="w-4 h-4 text-accent-green shrink-0" />
            )}
            <div className="flex-1">
              <span className="text-text-secondary text-sm">{t('monitoring.watchlistCheck')} #{entry.watchlist_item_id}</span>
            </div>
            <span className={clsx('text-xs', entry.has_findings ? 'text-yellow-400' : 'text-accent-green')}>
              {entry.has_findings ? t('monitoring.findings') : t('monitoring.clean')}
            </span>
            <span className="text-text-muted text-xs">{new Date(entry.checked_at).toLocaleString()}</span>
          </div>
        ))
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function MonitoringPage() {
  const { t } = useTranslation()
  const [tab, setTab] = useState<Tab>('watchlist')

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">{t('monitoring.title')}</h1>
        <p className="text-text-muted text-sm mt-1">{t('monitoring.subtitle')}</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-bg-secondary border border-bg-border rounded-xl p-1">
        {TABS.map(({ id, labelKey, Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={clsx(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all flex-1 justify-center',
              tab === id
                ? 'bg-accent-green/10 text-accent-green border border-accent-green/20'
                : 'text-text-secondary hover:text-text-primary hover:bg-white/5',
            )}
          >
            <Icon className="w-4 h-4" />
            {t(labelKey)}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div>
        {tab === 'watchlist' && <WatchlistTab />}
        {tab === 'searches' && <SavedSearchesTab />}
        {tab === 'folder' && <FolderMonitorTab />}
        {tab === 'activity' && <ActivityLogTab />}
      </div>
    </div>
  )
}
