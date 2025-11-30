import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import ProtectedDashboardRoute from './components/ProtectedDashboardRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Financier from './pages/Financier'
import Occupation from './pages/Occupation'
import OccupationZoneDetails from './pages/OccupationZoneDetails'
import Clients from './pages/Clients'
import ClientDetails from './pages/ClientDetails'
import Portefeuille from './pages/Portefeuille'
import Operationnel from './pages/Operationnel'
import ComplianceInfractions from './pages/ComplianceInfractions'
import ComplianceCompliance from './pages/ComplianceCompliance'
import RH from './pages/RH'
import TestMap from './pages/TestMap'
import ChatBot from './components/ChatBot'
import AlertsConfig from './components/AlertsConfig'
import AlertsAnalytics from './pages/AlertsAnalytics'
import ReportConfig from './pages/ReportConfig'
import UserManagement from './pages/UserManagement'

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Route publique */}
        <Route path="/login" element={<Login />} />
        <Route path="/test-map" element={<TestMap />} />
        
        {/* Routes protégées */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="financier" element={
            <ProtectedDashboardRoute dashboard="financier">
              <Financier />
            </ProtectedDashboardRoute>
          } />
          <Route path="occupation" element={
            <ProtectedDashboardRoute dashboard="occupation">
              <Occupation />
            </ProtectedDashboardRoute>
          } />
          <Route path="occupation/zone/:zoneName" element={
            <ProtectedDashboardRoute dashboard="occupation">
              <OccupationZoneDetails />
            </ProtectedDashboardRoute>
          } />
          <Route path="clients" element={<Clients />} />
          <Route path="clients/:entrepriseId" element={<ClientDetails />} />
          <Route path="portefeuille" element={
            <ProtectedDashboardRoute dashboard="portefeuille">
              <Portefeuille />
            </ProtectedDashboardRoute>
          } />
          <Route path="operationnel" element={
            <ProtectedDashboardRoute dashboard="operationnel">
              <Operationnel />
            </ProtectedDashboardRoute>
          } />
          <Route path="compliance" element={
            <ProtectedDashboardRoute dashboard="compliance">
              <ComplianceInfractions />
            </ProtectedDashboardRoute>
          } />
          <Route path="compliance-compliance" element={
            <ProtectedDashboardRoute dashboard="compliance-compliance">
              <ComplianceCompliance />
            </ProtectedDashboardRoute>
          } />
          <Route path="rh" element={
            <ProtectedDashboardRoute dashboard="rh">
              <RH />
            </ProtectedDashboardRoute>
          } />
          <Route path="chatbot" element={
            <ProtectedDashboardRoute dashboard="chatbot">
              <ChatBot />
            </ProtectedDashboardRoute>
          } />
          <Route path="alerts-config" element={<AlertsConfig />} />
          <Route path="alerts-analytics" element={<AlertsAnalytics />} />
          <Route path="report-config" element={<ReportConfig />} />
          <Route path="users" element={<UserManagement />} />
        </Route>

        {/* Redirection par défaut */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App