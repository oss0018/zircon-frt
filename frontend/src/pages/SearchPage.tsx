import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Info } from 'lucide-react'
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
        <div className="flex-1">
          {loading ? (
            <div className="text-center py-16 text-text-muted">
              <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              {t('common.loading')}
            </div>
          ) : (
            searched && <SearchResults hits={hits} total={total} tookMs={took} />
          )}
        </div>
      </div>
    </div>
  )
}
