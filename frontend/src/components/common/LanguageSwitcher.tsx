import { useTranslation } from 'react-i18next'
import clsx from 'clsx'

const LANGS = [
  { code: 'en', label: 'EN' },
  { code: 'ru', label: 'RU' },
  { code: 'uk', label: 'UK' },
]

export default function LanguageSwitcher() {
  const { i18n } = useTranslation()

  return (
    <div className="flex items-center gap-1 bg-bg-card border border-bg-border rounded-lg p-1">
      {LANGS.map(({ code, label }) => (
        <button
          key={code}
          onClick={() => i18n.changeLanguage(code)}
          className={clsx(
            'px-2 py-1 text-xs rounded font-mono transition-all',
            i18n.language === code
              ? 'bg-accent-green/20 text-accent-green'
              : 'text-text-muted hover:text-text-secondary',
          )}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
