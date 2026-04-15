import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Info, Download } from 'lucide-react'
import SearchBar from '../components/search/SearchBar'
import SearchFiltersPanel from '../components/search/SearchFilters'
import SearchResults from '../components/search/SearchResults'
import { searchApi, type SearchFilters, type SearchHit } from '../api/search'

export default function SearchPage() {
  const { t } = useTranslation()
  const [params, setParams] = useSearchParams()
  const [filters, setFilters] = useState<SearchFilters>({})
  const [hits, setHits] = useState<SearchHit[]>([])
  const [total, setTotal] = useState(0)
  const [took, setTook] = useState(0)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [exporting, setExporting] = useState<string | null>(null)

  const doSearch = async (q: string) => {
    if (!q.trim()) return
    setLoading(true)
    setSearched(true)
    try {
      const res = await searchApi.search({ query: q, filters })
      setHits(res.data.hits)
      setTotal(res.data.total)
      setTook(res.data.took_ms)
    } catch {
      setHits([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const q = params.get('q')
    if (q) doSearch(q)
  }, [])

  const handleSearch = (q: string) => {
    setParams({ q })
    doSearch(q)
  }

  const exportFile = async (fmt: string) => {
    const q = params.get('q') || ''
    if (!q) return
    setExporting(fmt)
    try {
      const token = localStorage.getItem('token') || sessionStorage.getItem('token') || ''
      const url = `/api/v1/export/search?q=${encodeURIComponent(q)}&fmt=${fmt}`
      const resp = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      if (!resp.ok) throw new Error(`Export failed: ${resp.status}`)
      const blob = await resp.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `search_results.${fmt}`
      a.click()
    } catch (err) {
      console.error('Export error:', err)
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <h1 className="text-xl font-bold text-text-primary">{t('search.title')}</h1>

      <SearchBar onSearch={handleSearch} placeholder={t('search.placeholder')} />

      {/* Hints */}
      <div className="flex items-start gap-2 bg-accent-cyan/5 border border-accent-cyan/20 rounded-lg px-4 py-3">
        <Info className="w-4 h-4 text-accent-cyan shrink-0 mt-0.5" />
        <p className="text-xs text-text-muted font-mono">{t('search.hints')}</p>
      </div>

      <div className="flex gap-6">
        {/* Filters sidebar */}
        <div className="w-56 shrink-0">
          <SearchFiltersPanel filters={filters} onChange={setFilters} />
        </div>

        {/* Results */}
        <div className="flex-1 space-y-4">
          {loading ? (
            <div className="text-center py-16 text-text-muted">
              <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              {t('common.loading')}
            </div>
          ) : (
            searched && (
              <>
                {hits.length > 0 && (
                  <div className="flex items-center gap-2 justify-end">
                    <span className="text-text-muted text-xs flex items-center gap-1">
                      <Download className="w-3.5 h-3.5" />
                      {t('export.exportResults')}:
                    </span>
                    {(['csv', 'json', 'pdf'] as const).map((fmt) => (
                      <button
                        key={fmt}
                        onClick={() => exportFile(fmt)}
                        disabled={exporting !== null}
                        className="px-3 py-1 text-xs border border-bg-border text-text-secondary rounded-lg hover:border-accent-cyan/50 hover:text-accent-cyan transition-colors disabled:opacity-50"
                      >
                        {exporting === fmt ? t('export.exporting') : t(`export.export${fmt.charAt(0).toUpperCase() + fmt.slice(1)}`)}
                      </button>
                    ))}
                  </div>
                )}
                <SearchResults hits={hits} total={total} tookMs={took} />
              </>
            )
          )}
        </div>
      </div>
    </div>
  )
}
