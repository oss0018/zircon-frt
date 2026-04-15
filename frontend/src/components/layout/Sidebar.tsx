import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  LayoutDashboard, Search, Files, Activity, Plug, Shield, Settings, Hexagon,
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, labelKey: 'nav.dashboard' },
  { to: '/search', icon: Search, labelKey: 'nav.search' },
  { to: '/files', icon: Files, labelKey: 'nav.files' },
  { to: '/monitoring', icon: Activity, labelKey: 'nav.monitoring' },
  { to: '/integrations', icon: Plug, labelKey: 'nav.integrations' },
  { to: '/brand-protection', icon: Shield, labelKey: 'nav.brandProtection' },
  { to: '/settings', icon: Settings, labelKey: 'nav.settings' },
]

export default function Sidebar() {
  const { t } = useTranslation()

  return (
    <aside className="w-64 bg-bg-secondary border-r border-bg-border flex flex-col shrink-0">
      {/* Brand */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-bg-border">
        <Hexagon className="w-8 h-8 text-accent-green" strokeWidth={1.5} />
        <div>
          <div className="text-accent-green font-bold text-lg leading-none text-glow-green">Zircon</div>
          <div className="text-text-muted text-xs font-mono">FRT v1.0</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3">
        {navItems.map(({ to, icon: Icon, labelKey }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 text-sm transition-all',
                isActive
                  ? 'bg-accent-green/10 text-accent-green border border-accent-green/20'
                  : 'text-text-secondary hover:text-text-primary hover:bg-white/5',
              )
            }
          >
            <Icon className="w-4 h-4 shrink-0" />
            <span>{t(labelKey)}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-bg-border">
        <div className="text-text-muted text-xs font-mono">OSINT Intelligence Platform</div>
      </div>
    </aside>
  )
}
