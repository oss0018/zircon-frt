import { useTranslation } from 'react-i18next'
import type { SearchFilters } from '../../api/search'

interface Props {
  filters: SearchFilters
  onChange: (f: SearchFilters) => void
}

export default function SearchFiltersPanel({ filters, onChange }: Props) {
  const { t } = useTranslation()

  return (
    <div className="bg-bg-card border border-bg-border rounded-xl p-4 space-y-4">
      <h3 className="text-text-secondary text-sm font-semibold uppercase tracking-wider">{t('search.filters')}</h3>

      <div>
        <label className="text-xs text-text-muted block mb-1">{t('search.fileType')}</label>
        <select
          value={filters.file_type || ''}
          onChange={(e) => onChange({ ...filters, file_type: e.target.value || undefined })}
          className="w-full bg-bg-secondary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
        >
          <option value="">All types</option>
          <option value="text/plain">TXT</option>
          <option value="text/csv">CSV</option>
          <option value="application/json">JSON</option>
          <option value="application/sql">SQL</option>
        </select>
      </div>

      <div>
        <label className="text-xs text-text-muted block mb-1">{t('search.dateFrom')}</label>
        <input
          type="date"
          value={filters.date_from || ''}
          onChange={(e) => onChange({ ...filters, date_from: e.target.value || undefined })}
          className="w-full bg-bg-secondary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
        />
      </div>

      <div>
        <label className="text-xs text-text-muted block mb-1">{t('search.dateTo')}</label>
        <input
          type="date"
          value={filters.date_to || ''}
          onChange={(e) => onChange({ ...filters, date_to: e.target.value || undefined })}
          className="w-full bg-bg-secondary border border-bg-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
        />
      </div>

      <button
        onClick={() => onChange({})}
        className="w-full py-2 text-xs text-text-muted hover:text-accent-red border border-bg-border rounded-lg transition-colors"
      >
        Clear Filters
      </button>
    </div>
  )
}
