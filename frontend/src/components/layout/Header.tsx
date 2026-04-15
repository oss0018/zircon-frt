import { useTranslation } from 'react-i18next'
import { LogOut, User } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import LanguageSwitcher from '../common/LanguageSwitcher'
import NotificationBell from '../common/NotificationBell'

export default function Header() {
  const { t } = useTranslation()
  const { user, logout } = useAuthStore()

  return (
    <header className="h-14 bg-bg-secondary border-b border-bg-border flex items-center justify-between px-6 shrink-0">
      <div className="text-text-secondary text-sm font-mono">
        {new Date().toLocaleDateString()} — {new Date().toLocaleTimeString()}
      </div>

      <div className="flex items-center gap-4">
        <LanguageSwitcher />

        <NotificationBell />

        <div className="flex items-center gap-2 text-text-secondary">
          <User className="w-4 h-4" />
          <span className="text-sm">{user?.username || 'User'}</span>
        </div>

        <button
          onClick={logout}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-text-secondary hover:text-accent-red transition-colors border border-bg-border rounded-lg hover:border-accent-red/50"
        >
          <LogOut className="w-4 h-4" />
          <span>{t('auth.logout')}</span>
        </button>
      </div>
    </header>
  )
}
