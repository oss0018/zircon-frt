import { useTranslation } from 'react-i18next'
import { FileText, Clock } from 'lucide-react'
import type { SearchHit } from '../../api/search'

interface Props {
  hits: SearchHit[]
  total: number
  tookMs: number
}

export default function SearchResults({ hits, total, tookMs }: Props) {
  const { t } = useTranslation()

  if (hits.length === 0) {
    return (
      <div className="text-center py-16 text-text-muted">
        <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p>{t('search.noResults')}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="text-xs text-text-muted mb-4 font-mono">
        {total} {t('search.results')} — {tookMs}ms
      </div>
      <div className="space-y-3">
        {hits.map((hit) => (
          <div
            key={hit.file_id}
            className="bg-bg-card border border-bg-border rounded-xl p-4 hover:border-accent-cyan/40 transition-all"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-accent-cyan shrink-0" />
                <span className="text-text-primary font-medium text-sm">{hit.filename}</span>
                {hit.file_type && (
                  <span className="px-2 py-0.5 bg-accent-cyan/10 text-accent-cyan text-xs rounded font-mono">
                    {hit.file_type}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 text-xs text-text-muted shrink-0 ml-4">
                <span className="text-accent-green font-mono">{(hit.score * 100).toFixed(0)}%</span>
                {hit.created_at && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(hit.created_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
            {hit.highlights.length > 0 && (
              <div className="space-y-1">
                {hit.highlights.map((h, i) => (
                  <p
                    key={i}
                    className="text-xs text-text-secondary font-mono leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: `...${h}...` }}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
