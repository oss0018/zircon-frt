import { useState, type FormEvent } from 'react'
import { Search } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import clsx from 'clsx'

interface Props {
  onSearch: (query: string) => void
  placeholder?: string
  className?: string
  autoFocus?: boolean
}

export default function SearchBar({ onSearch, placeholder, className, autoFocus }: Props) {
  const { t } = useTranslation()
  const [query, setQuery] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (query.trim()) onSearch(query.trim())
  }

  return (
    <form onSubmit={handleSubmit} className={clsx('relative', className)}>
      <div className="relative flex items-center">
        <Search className="absolute left-4 w-5 h-5 text-text-muted pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder || t('search.placeholder')}
          autoFocus={autoFocus}
          className="w-full bg-bg-card border border-bg-border rounded-xl pl-12 pr-32 py-3.5 text-text-primary placeholder-text-muted focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30 transition-all font-mono text-sm"
        />
        <button
          type="submit"
          className="absolute right-2 px-4 py-1.5 bg-accent-green text-bg-primary text-sm font-semibold rounded-lg hover:bg-accent-green/90 transition-all glow-green"
        >
          {t('search.search')}
        </button>
      </div>
    </form>
  )
}
