import { apiClient } from './api'

/**
 * Service pour accéder aux données de conformité et infractions via l'API
 */

export const complianceAPI = {
  /**
   * Récupère le résumé des infractions pour une année donnée
   */
  getSummary: async (annee = new Date().getFullYear()) => {
    try {
      const response = await apiClient.get('/api/compliance/summary/', {
        params: { annee }
      })
      return response.data
    } catch (error) {
      console.error('Erreur récupération résumé conformité:', error)
      throw error
    }
  },

  /**
   * Récupère les tendances annuelles des infractions
   */
  getTendancesAnnuelles: async () => {
    try {
      const response = await apiClient.get('/api/compliance/tendances-annuelles/')
      return response.data || []
    } catch (error) {
      console.error('Erreur récupération tendances:', error)
      throw error
    }
  },

  /**
   * Récupère les infractions groupées par zone
   */
  getInfractionsParZone: async (annee = new Date().getFullYear()) => {
    try {
      const response = await apiClient.get('/api/compliance/infractions-par-zone/', {
        params: { annee }
      })
      return response.data || []
    } catch (error) {
      console.error('Erreur récupération infractions par zone:', error)
      throw error
    }
  },

  /**
   * Récupère la distribution des infractions par gravité
   */
  getDistributionGravite: async (annee = new Date().getFullYear()) => {
    try {
      const response = await apiClient.get('/api/compliance/distribution-gravite/', {
        params: { annee }
      })
      return response.data || []
    } catch (error) {
      console.error('Erreur récupération distribution gravité:', error)
      throw error
    }
  },

  /**
   * Récupère les statistiques de résolution par zone
   */
  getResolutionStats: async (annee = new Date().getFullYear()) => {
    try {
      const response = await apiClient.get('/api/compliance/resolution-stats/', {
        params: { annee }
      })
      return response.data || []
    } catch (error) {
      console.error('Erreur récupération stats résolution:', error)
      throw error
    }
  },

  /**
   * Récupère le détail des infractions avec filtres optionnels
   */
  getInfractionsDetail: async (filters = {}) => {
    try {
      const response = await apiClient.get('/api/compliance/infractions-detail/', {
        params: {
          annee: filters.annee || new Date().getFullYear(),
          zone_id: filters.zone_id || undefined,
          gravite: filters.gravite || undefined,
          statut: filters.statut || 'all',
        }
      })
      return response.data || []
    } catch (error) {
      console.error('Erreur récupération détail infractions:', error)
      throw error
    }
  },

  /**
   * Récupère la liste des zones disponibles
   */
  getZones: async () => {
    try {
      const response = await apiClient.get('/api/compliance/zones/')
      return response.data || []
    } catch (error) {
      console.error('Erreur récupération zones:', error)
      throw error
    }
  },

  /**
   * Export le rapport complet de conformité
   */
  exportRapport: async (annee = new Date().getFullYear()) => {
    try {
      const response = await apiClient.get('/api/compliance/export-rapport/', {
        params: { annee },
        responseType: 'blob'
      })
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `compliance_rapport_${annee}.csv`)
      document.body.appendChild(link)
      link.click()
      link.parentElement.removeChild(link)
      
      return true
    } catch (error) {
      console.error('Erreur export rapport:', error)
      throw error
    }
  }
}

export default complianceAPI
