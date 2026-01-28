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
import { SimulationsPage, MeetingRoomPage, SimulationSummaryPage, PresentialInfoPage } from './features/simulations'
import { PracticePage, QuizPage } from './features/practice'

// Nuevas páginas cliente
import { InboxPage } from './features/inbox'
import { CalendarPage } from './features/calendar'

// Paginas asesor
import {
  AdvisorDashboard,
  AdvisorApplicationsListPage,
  ApplicationReviewPage,
  DocumentExplorerPage,
  AdvisorSimulationsPage,
  AdvisorMeetingRoomPage,
  InterviewScheduling,
  AdvisorInboxPage,
  IAConfigPage
} from './features/advisor'

// Pagina admin
import { AdminDashboard } from './features/admin'

// Pagina asesor - Presencial Feedback
import { PresentialFeedbackPage } from './features/simulations'
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

        {/* Client Inbox (Centro de Notificaciones) */}
        <Route path="/inbox" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <InboxPage />
            </ClientLayout>
          </ProtectedRoute>
        } />

        {/* Client Calendar (Calendario Maestro) */}
        <Route path="/calendario" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <CalendarPage />
            </ClientLayout>
          </ProtectedRoute>
        } />

        {/* Client Presential Simulation Info */}
        <Route path="/simulacros/:id/presencial" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientLayout>
              <PresentialInfoPage />
            </ClientLayout>
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
              <AdvisorApplicationsListPage />
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

        <Route path="/asesor/entrevistas" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <InterviewScheduling />
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

        {/* Advisor Presential Feedback */}
        <Route path="/asesor/simulacros/:id/presencial" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <PresentialFeedbackPage />
          </ProtectedRoute>
        } />

        {/* Advisor Inbox (Centro de Notificaciones) */}
        <Route path="/asesor/inbox" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <AdvisorInboxPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        {/* Advisor IA Config (Configuración de IA) */}
        <Route path="/asesor/configuracion-ia" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <IAConfigPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        {/* Advisor Calendar (Calendario Maestro) */}
        <Route path="/asesor/calendario" element={
          <ProtectedRoute allowedRoles={['advisor']}>
            <AdvisorLayout>
              <CalendarPage />
            </AdvisorLayout>
          </ProtectedRoute>
        } />

        {/* Admin Routes */}
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        } />

        <Route path="/admin/*" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        } />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

export default App
