import { useEffect, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Shield, CheckCircle, XCircle, AlertCircle, Eye, EyeOff,
  RefreshCw, Search, Download, Activity,
} from 'lucide-react'
import clsx from 'clsx'
import {
  integrationsApi,
  ServiceCatalogueEntry,
  IntegrationResponse,
  UnifiedSearchResult,
  UsageStatsEntry,
} from '../api/integrations'

// ---------- helpers ----------
const CATEGORY_LABELS: Record<string, string> = {
  breach: 'Breach / Leak',
  phishing: 'Phishing / Malware',
  infrastructure: 'Infrastructure',
  threat_intel: 'Threat Intelligence',
}

const STATUS_DOT: Record<string, string> = {
  active: 'bg-accent-green shadow-[0_0_6px_#39ff14]',
  error: 'bg-red-500',
  inactive: 'bg-gray-500',
}

function statusOf(entry: ServiceCatalogueEntry): 'active' | 'inactive' {
  return entry.is_active ? 'active' : 'inactive'
}

// ---------- Modal ----------
function ConfigureModal({
  entry,
  integration,
  onSave,
  onClose,
}: {
  entry: ServiceCatalogueEntry
  integration: IntegrationResponse | null
  onSave: (apiKey: string) => Promise<void>
  onClose: () => void
}) {
  const { t } = useTranslation()
  const [apiKey, setApiKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ status: string; message: string } | null>(null)
  const [saving, setSaving] = useState(false)

  const handleTest = async () => {
    if (!integration) return
    setTesting(true)
    setTestResult(null)
    try {
      const res = await integrationsApi.test(integration.id)
      setTestResult(res)
    } catch {
      setTestResult({ status: 'error', message: 'Request failed' })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await onSave(apiKey)
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-bg-secondary border border-bg-border rounded-xl w-full max-w-md mx-4 p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-text-primary font-semibold text-lg">{entry.display_name}</h2>
            <p className="text-text-muted text-xs mt-0.5">{entry.description}</p>
          </div>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary">
            <XCircle className="w-5 h-5" />
          </button>
        </div>

        {/* API Key */}
        <div className="mb-4">
          <label className="block text-text-secondary text-sm mb-1.5">
            {t('integrations.apiKey')}
          </label>
          <div className="flex gap-2">
            <input
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={integration ? '••••••••••••••••' : t('integrations.enterApiKey')}
              className="flex-1 bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-green/50"
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="text-text-muted hover:text-text-primary px-2"
            >
              {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Info */}
        <div className="grid grid-cols-2 gap-3 mb-5 text-xs">
          <div className="bg-bg-primary border border-bg-border rounded-lg p-3">
            <div className="text-text-muted mb-1">{t('integrations.rateLimit')}</div>
            <div className="text-text-primary font-mono">{entry.rate_limit} req/min</div>
          </div>
          <div className="bg-bg-primary border border-bg-border rounded-lg p-3">
            <div className="text-text-muted mb-1">{t('integrations.queryTypes')}</div>
            <div className="text-text-primary font-mono">{entry.query_types.join(', ')}</div>
          </div>
        </div>

        {/* Test result */}
        {testResult && (
          <div
            className={clsx(
              'flex items-center gap-2 text-sm rounded-lg px-3 py-2 mb-4',
              testResult.status === 'ok'
                ? 'bg-accent-green/10 text-accent-green border border-accent-green/20'
                : 'bg-red-500/10 text-red-400 border border-red-500/20',
            )}
          >
            {testResult.status === 'ok' ? (
              <CheckCircle className="w-4 h-4 shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 shrink-0" />
            )}
            {testResult.message}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          {integration && (
            <button
              onClick={handleTest}
              disabled={testing}
              className="flex items-center gap-2 px-3 py-2 text-sm border border-bg-border rounded-lg text-text-secondary hover:text-text-primary hover:border-accent-green/30 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={clsx('w-4 h-4', testing && 'animate-spin')} />
              {t('integrations.testConnection')}
            </button>
          )}
          <div className="flex-1" />
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary"
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !apiKey}
            className="px-4 py-2 text-sm bg-accent-green/20 text-accent-green border border-accent-green/30 rounded-lg hover:bg-accent-green/30 transition-colors disabled:opacity-40"
          >
            {saving ? t('common.loading') : t('common.save')}
          </button>
        </div>
      </div>
    </div>
  )
}

// ---------- Integration Card ----------
function IntegrationCard({
  entry,
  integration,
  onConfigure,
  onToggle,
}: {
  entry: ServiceCatalogueEntry
  integration: IntegrationResponse | null
  onConfigure: () => void
  onToggle: () => void
}) {
  const { t } = useTranslation()
  const st = statusOf(entry)

  const CATEGORY_BORDER: Record<string, string> = {
    breach: 'border-red-500/20 hover:border-red-500/40',
    phishing: 'border-orange-500/20 hover:border-orange-500/40',
    infrastructure: 'border-blue-500/20 hover:border-blue-500/40',
    threat_intel: 'border-purple-500/20 hover:border-purple-500/40',
  }

  return (
    <div
      className={clsx(
        'bg-bg-secondary border rounded-xl p-5 flex flex-col gap-4 transition-colors',
        CATEGORY_BORDER[entry.category] ?? 'border-bg-border hover:border-accent-green/30',
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-bg-primary border border-bg-border flex items-center justify-center">
            <Shield className="w-5 h-5 text-text-muted" />
          </div>
          <div>
            <div className="text-text-primary font-semibold text-sm">{entry.display_name}</div>
            <div className="text-text-muted text-xs capitalize">{CATEGORY_LABELS[entry.category] ?? entry.category}</div>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={clsx('w-2 h-2 rounded-full', STATUS_DOT[st])} />
          <span className="text-text-muted text-xs">{t(`integrations.status.${st}`)}</span>
        </div>
      </div>

      {/* Description */}
      <p className="text-text-secondary text-xs leading-relaxed">{entry.description}</p>

      {/* Meta */}
      {integration?.last_check && (
        <div className="text-text-muted text-xs">
          {t('integrations.lastChecked')}: {new Date(integration.last_check).toLocaleString()}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-auto">
        {entry.is_configured && (
          <button
            onClick={onToggle}
            className={clsx(
              'flex-1 py-1.5 text-xs rounded-lg border transition-colors',
              entry.is_active
                ? 'border-red-500/30 text-red-400 hover:bg-red-500/10'
                : 'border-accent-green/30 text-accent-green hover:bg-accent-green/10',
            )}
          >
            {entry.is_active ? t('integrations.disable') : t('integrations.enable')}
          </button>
        )}
        <button
          onClick={onConfigure}
          className="flex-1 py-1.5 text-xs rounded-lg border border-bg-border text-text-secondary hover:text-text-primary hover:border-accent-green/30 transition-colors"
        >
          {t('integrations.configure')}
        </button>
      </div>
    </div>
  )
}

// ---------- Search Panel ----------
function OsintSearchPanel({
  availableServices,
  userIntegrations,
}: {
  availableServices: ServiceCatalogueEntry[]
  userIntegrations: IntegrationResponse[]
}) {
  const { t } = useTranslation()
  const [query, setQuery] = useState('')
  const [queryType, setQueryType] = useState('domain')
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<UnifiedSearchResult[]>([])
  const [activeTab, setActiveTab] = useState<string | null>(null)

  const activeIntegrationNames = userIntegrations
    .filter((i) => i.is_active)
    .map((i) => i.service_name)

  const toggleService = (name: string) => {
    setSelectedServices((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name],
    )
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setResults([])
    setActiveTab(null)
    try {
      const res = await integrationsApi.search({
        query,
        query_type: queryType,
        services: selectedServices.length ? selectedServices : undefined,
      })
      setResults(res.results)
      if (res.results.length > 0) setActiveTab(res.results[0].service)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = (format: 'json' | 'csv') => {
    const data = results.flatMap((r) => r.results.map((item) => ({ service: r.service, ...item })))
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `osint-results-${Date.now()}.json`
      a.click()
    } else {
      if (data.length === 0) return
      const keys = Object.keys(data[0])
      const csv = [keys.join(','), ...data.map((row) => keys.map((k) => JSON.stringify((row as Record<string, unknown>)[k] ?? '')).join(','))].join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `osint-results-${Date.now()}.csv`
      a.click()
    }
  }

  const activeResults = results.find((r) => r.service === activeTab)

  return (
    <div className="bg-bg-secondary border border-bg-border rounded-xl p-6">
      <h2 className="text-text-primary font-semibold mb-5 flex items-center gap-2">
        <Search className="w-5 h-5 text-accent-green" />
        {t('integrations.unifiedSearch')}
      </h2>

      {/* Search bar */}
      <div className="flex gap-3 mb-4">
        <select
          value={queryType}
          onChange={(e) => setQueryType(e.target.value)}
          className="bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-green/50"
        >
          {['email', 'domain', 'ip', 'url', 'hash', 'username'].map((qt) => (
            <option key={qt} value={qt}>{qt}</option>
          ))}
        </select>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder={t('integrations.searchPlaceholder')}
          className="flex-1 bg-bg-primary border border-bg-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-green/50"
        />
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="flex items-center gap-2 px-5 py-2 bg-accent-green/20 text-accent-green border border-accent-green/30 rounded-lg text-sm hover:bg-accent-green/30 transition-colors disabled:opacity-40"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          {t('integrations.searchAll')}
        </button>
      </div>

      {/* Service checkboxes */}
      <div className="flex flex-wrap gap-2 mb-5">
        {activeIntegrationNames.map((name) => {
          const entry = availableServices.find((e) => e.name === name)
          const checked = selectedServices.includes(name)
          return (
            <button
              key={name}
              onClick={() => toggleService(name)}
              className={clsx(
                'px-3 py-1 rounded-full text-xs border transition-colors',
                checked
                  ? 'bg-accent-green/20 text-accent-green border-accent-green/40'
                  : 'bg-bg-primary text-text-secondary border-bg-border hover:border-accent-green/30',
              )}
            >
              {entry?.display_name ?? name}
            </button>
          )
        })}
        {activeIntegrationNames.length === 0 && (
          <span className="text-text-muted text-sm">{t('integrations.noActiveIntegrations')}</span>
        )}
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div>
          {/* Tabs */}
          <div className="flex gap-1 border-b border-bg-border mb-4 overflow-x-auto">
            {results.map((r) => (
              <button
                key={r.service}
                onClick={() => setActiveTab(r.service)}
                className={clsx(
                  'px-4 py-2 text-sm border-b-2 whitespace-nowrap transition-colors',
                  activeTab === r.service
                    ? 'border-accent-green text-accent-green'
                    : 'border-transparent text-text-secondary hover:text-text-primary',
                )}
              >
                {r.display_name}
                {r.error && <AlertCircle className="inline w-3 h-3 ml-1 text-red-400" />}
                <span className="ml-1 text-xs text-text-muted">({r.results.length})</span>
              </button>
            ))}
          </div>

          {/* Export */}
          <div className="flex justify-end gap-2 mb-4">
            <button
              onClick={() => handleExport('json')}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-bg-border rounded-lg text-text-secondary hover:text-text-primary hover:border-accent-green/30 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              JSON
            </button>
            <button
              onClick={() => handleExport('csv')}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-bg-border rounded-lg text-text-secondary hover:text-text-primary hover:border-accent-green/30 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              CSV
            </button>
          </div>

          {/* Active tab results */}
          {activeResults && (
            <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
              {activeResults.error && (
                <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                  <XCircle className="w-4 h-4 shrink-0" />
                  {activeResults.error}
                </div>
              )}
              {activeResults.results.length === 0 && !activeResults.error && (
                <div className="text-text-muted text-sm text-center py-6">{t('integrations.noResults')}</div>
              )}
              {activeResults.results.map((item, idx) => (
                <div key={idx} className="bg-bg-primary border border-bg-border rounded-lg p-3">
                  <pre className="text-text-secondary text-xs overflow-x-auto whitespace-pre-wrap break-words">
                    {JSON.stringify(item, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ---------- Usage Dashboard ----------
function UsageDashboard({ stats }: { stats: UsageStatsEntry[] }) {
  const { t } = useTranslation()

  if (stats.length === 0) {
    return (
      <div className="bg-bg-secondary border border-bg-border rounded-xl p-6">
        <h2 className="text-text-primary font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-accent-green" />
          {t('integrations.usageDashboard')}
        </h2>
        <p className="text-text-muted text-sm">{t('common.noData')}</p>
      </div>
    )
  }

  const maxToday = Math.max(...stats.map((s) => s.today), 1)

  return (
    <div className="bg-bg-secondary border border-bg-border rounded-xl p-6">
      <h2 className="text-text-primary font-semibold mb-5 flex items-center gap-2">
        <Activity className="w-5 h-5 text-accent-green" />
        {t('integrations.usageDashboard')}
      </h2>

      {/* Bar chart */}
      <div className="flex items-end gap-3 h-24 mb-6">
        {stats.map((s) => (
          <div key={s.service} className="flex-1 flex flex-col items-center gap-1">
            <div className="w-full flex items-end justify-center" style={{ height: '72px' }}>
              <div
                className="w-full bg-accent-green/30 rounded-t"
                style={{ height: `${(s.today / maxToday) * 100}%`, minHeight: s.today > 0 ? '4px' : '0' }}
              />
            </div>
            <span className="text-text-muted text-xs truncate w-full text-center">{s.service}</span>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-bg-border">
              <th className="text-left text-text-muted font-normal py-2 pr-4">{t('integrations.service')}</th>
              <th className="text-right text-text-muted font-normal py-2 px-2">{t('integrations.today')}</th>
              <th className="text-right text-text-muted font-normal py-2 px-2">{t('integrations.thisWeek')}</th>
              <th className="text-right text-text-muted font-normal py-2 px-2">{t('integrations.thisMonth')}</th>
              <th className="text-right text-text-muted font-normal py-2 pl-2">{t('integrations.total')}</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((s) => (
              <tr key={s.service} className="border-b border-bg-border/50">
                <td className="py-2 pr-4 text-text-primary font-mono text-xs">{s.service}</td>
                <td className="py-2 px-2 text-right text-text-secondary">{s.today}</td>
                <td className="py-2 px-2 text-right text-text-secondary">{s.this_week}</td>
                <td className="py-2 px-2 text-right text-text-secondary">{s.this_month}</td>
                <td className="py-2 pl-2 text-right text-text-secondary">{s.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ---------- Main Page ----------
export default function IntegrationsPage() {
  const { t } = useTranslation()
  const [available, setAvailable] = useState<ServiceCatalogueEntry[]>([])
  const [userIntegrations, setUserIntegrations] = useState<IntegrationResponse[]>([])
  const [usageStats, setUsageStats] = useState<UsageStatsEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [configuring, setConfiguring] = useState<ServiceCatalogueEntry | null>(null)
  const [filter, setFilter] = useState<string>('all')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [avail, user, usage] = await Promise.all([
        integrationsApi.listAvailable(),
        integrationsApi.list(),
        integrationsApi.getUsage().catch(() => [] as UsageStatsEntry[]),
      ])
      setAvailable(avail)
      setUserIntegrations(user)
      setUsageStats(usage)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleSave = async (entry: ServiceCatalogueEntry, apiKey: string) => {
    const existing = userIntegrations.find((i) => i.service_name === entry.name)
    if (existing) {
      await integrationsApi.update(existing.id, { api_key: apiKey })
    } else {
      await integrationsApi.create(entry.name, apiKey)
    }
    await load()
  }

  const handleToggle = async (entry: ServiceCatalogueEntry) => {
    const existing = userIntegrations.find((i) => i.service_name === entry.name)
    if (!existing) return
    await integrationsApi.update(existing.id, { is_active: !existing.is_active })
    await load()
  }

  const categories = ['all', ...Array.from(new Set(available.map((e) => e.category)))]
  const filtered = filter === 'all' ? available : available.filter((e) => e.category === filter)

  return (
    <div className="p-8 space-y-8 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">{t('nav.integrations')}</h1>
          <p className="text-text-muted text-sm mt-1">{t('integrations.subtitle')}</p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-4 py-2 text-sm border border-bg-border rounded-lg text-text-secondary hover:text-text-primary hover:border-accent-green/30 transition-colors"
        >
          <RefreshCw className={clsx('w-4 h-4', loading && 'animate-spin')} />
          {t('common.loading') && loading ? t('common.loading') : t('integrations.refresh')}
        </button>
      </div>

      {/* Category filter */}
      <div className="flex gap-2 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={clsx(
              'px-4 py-1.5 text-sm rounded-full border transition-colors',
              filter === cat
                ? 'bg-accent-green/20 text-accent-green border-accent-green/40'
                : 'border-bg-border text-text-secondary hover:text-text-primary hover:border-accent-green/30',
            )}
          >
            {cat === 'all' ? t('integrations.all') : (CATEGORY_LABELS[cat] ?? cat)}
          </button>
        ))}
      </div>

      {/* Integration grid */}
      {loading ? (
        <div className="text-text-muted text-sm">{t('common.loading')}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((entry) => {
            const integration = userIntegrations.find((i) => i.service_name === entry.name) ?? null
            return (
              <IntegrationCard
                key={entry.name}
                entry={entry}
                integration={integration}
                onConfigure={() => setConfiguring(entry)}
                onToggle={() => handleToggle(entry)}
              />
            )
          })}
        </div>
      )}

      {/* OSINT Search Panel */}
      <OsintSearchPanel availableServices={available} userIntegrations={userIntegrations} />

      {/* Usage Dashboard */}
      <UsageDashboard stats={usageStats} />

      {/* Configure modal */}
      {configuring && (
        <ConfigureModal
          entry={configuring}
          integration={userIntegrations.find((i) => i.service_name === configuring.name) ?? null}
          onSave={(key) => handleSave(configuring, key)}
          onClose={() => setConfiguring(null)}
        />
      )}
    </div>
  )
}
