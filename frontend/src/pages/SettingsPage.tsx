import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'
import LanguageSwitcher from '../components/common/LanguageSwitcher'

const INTEGRATION_PLACEHOLDERS = [
  { name: 'Shodan', desc: 'Internet-wide scanning data' },
  { name: 'VirusTotal', desc: 'File and URL analysis' },
  { name: 'Have I Been Pwned', desc: 'Breach data lookup' },
  { name: 'Censys', desc: 'Internet infrastructure data' },
]

export default function SettingsPage() {
  const { t } = useTranslation()
  const { user } = useAuthStore()

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="text-xl font-bold text-text-primary">{t('settings.title')}</h1>

      {/* Profile */}
      <section className="bg-bg-card border border-bg-border rounded-xl p-6 space-y-4">
        <h2 className="text-text-secondary font-semibold">{t('settings.profile')}</h2>
        <div>
          <label className="text-xs text-text-muted block mb-1">{t('settings.email')}</label>
          <input
            type="email"
            defaultValue={user?.email}
            readOnly
            className="w-full bg-bg-secondary border border-bg-border rounded-lg px-4 py-2.5 text-text-primary text-sm opacity-70 cursor-not-allowed"
          />
        </div>
        <div>
          <label className="text-xs text-text-muted block mb-1">{t('settings.username')}</label>
          <input
            type="text"
            defaultValue={user?.username}
            readOnly
            className="w-full bg-bg-secondary border border-bg-border rounded-lg px-4 py-2.5 text-text-primary text-sm opacity-70 cursor-not-allowed"
          />
        </div>
        <div>
          <label className="text-xs text-text-muted block mb-2">{t('settings.language')}</label>
          <LanguageSwitcher />
        </div>
      </section>

      {/* Integrations */}
      <section className="bg-bg-card border border-bg-border rounded-xl p-6 space-y-4">
        <h2 className="text-text-secondary font-semibold">{t('settings.integrations')}</h2>
        <div className="grid grid-cols-2 gap-3">
          {INTEGRATION_PLACEHOLDERS.map((intg) => (
            <div key={intg.name} className="border border-bg-border rounded-lg p-3 opacity-50">
              <div className="text-sm font-medium text-text-primary">{intg.name}</div>
              <div className="text-xs text-text-muted">{intg.desc}</div>
              <div className="text-xs text-accent-cyan mt-1">Phase 2</div>
            </div>
          ))}
        </div>
      </section>

      {/* Notifications */}
      <section className="bg-bg-card border border-bg-border rounded-xl p-6 space-y-4">
        <h2 className="text-text-secondary font-semibold">{t('settings.notifications')}</h2>
        <label className="flex items-center gap-3 cursor-pointer">
          <div className="w-10 h-5 bg-bg-secondary border border-bg-border rounded-full relative">
            <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-text-muted rounded-full transition-all" />
          </div>
          <span className="text-sm text-text-secondary">{t('settings.emailNotifications')}</span>
        </label>
        <label className="flex items-center gap-3 cursor-pointer">
          <div className="w-10 h-5 bg-bg-secondary border border-bg-border rounded-full relative">
            <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-text-muted rounded-full transition-all" />
          </div>
          <span className="text-sm text-text-secondary">{t('settings.telegramNotifications')}</span>
        </label>
      </section>
    </div>
  )
}
