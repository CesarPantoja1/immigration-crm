import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import LandingPage from './pages/LandingPage'
import { LoginPage, RegisterPage } from './features/auth'
import { useAuth } from './contexts/AuthContext'

// Layouts
import ClientLayout from './layouts/ClientLayout'
import AdvisorLayout from './layouts/AdvisorLayout'

// Paginas cliente
import { ClientDashboard } from './features/client'
import { NewApplicationPage, ApplicationsListPage, ApplicationDetailPage } from './features/applications'
import { SimulationsPage, MeetingRoomPage, SimulationSummaryPage } from './features/simulations'
import { PracticePage, QuizPage } from './features/practice'

// Paginas asesor
import {
  AdvisorDashboard,
  ApplicationReviewPage,
  DocumentExplorerPage,
  AdvisorSimulationsPage,
  AdvisorMeetingRoomPage
} from './features/advisor'
// Rutas protegidas
function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/" replace />
  }

  return children
}

function App() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegisterPage />} />

        {/* Client Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <ClientDashboard />
            </ClientLayout>
          </ProtectedRoute>
        } />

        <Route path="/nueva-solicitud" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <NewApplicationPage />
            </ClientLayout>
          </ProtectedRoute>
        } />

        <Route path="/solicitudes" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <ApplicationsListPage />
            </ClientLayout>
          </ProtectedRoute>
        } />

        <Route path="/solicitudes/:id" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <ApplicationDetailPage />
            </ClientLayout>
          </ProtectedRoute>
        } />

        <Route path="/simulacros" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <SimulationsPage />
            </ClientLayout>
          </ProtectedRoute>
        } />

        <Route path="/simulacros/:id/room" element={
          <ProtectedRoute allowedRoles={['client']}>
            <MeetingRoomPage />
          </ProtectedRoute>
        } />

        <Route path="/simulacros/:id/resumen" element={
          <ProtectedRoute allowedRoles={['client']}>
            <SimulationSummaryPage />
          </ProtectedRoute>
        } />

        <Route path="/practica" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <PracticePage />
            </ClientLayout>
          </ProtectedRoute>
        } />

        <Route path="/practica/:visaType" element={
          <ProtectedRoute allowedRoles={['client']}>
            <QuizPage />
          </ProtectedRoute>
        } />

        {/* Advisor Routes */}
        <Route path="/asesor" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <AdvisorDashboard />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        <Route path="/asesor/solicitudes" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <ApplicationsListPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        <Route path="/asesor/solicitudes/:id" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <ApplicationReviewPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        <Route path="/asesor/documentos" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <DocumentExplorerPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        <Route path="/asesor/simulacros" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <AdvisorSimulationsPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        <Route path="/asesor/simulacros/:id/room" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <AdvisorMeetingRoomPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

export default App
