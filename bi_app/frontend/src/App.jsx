import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Financier from './pages/Financier'
import Occupation from './pages/Occupation'
import OccupationZoneDetails from './pages/OccupationZoneDetails'
import Clients from './pages/Clients'
import Portefeuille from './pages/Portefeuille'
import Operationnel from './pages/Operationnel'

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Route publique */}
        <Route path="/login" element={<Login />} />
        
        {/* Routes protégées */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="financier" element={<Financier />} />
          <Route path="occupation" element={<Occupation />} />
          <Route path="occupation/zone/:zoneName" element={<OccupationZoneDetails />} />
          <Route path="clients" element={<Clients />} />
          <Route path="portefeuille" element={<Portefeuille />} />
          <Route path="operationnel" element={<Operationnel />} />
        </Route>

        {/* Redirection par défaut */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App