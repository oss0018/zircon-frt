import { useEffect, useRef, useState } from 'react'
import { Bell, Check, CheckCheck, Trash2, AlertTriangle, Info, Shield, ShieldAlert } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { notificationsApi, type Notification } from '../../api/notifications'
import { useAuthStore } from '../../store/authStore'
import clsx from 'clsx'

const TYPE_ICON: Record<string, React.FC<{ className?: string }>> = {
  info: Info,
  warning: AlertTriangle,
  alert: AlertTriangle,
  breach: ShieldAlert,
  phishing: ShieldAlert,
  brand: Shield,
}

const TYPE_COLOR: Record<string, string> = {
  info: 'text-accent-cyan',
  warning: 'text-yellow-400',
  alert: 'text-accent-red',
  breach: 'text-accent-red',
  phishing: 'text-orange-400',
  brand: 'text-accent-green',
}

function timeAgo(dateStr: string): string {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000
  if (diff < 60) return `${Math.floor(diff)}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost/ws'

export default function NotificationBell() {
  const { t } = useTranslation()
  const { accessToken } = useAuthStore()
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unread, setUnread] = useState(0)
  const [loading, setLoading] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const fetchNotifications = async () => {
    try {
      const [listRes, countRes] = await Promise.all([
        notificationsApi.list({ limit: 20 }),
        notificationsApi.unreadCount(),
      ])
      setNotifications(listRes.data)
      setUnread(countRes.data.count)
    } catch {
      // silently ignore
    }
  }

  useEffect(() => {
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
  }, [])

  // WebSocket for real-time push
  useEffect(() => {
    if (!accessToken) return
    let ws: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout>

    const connect = () => {
      try {
        ws = new WebSocket(`${WS_BASE}/notifications?token=${accessToken}`)
        ws.onmessage = (e) => {
          try {
            const notif: Notification = JSON.parse(e.data)
            setNotifications((prev) => [notif, ...prev.slice(0, 49)])
            setUnread((prev) => prev + 1)
          } catch {
            // ignore parse errors
          }
        }
        ws.onclose = () => {
          reconnectTimer = setTimeout(connect, 5000)
        }
      } catch {
        reconnectTimer = setTimeout(connect, 5000)
      }
    }

    connect()
    return () => {
      ws?.close()
      clearTimeout(reconnectTimer)
    }
  }, [accessToken])

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    if (open) document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  const handleMarkRead = async (id: number) => {
    await notificationsApi.markRead(id)
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)))
    setUnread((prev) => Math.max(0, prev - 1))
  }

  const handleMarkAllRead = async () => {
    setLoading(true)
    await notificationsApi.markAllRead()
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    setUnread(0)
    setLoading(false)
  }

  const handleDelete = async (id: number, isRead: boolean) => {
    await notificationsApi.delete(id)
    setNotifications((prev) => prev.filter((n) => n.id !== id))
    if (!isRead) setUnread((prev) => Math.max(0, prev - 1))
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="relative p-2 text-text-secondary hover:text-accent-cyan transition-colors"
        aria-label={t('notifications.title')}
      >
        <Bell className="w-5 h-5" />
        {unread > 0 && (
          <span className="absolute top-1 right-1 min-w-[16px] h-4 bg-accent-red text-white text-[10px] font-bold rounded-full flex items-center justify-center px-0.5">
            {unread > 99 ? '99+' : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-96 bg-bg-secondary border border-bg-border rounded-xl shadow-2xl z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-bg-border">
            <span className="text-text-primary font-semibold text-sm">{t('notifications.title')}</span>
            {unread > 0 && (
              <button
                onClick={handleMarkAllRead}
                disabled={loading}
                className="flex items-center gap-1.5 text-xs text-accent-cyan hover:text-accent-cyan/80 transition-colors"
              >
                <CheckCheck className="w-3.5 h-3.5" />
                {t('notifications.markAllRead')}
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="py-8 text-center text-text-muted text-sm">
                {t('notifications.empty')}
              </div>
            ) : (
              notifications.map((n) => {
                const Icon = TYPE_ICON[n.type] || Info
                const color = TYPE_COLOR[n.type] || 'text-text-secondary'
                return (
                  <div
                    key={n.id}
                    className={clsx(
                      'flex items-start gap-3 px-4 py-3 border-b border-bg-border/50 hover:bg-white/5 transition-colors',
                      !n.is_read && 'bg-accent-cyan/5',
                    )}
                  >
                    <Icon className={clsx('w-4 h-4 mt-0.5 shrink-0', color)} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-text-primary text-sm font-medium truncate">{n.title}</span>
                        <span className="text-text-muted text-xs shrink-0">{timeAgo(n.created_at)}</span>
                      </div>
                      {n.message && (
                        <p className="text-text-secondary text-xs mt-0.5 line-clamp-2">{n.message}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      {!n.is_read && (
                        <button
                          onClick={() => handleMarkRead(n.id)}
                          className="p-1 text-text-muted hover:text-accent-cyan transition-colors"
                          title={t('notifications.markRead')}
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(n.id, n.is_read)}
                        className="p-1 text-text-muted hover:text-accent-red transition-colors"
                        title={t('common.delete')}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}
