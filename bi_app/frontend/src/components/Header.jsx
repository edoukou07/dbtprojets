import { useLocation, useNavigate } from 'react-router-dom'
import { Bell, Search, Settings, RefreshCw, Activity, LogOut } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import ThemeToggle from './ThemeToggle'
import { useState } from 'react'

export default function Header() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [refreshing, setRefreshing] = useState(false)

  // Mapping des routes vers les titres
  const pageTitles = {
    '/dashboard': 'Tableau de bord',
    '/financier': 'Performance Financière',
    '/occupation': 'Occupation des Zones',
    '/clients': 'Portefeuille Clients',
    '/portefeuille': 'Portefeuille Clients',
    '/operationnel': 'KPI Opérationnels',
  }

  const pageDescriptions = {
    '/dashboard': 'Vue d\'ensemble de tous vos indicateurs clés',
    '/financier': 'Analyse des revenus, factures et paiements',
    '/occupation': 'Taux d\'occupation et disponibilité des lots',
    '/clients': 'Analyse du portefeuille et segmentation client',
    '/portefeuille': 'Analyse du portefeuille et segmentation client',
    '/operationnel': 'Indicateurs de performance opérationnelle',
  }

  const currentTitle = pageTitles[location.pathname] || 'SIGETI BI'
  const currentDescription = pageDescriptions[location.pathname] || ''

  const handleRefreshData = async () => {
    setRefreshing(true)
    try {
      // Recharger la page actuelle
      window.location.reload()
    } catch (error) {
      console.error('Erreur lors du rafraîchissement:', error)
    } finally {
      setTimeout(() => setRefreshing(false), 1000)
    }
  }

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30 shadow-sm transition-colors">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Page Title */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{currentTitle}</h1>
            {currentDescription && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{currentDescription}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            {/* Refresh Button */}
            <button 
              onClick={handleRefreshData}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
              title="Rafraîchir les données"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline text-sm font-medium">Rafraîchir</span>
            </button>

            {/* Search */}
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
              <input
                type="text"
                placeholder="Rechercher..."
                className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
              />
            </div>

            {/* Notifications */}
            <button className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg relative transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Settings - Navigation vers configuration des alertes */}
            <button 
              onClick={() => navigate('/alerts-config')}
              className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="Configuration des alertes"
            >
              <Settings className="w-5 h-5" />
            </button>
            
            {/* Analytics - Navigation vers analytics des alertes */}
            <button 
              onClick={() => navigate('/alerts-analytics')}
              className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="Analytics des alertes"
            >
              <Activity className="w-5 h-5" />
            </button>

            {/* User Badge */}
            <div className="ml-3 pl-3 border-l border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user?.first_name} {user?.last_name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user?.is_staff ? 'Administrateur' : 'Utilisateur'}
                  </p>
                </div>
                {/* Logout Button */}
                <button 
                  onClick={() => {
                    logout()
                    navigate('/login')
                  }}
                  className="p-2 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  title="Se déconnecter"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
