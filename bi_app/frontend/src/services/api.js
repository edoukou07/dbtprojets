import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token invalide ou expiré, rediriger vers login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Financier API
export const financierAPI = {
  getAll: (params) => api.get('/financier/', { params }),
  getSummary: (params) => api.get('/financier/summary/', { params }),
  getByZone: (params) => api.get('/financier/by_zone/', { params }),
  getTendancesMensuelles: (annee) => api.get('/financier/tendances_mensuelles/', { params: { annee } }),
  getTendancesTrimestrielles: (annee) => api.get('/financier/tendances_trimestrielles/', { params: { annee } }),
  getAnalyseRecouvrement: (annee) => api.get('/financier/analyse_recouvrement/', { params: { annee } }),
  getTopZonesPerformance: (annee, limit = 5) => api.get('/financier/top_zones_performance/', { params: { annee, limit } }),
  getComparaisonAnnuelle: (annee) => api.get('/financier/comparaison_annuelle/', { params: { annee } }),
};

// Occupation API
export const occupationAPI = {
  getAll: (params) => api.get('/occupation/', { params }),
  getSummary: () => api.get('/occupation/summary/'),
  getByZone: () => api.get('/occupation/by_zone/'),
  getDisponibilite: () => api.get('/occupation/disponibilite/'),
  getTopZones: (limit = 5) => api.get('/occupation/top_zones/', { params: { limit } }),
};

// Clients API
export const clientsAPI = {
  getAll: (params) => api.get('/clients/', { params }),
  getSummary: (params) => api.get('/clients/summary/', { params }),
  getTopClients: (limit = 10) => api.get('/clients/top_clients/', { params: { limit } }),
  getAtRisk: () => api.get('/clients/at_risk/'),
  getSegmentation: () => api.get('/clients/segmentation/'),
  getAnalyseComportement: () => api.get('/clients/analyse_comportement/'),
  getAnalyseOccupation: () => api.get('/clients/analyse_occupation/'),
};

// Opérationnel API
export const operationnelAPI = {
  getAll: (params) => api.get('/operationnel/', { params }),
  getSummary: (params) => api.get('/operationnel/summary/', { params }),
  getTrends: (params) => api.get('/operationnel/trends/', { params }),
  getPerformanceCollectes: (params) => api.get('/operationnel/performance_collectes/', { params }),
  getPerformanceAttributions: (params) => api.get('/operationnel/performance_attributions/', { params }),
  getPerformanceFacturation: (params) => api.get('/operationnel/performance_facturation/', { params }),
  getIndicateursCles: (params) => api.get('/operationnel/indicateurs_cles/', { params }),
};

export default api;
