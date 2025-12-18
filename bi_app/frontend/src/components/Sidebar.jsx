import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  DollarSign, 
  Building2, 
  Users, 
  Activity, 
  LogOut, 
  User,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Bot,
  Shield,
  UserCog,
  Clock
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

export default function Sidebar() {
  const location = useLocation()
  const { user, logout } = useAuth()
  const [isCollapsed, setIsCollapsed] = useState(false)
  
  // Tous les tableaux de bord disponibles avec leur ID correspondant
  const allDashboards = [
    { name: 'Tableau de bord', path: '/dashboard', icon: LayoutDashboard, id: null },
    { name: 'Performance Financière', path: '/financier', icon: DollarSign, id: 'financier' },
    { name: 'Occupation Zones', path: '/occupation', icon: Building2, id: 'occupation' },
    { name: 'Portefeuille Clients', path: '/portefeuille', icon: Users, id: 'portefeuille' },
    { name: 'KPI Opérationnels', path: '/operationnel', icon: Activity, id: 'operationnel' },
    { name: 'Ressources Humaines', path: '/rh', icon: UserCog, id: 'rh' },
    { name: 'Temps & Goulots', path: '/temps-traitement', icon: Clock, id: 'rh' },
    { name: 'Conformité & Infractions', path: '/compliance', icon: Shield, id: 'compliance' },
    { name: 'Tableau de Conformité', path: '/compliance-compliance', icon: Shield, id: 'compliance-compliance' },
    { name: 'Assistant IA', path: '/chatbot', icon: Bot, id: 'chatbot' },
  ]

  // Filtrer les tableaux selon les permissions de l'utilisateur
  const getFilteredDashboards = () => {
    console.log('User dashboards:', user?.dashboards) // DEBUG
    
    // Par défaut: si pas de permissions assignées (null ou vide), afficher TOUS les tableaux
    // L'admin peut restreindre en sélectionnant spécifiquement des dashboards
    if (!user?.dashboards || user.dashboards.length === 0) {
      return allDashboards
    }
    
    // Si des permissions sont assignées, afficher SEULEMENT celles autorisées
    return allDashboards.filter(dashboard => {
      // Toujours afficher dashboard et chatbot (pas de permission requise)
      if (dashboard.id === null) return true
      // Sinon, vérifier si dans les permissions
      return user.dashboards.includes(dashboard.id)
    })
  }

  const commonNavigation = getFilteredDashboards()

  const adminNavigation = [
    { name: 'Config. Rapports', path: '/report-config', icon: LayoutDashboard },
    { name: 'Gestion Utilisateurs', path: '/users', icon: Shield },
  ]

  // Afficher les menus d'admin seulement pour admin SIGETI
  const navigation = user?.is_staff && user?.username === 'admin' 
    ? [...commonNavigation, ...adminNavigation]
    : commonNavigation
  
  const isActive = (path) => location.pathname === path

  return (
    <aside
      className={`
        fixed left-0 top-0 h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900
        border-r border-gray-700 transition-all duration-300 ease-in-out z-40
        ${isCollapsed ? 'w-20' : 'w-72'}
      `}
    >
      {/* Logo Section */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-gray-700">
        <div className={`flex items-center space-x-3 ${isCollapsed ? 'justify-center w-full' : ''}`}>
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-xl">S</span>
          </div>
          {!isCollapsed && (
            <div>
              <h1 className="text-white font-bold text-lg">SIGETI BI</h1>
              <p className="text-gray-400 text-xs">Business Intelligence</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                ${active 
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' 
                  : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'
                }
                ${isCollapsed ? 'justify-center' : ''}
              `}
              title={isCollapsed ? item.name : ''}
            >
              <Icon className={`${isCollapsed ? 'w-6 h-6' : 'w-5 h-5'} flex-shrink-0`} />
              {!isCollapsed && (
                <span className="font-medium text-sm">{item.name}</span>
              )}
              {!isCollapsed && active && (
                <div className="ml-auto w-2 h-2 bg-white rounded-full"></div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-gray-700">
        <div className={`p-4 ${isCollapsed ? 'px-2' : ''}`}>
          {!isCollapsed ? (
            <div className="bg-gray-800/50 rounded-lg p-3 mb-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">
                    {user?.first_name} {user?.last_name}
                  </p>
                  <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex justify-center mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
          )}

          <button
            onClick={logout}
            className={`
              w-full flex items-center space-x-3 px-4 py-3 rounded-lg
              text-red-400 hover:bg-red-500/10 hover:text-red-300
              transition-colors duration-200
              ${isCollapsed ? 'justify-center' : ''}
            `}
            title="Se déconnecter"
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && <span className="font-medium text-sm">Déconnexion</span>}
          </button>
        </div>

        {/* Collapse Toggle */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full h-12 flex items-center justify-center border-t border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800/50 transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>
    </aside>
  )
}
