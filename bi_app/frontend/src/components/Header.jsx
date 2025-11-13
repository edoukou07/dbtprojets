import { useLocation } from 'react-router-dom'
import { Bell, Search, Settings } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Header() {
  const location = useLocation()
  const { user } = useAuth()

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

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Page Title */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{currentTitle}</h1>
            {currentDescription && (
              <p className="text-sm text-gray-500 mt-1">{currentDescription}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            {/* Search */}
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>

            {/* Notifications */}
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg relative transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Settings */}
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Settings className="w-5 h-5" />
            </button>

            {/* User Badge */}
            <div className="ml-3 pl-3 border-l border-gray-200">
              <div className="flex items-center space-x-2">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.first_name} {user?.last_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.is_staff ? 'Administrateur' : 'Utilisateur'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
