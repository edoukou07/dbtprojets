import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { AlertCircle } from 'lucide-react'

/**
 * Composant pour protéger les routes des tableaux de bord
 * Vérifie que l'utilisateur a accès au tableau spécifique
 */
export default function ProtectedDashboardRoute({ children, dashboard }) {
  const { user } = useAuth()

  // Si l'utilisateur n'a pas de permissions, il peut accéder à tous les tableaux
  // (comportement pour compatibilité avec les utilisateurs existants)
  if (!user?.dashboards || user.dashboards.length === 0) {
    return children
  }

  // Vérifier si le tableau est dans les permissions de l'utilisateur
  const hasAccess = user.dashboards.includes(dashboard)

  if (!hasAccess) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-6 max-w-md">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
            <div>
              <h2 className="text-lg font-semibold text-red-400">Accès Refusé</h2>
              <p className="text-red-300/80 text-sm mt-1">
                Vous n'avez pas accès à ce tableau de bord. Contactez un administrateur.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return children
}
