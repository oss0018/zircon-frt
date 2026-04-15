import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Home, ArrowLeft } from 'lucide-react'

export default function NotFoundPage() {
  const { t } = useTranslation()
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-6 text-center bg-bg-primary">
      <div className="text-8xl font-black text-accent-cyan/20 select-none">404</div>
      <h1 className="text-2xl font-bold text-text-primary">Page Not Found</h1>
      <p className="text-text-muted max-w-sm">The page you are looking for doesn't exist or has been moved.</p>
      <div className="flex gap-3">
        <Link
          to="/"
          className="flex items-center gap-2 px-4 py-2 bg-accent-cyan text-white rounded-lg text-sm hover:bg-accent-cyan/80"
        >
          <Home className="w-4 h-4" />
          {t('nav.dashboard')}
        </Link>
        <button
          onClick={() => window.history.back()}
          className="flex items-center gap-2 px-4 py-2 bg-bg-card border border-bg-border text-text-primary rounded-lg text-sm hover:border-accent-cyan/50"
        >
          <ArrowLeft className="w-4 h-4" />
          {t('common.back')}
        </button>
      </div>
    </div>
  )
}
