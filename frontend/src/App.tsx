import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Suspense } from 'react'
import { useAuthStore } from './store/authStore'
import MainLayout from './components/layout/MainLayout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SearchPage from './pages/SearchPage'
import FilesPage from './pages/FilesPage'
import SettingsPage from './pages/SettingsPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="flex items-center justify-center h-screen text-accent-green">Loading...</div>}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <MainLayout />
              </PrivateRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="files" element={<FilesPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="monitoring" element={<div className="p-8 text-text-secondary">Monitoring — Phase 2</div>} />
            <Route path="integrations" element={<div className="p-8 text-text-secondary">Integrations — Phase 2</div>} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
