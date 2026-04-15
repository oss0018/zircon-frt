import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Hexagon, Eye, EyeOff } from 'lucide-react'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import LanguageSwitcher from '../components/common/LanguageSwitcher'

export default function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let tokens
      if (mode === 'login') {
        const res = await authApi.login({ email, password })
        tokens = res.data
      } else {
        const res = await authApi.register({ email, username, password })
        tokens = res.data
      }
      setTokens(tokens.access_token, tokens.refresh_token)
      const userRes = await authApi.me()
      setUser(userRes.data)
      navigate('/dashboard')
    } catch {
      setError(t('auth.invalidCredentials'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary grid-pattern flex flex-col items-center justify-center p-4">
      <div className="absolute top-4 right-4">
        <LanguageSwitcher />
      </div>

      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-accent-green/10 rounded-2xl border border-accent-green/20 glow-green">
              <Hexagon className="w-12 h-12 text-accent-green" strokeWidth={1} />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-accent-green text-glow-green">Zircon FRT</h1>
          <p className="text-text-muted text-sm mt-1 font-mono">{t('auth.loginSubtitle')}</p>
        </div>

        {/* Card */}
        <div className="bg-bg-secondary border border-bg-border rounded-2xl p-8">
          <h2 className="text-text-primary font-semibold text-lg mb-6">
            {mode === 'login' ? t('auth.loginTitle') : t('auth.registerTitle')}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-xs text-text-muted block mb-1.5">{t('auth.email')}</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-bg-card border border-bg-border rounded-lg px-4 py-3 text-text-primary text-sm focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30 transition-all"
              />
            </div>

            {mode === 'register' && (
              <div>
                <label className="text-xs text-text-muted block mb-1.5">{t('auth.username')}</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full bg-bg-card border border-bg-border rounded-lg px-4 py-3 text-text-primary text-sm focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30 transition-all"
                />
              </div>
            )}

            <div>
              <label className="text-xs text-text-muted block mb-1.5">{t('auth.password')}</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full bg-bg-card border border-bg-border rounded-lg px-4 py-3 pr-10 text-text-primary text-sm focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-accent-red/10 border border-accent-red/30 rounded-lg px-4 py-3 text-accent-red text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-accent-green text-bg-primary font-semibold rounded-lg hover:bg-accent-green/90 transition-all glow-green disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? t('common.loading') : mode === 'login' ? t('auth.login') : t('auth.register')}
            </button>
          </form>

          <div className="mt-4 text-center text-sm text-text-muted">
            {mode === 'login' ? (
              <>
                {t('auth.noAccount')}{' '}
                <button onClick={() => setMode('register')} className="text-accent-cyan hover:underline">
                  {t('auth.register')}
                </button>
              </>
            ) : (
              <>
                {t('auth.alreadyHaveAccount')}{' '}
                <button onClick={() => setMode('login')} className="text-accent-cyan hover:underline">
                  {t('auth.login')}
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
