import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle, X, Bell, BellOff, AlertCircle, Info } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default function AlertsPanel({ showOnlyActive = false, maxAlerts = 5 }) {
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [alertsEnabled, setAlertsEnabled] = useState(() => {
    return localStorage.getItem('alerts_enabled') !== 'false'
  })
  const queryClient = useQueryClient()

  const toggleAlerts = () => {
    const newState = !alertsEnabled
    setAlertsEnabled(newState)
    localStorage.setItem('alerts_enabled', newState.toString())
  }

  // Fetch alerts
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', showOnlyActive],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const endpoint = showOnlyActive ? `${API_URL}/alerts/active/` : `${API_URL}/alerts/`
      const response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    },
    staleTime: 30 * 1000, // Rafraîchir toutes les 30 secondes
    enabled: alertsEnabled, // N'exécute la requête que si les alertes sont activées
  })

  // Acknowledge mutation
  const acknowledgeMutation = useMutation({
    mutationFn: async (alertId) => {
      const token = localStorage.getItem('access_token')
      const response = await axios.post(
        `${API_URL}/alerts/${alertId}/acknowledge/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['alerts'])
    },
  })

  // Resolve mutation
  const resolveMutation = useMutation({
    mutationFn: async (alertId) => {
      const token = localStorage.getItem('access_token')
      const response = await axios.post(
        `${API_URL}/alerts/${alertId}/resolve/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['alerts'])
      setSelectedAlert(null)
    },
  })

  const getSeverityConfig = (severity) => {
    const configs = {
      critical: {
        icon: AlertTriangle,
        color: 'red',
        bg: 'bg-red-50',
        border: 'border-red-200',
        text: 'text-red-800',
        badge: 'bg-red-100 text-red-800'
      },
      high: {
        icon: AlertCircle,
        color: 'orange',
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        text: 'text-orange-800',
        badge: 'bg-orange-100 text-orange-800'
      },
      medium: {
        icon: Info,
        color: 'yellow',
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        text: 'text-yellow-800',
        badge: 'bg-yellow-100 text-yellow-800'
      },
      low: {
        icon: Info,
        color: 'blue',
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        text: 'text-blue-800',
        badge: 'bg-blue-100 text-blue-800'
      }
    }
    return configs[severity] || configs.low
  }

  const getStatusBadge = (status) => {
    const badges = {
      active: { label: 'Active', class: 'bg-red-100 text-red-800' },
      acknowledged: { label: 'Acquittée', class: 'bg-yellow-100 text-yellow-800' },
      resolved: { label: 'Résolue', class: 'bg-green-100 text-green-800' },
      dismissed: { label: 'Ignorée', class: 'bg-gray-100 text-gray-800' },
    }
    return badges[status] || badges.active
  }

  const displayAlerts = alerts?.slice(0, maxAlerts) || []

  // Si les alertes sont désactivées
  if (!alertsEnabled) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <BellOff className="w-5 h-5 text-gray-400" />
            <h3 className="font-semibold text-gray-900">Alertes</h3>
          </div>
          <button
            onClick={toggleAlerts}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Bell className="w-4 h-4" />
            <span className="text-sm font-medium">Activer les alertes</span>
          </button>
        </div>
        <div className="text-center py-4">
          <p className="text-gray-600">Les alertes sont désactivées</p>
          <p className="text-sm text-gray-500 mt-1">Activez-les pour surveiller les indicateurs critiques</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-gray-600">Chargement des alertes...</span>
        </div>
      </div>
    )
  }

  if (!displayAlerts || displayAlerts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-gray-900">Alertes</h3>
          </div>
          <button
            onClick={toggleAlerts}
            className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Désactiver les alertes"
          >
            <BellOff className="w-4 h-4" />
            <span>Désactiver</span>
          </button>
        </div>
        <div className="p-6 text-center">
          <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-2" />
          <p className="text-gray-600 font-medium">Aucune alerte active</p>
          <p className="text-sm text-gray-500 mt-1">Tous les indicateurs sont dans les normes</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bell className="w-5 h-5 text-red-600" />
          <h3 className="font-semibold text-gray-900">Alertes</h3>
          <span className="px-2 py-0.5 bg-red-100 text-red-800 text-xs font-medium rounded-full">
            {alerts?.filter(a => a.status === 'active').length || 0}
          </span>
        </div>
        <button
          onClick={toggleAlerts}
          className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          title="Désactiver les alertes"
        >
          <BellOff className="w-4 h-4" />
          <span>Désactiver</span>
        </button>
      </div>

      {/* Alerts List */}
      <div className="divide-y divide-gray-200">
        {displayAlerts.map((alert) => {
          const config = getSeverityConfig(alert.severity)
          const Icon = config.icon
          const statusBadge = getStatusBadge(alert.status)

          return (
            <div
              key={alert.id}
              className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer ${config.bg} border-l-4 ${config.border}`}
              onClick={() => setSelectedAlert(alert)}
            >
              <div className="flex items-start space-x-3">
                <Icon className={`w-5 h-5 mt-0.5 text-${config.color}-600 flex-shrink-0`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 text-sm">{alert.title}</p>
                      <p className="text-xs text-gray-600 mt-1 line-clamp-2">{alert.message}</p>
                    </div>
                    <span className={`ml-2 px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap ${statusBadge.class}`}>
                      {statusBadge.label}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-3 mt-2">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${config.badge}`}>
                      {alert.severity_display}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(alert.created_at).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>

                  {/* Quick Actions */}
                  {alert.status === 'active' && (
                    <div className="flex space-x-2 mt-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          acknowledgeMutation.mutate(alert.id)
                        }}
                        className="text-xs px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                      >
                        Acquitter
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          resolveMutation.mutate(alert.id)
                        }}
                        className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                      >
                        Résoudre
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Footer */}
      {alerts && alerts.length > maxAlerts && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 text-center">
          <span className="text-sm text-gray-600">
            +{alerts.length - maxAlerts} autre{alerts.length - maxAlerts > 1 ? 's' : ''} alerte{alerts.length - maxAlerts > 1 ? 's' : ''}
          </span>
        </div>
      )}

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setSelectedAlert(null)}
          ></div>
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-2xl">
                {/* Modal Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900">Détails de l'Alerte</h2>
                  <button
                    onClick={() => setSelectedAlert(null)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                {/* Modal Content */}
                <div className="px-6 py-4">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Type</label>
                      <p className="text-gray-900">{selectedAlert.alert_type_display}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-600">Titre</label>
                      <p className="text-gray-900 font-medium">{selectedAlert.title}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-600">Message</label>
                      <p className="text-gray-900">{selectedAlert.message}</p>
                    </div>

                    {selectedAlert.threshold_value && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-600">Seuil</label>
                          <p className="text-gray-900">{selectedAlert.threshold_value}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-600">Valeur Actuelle</label>
                          <p className="text-gray-900">{selectedAlert.actual_value}</p>
                        </div>
                      </div>
                    )}

                    {selectedAlert.context_data && (
                      <div>
                        <label className="text-sm font-medium text-gray-600">Contexte</label>
                        <pre className="mt-1 p-3 bg-gray-50 rounded text-xs overflow-auto">
                          {JSON.stringify(selectedAlert.context_data, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>

                {/* Modal Footer */}
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
                  <button
                    onClick={() => setSelectedAlert(null)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100"
                  >
                    Fermer
                  </button>
                  {selectedAlert.status === 'active' && (
                    <>
                      <button
                        onClick={() => acknowledgeMutation.mutate(selectedAlert.id)}
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                      >
                        Acquitter
                      </button>
                      <button
                        onClick={() => resolveMutation.mutate(selectedAlert.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                      >
                        Résoudre
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
