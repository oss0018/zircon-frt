import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Files, Database, Bell, Activity, Upload, Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'
import SearchBar from '../components/search/SearchBar'

interface Stats {
  total_files: number
  indexed_files: number
  alerts_today: number
  active_monitors: number
}

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: number; color: string }) {
  return (
    <div className="bg-bg-card border border-bg-border rounded-xl p-5 hover:border-opacity-50 transition-all">
      <div className="flex items-center gap-3 mb-3">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <span className="text-text-muted text-sm">{label}</span>
      </div>
      <div className="text-3xl font-bold text-text-primary font-mono">{value.toLocaleString()}</div>
    </div>
  )
}

export default function DashboardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    apiClient.get<Stats>('/dashboard/stats').then((r) => setStats(r.data)).catch(() => {})
  }, [])

  const handleSearch = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Hero search */}
      <div className="text-center pt-4">
        <h1 className="text-2xl font-bold text-text-primary mb-2">{t('dashboard.title')}</h1>
        <p className="text-text-muted text-sm mb-6 font-mono">OSINT Intelligence Platform</p>
        <SearchBar onSearch={handleSearch} placeholder={t('dashboard.searchPlaceholder')} className="max-w-2xl mx-auto" />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Files} label={t('dashboard.totalFiles')} value={stats?.total_files ?? 0} color="bg-accent-cyan/10 text-accent-cyan" />
        <StatCard icon={Database} label={t('dashboard.indexedFiles')} value={stats?.indexed_files ?? 0} color="bg-accent-green/10 text-accent-green" />
        <StatCard icon={Bell} label={t('dashboard.alertsToday')} value={stats?.alerts_today ?? 0} color="bg-accent-red/10 text-accent-red" />
        <StatCard icon={Activity} label={t('dashboard.activeMonitors')} value={stats?.active_monitors ?? 0} color="bg-accent-purple/10 text-accent-purple" />
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-text-secondary text-sm font-semibold uppercase tracking-wider mb-3">{t('dashboard.quickActions')}</h2>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/files')}
            className="flex items-center gap-2 px-4 py-2.5 bg-accent-green/10 border border-accent-green/30 text-accent-green rounded-lg hover:bg-accent-green/20 transition-all text-sm"
          >
            <Upload className="w-4 h-4" />
            {t('dashboard.uploadFiles')}
          </button>
          <button
            onClick={() => navigate('/monitoring')}
            className="flex items-center gap-2 px-4 py-2.5 bg-accent-cyan/10 border border-accent-cyan/30 text-accent-cyan rounded-lg hover:bg-accent-cyan/20 transition-all text-sm"
          >
            <Plus className="w-4 h-4" />
            {t('dashboard.newMonitor')}
          </button>
        </div>
      </div>

      {/* Recent activity placeholder */}
      <div>
        <h2 className="text-text-secondary text-sm font-semibold uppercase tracking-wider mb-3">{t('dashboard.recentActivity')}</h2>
        <div className="bg-bg-card border border-bg-border rounded-xl p-6">
          <p className="text-text-muted text-sm text-center font-mono">No recent activity</p>
        </div>
      </div>
    </div>
  )
}
