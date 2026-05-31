import { useCallback, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import InspectionsPage from './pages/InspectionsPage'
import InspectionDetailPage from './pages/InspectionDetailPage'
import TemplatesPage from './pages/TemplatesPage'
import ReportsPage from './pages/ReportsPage'
import AlertsPage from './pages/AlertsPage'
import CameraPage from './pages/CameraPage'
import SettingsPage from './pages/SettingsPage'
import { AlertToastContainer } from './components/AlertToast'
import { useWebSocketAlerts } from './hooks/useWebSocketAlerts'
import { useAlertStore } from './stores/alertStore'
import { useAuthStore } from './services/authStore'

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return children
}

function App() {
  const addRealtimeAlert = useAlertStore((s) => s.addRealtimeAlert)
  const setWsConnected = useAlertStore((s) => s.setWsConnected)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  const handleAlert = useCallback(
    (data) => {
      addRealtimeAlert(data)
    },
    [addRealtimeAlert]
  )

  const { isConnected, toasts, dismissToast } = useWebSocketAlerts({
    onAlert: handleAlert,
    autoConnect: isAuthenticated,
  })

  // Sync connection status to store
  if (useAlertStore.getState().wsConnected !== isConnected) {
    setWsConnected(isConnected)
  }

  return (
    <Router>
      {/* Real-time alert toasts */}
      <AlertToastContainer toasts={toasts} onDismiss={dismissToast} />

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="inspections" element={<InspectionsPage />} />
          <Route path="inspections/:id" element={<InspectionDetailPage />} />
          <Route path="templates" element={<TemplatesPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="camera" element={<CameraPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
