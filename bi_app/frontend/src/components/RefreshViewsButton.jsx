import React, { useState, useEffect } from 'react';
import { RefreshCw, Database, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const RefreshViewsButton = ({ className = '' }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [viewsStatus, setViewsStatus] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [showStatus, setShowStatus] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Récupérer le token JWT
  const getAuthToken = () => {
    return localStorage.getItem('access_token') || localStorage.getItem('token');
  };

  // Charger le statut des vues au montage
  useEffect(() => {
    fetchViewsStatus();
  }, []);

  const fetchViewsStatus = async () => {
    try {
      const token = getAuthToken();
      const response = await axios.get(`${API_BASE_URL}/refresh/status/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.data.success) {
        setViewsStatus(response.data.views);
      }
    } catch (err) {
      console.error('Erreur lors de la récupération du statut:', err);
    }
  };

  const handleRefreshAll = async () => {
    setRefreshing(true);
    setError(null);
    setSuccess(null);

    try {
      const token = getAuthToken();
      
      if (!token) {
        setError('Vous devez être connecté pour rafraîchir les vues');
        setRefreshing(false);
        return;
      }

      const response = await axios.post(
        `${API_BASE_URL}/refresh/all/`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setSuccess(`✓ Vues rafraîchies en ${response.data.duration_seconds.toFixed(1)}s`);
        setLastRefresh(new Date());
        await fetchViewsStatus(); // Recharger le statut
        
        // Effacer le message de succès après 5 secondes
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(response.data.message || 'Erreur lors du rafraîchissement');
      }
    } catch (err) {
      console.error('Erreur:', err);
      if (err.response?.status === 401) {
        setError('Session expirée. Veuillez vous reconnecter.');
      } else if (err.response?.status === 408) {
        setError('Timeout: le rafraîchissement prend trop de temps');
      } else {
        setError(err.response?.data?.message || 'Erreur lors du rafraîchissement');
      }
    } finally {
      setRefreshing(false);
    }
  };

  const handleRefreshSpecific = async (viewName) => {
    setRefreshing(true);
    setError(null);
    setSuccess(null);

    try {
      const token = getAuthToken();
      const response = await axios.post(
        `${API_BASE_URL}/refresh/${viewName}/`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.success) {
        setSuccess(`✓ Vue ${viewName} rafraîchie en ${response.data.duration_seconds.toFixed(1)}s`);
        await fetchViewsStatus();
        setTimeout(() => setSuccess(null), 5000);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors du rafraîchissement');
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Bouton principal */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleRefreshAll}
          disabled={refreshing}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg font-medium
            transition-all duration-200 shadow-sm
            ${refreshing 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md active:scale-95'
            }
          `}
          title="Rafraîchir toutes les vues matérialisées"
        >
          <RefreshCw 
            className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} 
          />
          <span>
            {refreshing ? 'Rafraîchissement...' : 'Rafraîchir les vues'}
          </span>
        </button>

        {/* Bouton Statut */}
        <button
          onClick={() => setShowStatus(!showStatus)}
          className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
          title="Voir le statut des vues"
        >
          <Database className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      {/* Messages de retour */}
      {success && (
        <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-800 text-sm">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-800 text-sm">
          <XCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {lastRefresh && (
        <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Dernière mise à jour: {lastRefresh.toLocaleTimeString()}
        </div>
      )}

      {/* Panel de statut */}
      {showStatus && (
        <div className="absolute top-full mt-2 right-0 w-96 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-auto">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <Database className="w-5 h-5" />
              Statut des vues matérialisées
            </h3>
          </div>

          <div className="p-4 space-y-3">
            {viewsStatus ? (
              viewsStatus.map((view) => (
                <div
                  key={view.name}
                  className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-800 text-sm">
                      {view.name}
                    </span>
                    <button
                      onClick={() => handleRefreshSpecific(view.name)}
                      disabled={refreshing}
                      className="p-1 rounded hover:bg-blue-50 text-blue-600 disabled:opacity-50"
                      title={`Rafraîchir ${view.name}`}
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>
                  </div>

                  {view.exists ? (
                    <div className="space-y-1 text-xs text-gray-600">
                      <div className="flex justify-between">
                        <span>Taille:</span>
                        <span className="font-mono">{view.size || 'N/A'}</span>
                      </div>
                      {view.last_analyze && (
                        <div className="flex justify-between">
                          <span>Dernière analyse:</span>
                          <span className="font-mono">
                            {new Date(view.last_analyze).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                      <div className="flex items-center gap-1 text-green-600 mt-1">
                        <CheckCircle className="w-3 h-3" />
                        <span>Active</span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-orange-600 text-xs">
                      <AlertCircle className="w-3 h-3" />
                      <span>Vue non trouvée</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-4">
                Chargement du statut...
              </div>
            )}
          </div>

          <div className="p-3 border-t border-gray-200 bg-gray-50 text-xs text-gray-600">
            <p className="flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              Le rafraîchissement peut prendre plusieurs minutes
            </p>
          </div>
        </div>
      )}

      {/* Overlay pour fermer le panel */}
      {showStatus && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowStatus(false)}
        />
      )}
    </div>
  );
};

export default RefreshViewsButton;
