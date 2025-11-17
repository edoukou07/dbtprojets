import { useState, useEffect } from 'react'
import React from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  BarChart, Bar, LineChart, Line, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Area, AreaChart, RadialBarChart, RadialBar
} from 'recharts'
import {
  AlertTriangle, TrendingUp, TrendingDown, Clock,
  Activity, DollarSign, Home, Calendar, Target, Filter
} from 'lucide-react'

const API_URL = 'http://localhost:8000/api'

// Composant Gauge personnalisé
const GaugeChart = ({ value, max, label, threshold, warningThreshold, unit = '%' }) => {
  const percentage = (value / max) * 100
  const rotation = (percentage / 100) * 180 - 90
  
  const getColor = () => {
    if (value >= threshold) return '#ef4444' // Rouge
    if (value >= warningThreshold) return '#f59e0b' // Orange
    return '#10b981' // Vert
  }
  
  const color = getColor()
  
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-24">
        <svg viewBox="0 0 200 100" className="w-full h-full">
          {/* Arc de fond */}
          <path
            d="M 20 80 A 80 80 0 0 1 180 80"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="20"
          />
          {/* Arc coloré */}
          <path
            d="M 20 80 A 80 80 0 0 1 180 80"
            fill="none"
            stroke={color}
            strokeWidth="20"
            strokeDasharray={`${(percentage / 100) * 251} 251`}
            strokeLinecap="round"
          />
          {/* Aiguille */}
          <g transform="translate(100, 80)">
            <line
              x1="0"
              y1="0"
              x2="0"
              y2="-60"
              stroke="#374151"
              strokeWidth="3"
              strokeLinecap="round"
              transform={`rotate(${rotation})`}
            />
            <circle cx="0" cy="0" r="5" fill="#374151" />
          </g>
        </svg>
        {/* Valeur */}
        <div className="absolute inset-0 flex items-end justify-center pb-2">
          <span className="text-3xl font-bold" style={{ color }}>
            {value.toFixed(1)}{unit}
          </span>
        </div>
      </div>
      <p className="text-sm font-medium text-gray-700 mt-2">{label}</p>
      <div className="flex gap-2 mt-1 text-xs">
        <span className="text-green-600">✓ &lt;{warningThreshold}{unit}</span>
        <span className="text-orange-600">⚠ {warningThreshold}-{threshold}{unit}</span>
        <span className="text-red-600">✗ &gt;{threshold}{unit}</span>
      </div>
    </div>
  )
}

// Composant Bullet Chart avec légende améliorée
const BulletChart = ({ label, value, threshold, warning, target, max }) => {
  const percentage = (value / max) * 100
  const thresholdPercentage = (threshold / max) * 100
  const warningPercentage = (warning / max) * 100
  const targetPercentage = (target / max) * 100
  
  const getColor = () => {
    if (value >= threshold) return 'bg-red-500'
    if (value >= warning) return 'bg-orange-500'
    return 'bg-green-500'
  }
  
  const getStatusIcon = () => {
    if (value >= threshold) return '🔴'
    if (value >= warning) return '🟠'
    return '🟢'
  }
  
  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">
          {getStatusIcon()} {label}
        </span>
        <span className="text-lg font-bold text-gray-900">{value.toFixed(1)}%</span>
      </div>
      <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
        {/* Zones de couleur */}
        <div className="absolute inset-0 flex">
          <div className="bg-green-100" style={{ width: `${warningPercentage}%` }}></div>
          <div className="bg-orange-100" style={{ width: `${thresholdPercentage - warningPercentage}%` }}></div>
          <div className="bg-red-100" style={{ width: `${100 - thresholdPercentage}%` }}></div>
        </div>
        {/* Barre de valeur */}
        <div
          className={`absolute inset-y-0 left-0 ${getColor()} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        ></div>
        {/* Marqueur cible */}
        <div
          className="absolute inset-y-0 w-1 bg-blue-600"
          style={{ left: `${targetPercentage}%` }}
        ></div>
      </div>
      <div className="flex justify-between text-xs text-gray-500 mt-1">
        <span>0</span>
        <span className="text-blue-600">Cible: {target}%</span>
        <span>{max}%</span>
      </div>
    </div>
  )
}

// Composant Heatmap avec tooltip
const HeatmapCell = ({ zone, value, occupation, onClick }) => {
  const getColor = () => {
    if (value >= 80) return 'bg-red-500 text-white'
    if (value >= 60) return 'bg-orange-500 text-white'
    if (value >= 40) return 'bg-yellow-500 text-gray-900'
    return 'bg-green-500 text-white'
  }
  
  const getRiskLabel = () => {
    if (value >= 80) return 'Critique'
    if (value >= 60) return 'Élevé'
    if (value >= 40) return 'Modéré'
    return 'Faible'
  }
  
  // Convertir occupation en nombre si nécessaire
  const occupationValue = typeof occupation === 'number' ? occupation : parseFloat(occupation) || 0
  
  return (
    <div
      onClick={onClick}
      className={`${getColor()} p-3 rounded-lg cursor-pointer hover:opacity-80 transition-all transform hover:scale-105 relative group`}
      title={`${zone}\nOccupation: ${occupationValue.toFixed(1)}%\nNiveau de risque: ${getRiskLabel()} (${value.toFixed(0)}%)`}
    >
      <div className="text-xs font-medium truncate">{zone}</div>
      <div className="text-lg font-bold">{value.toFixed(0)}%</div>
      <div className="text-xs opacity-75 mt-1">Occ: {occupationValue.toFixed(0)}%</div>
      
      {/* Tooltip au survol */}
      <div className="absolute hidden group-hover:block bg-gray-900 text-white text-xs rounded-lg p-3 -top-20 left-1/2 transform -translate-x-1/2 w-48 z-10 shadow-xl">
        <div className="font-bold mb-1">{zone}</div>
        <div>Occupation: {occupationValue.toFixed(1)}%</div>
        <div>Risque: {getRiskLabel()} ({value.toFixed(0)}%)</div>
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900"></div>
      </div>
    </div>
  )
}

export default function AlertsAnalytics() {
  const [selectedZone, setSelectedZone] = useState(null)
  const [timeRange, setTimeRange] = useState('30')
  
  // Fonction pour calculer le niveau de risque basé sur l'occupation
  const calculateRiskScore = (occupation) => {
    // Zones critiques (rouge):
    if (occupation < 30) return 85  // Sous-occupation critique
    if (occupation > 95) return 90  // Saturation critique
    
    // Zones à risque élevé (orange):
    if (occupation < 50) return 65  // Sous-occupation modérée
    if (occupation > 90) return 70  // Proche saturation
    
    // Zones à surveiller (jaune):
    if (occupation < 60) return 45  // Légèrement sous-occupée
    if (occupation > 85) return 50  // Occupation élevée
    
    // Zone optimale (vert): 60-85%
    return 20
  }
  
  // Récupérer les alertes
  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${API_URL}/alerts/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.data
    }
  })
  
  // Récupérer les données financières
  const { data: financialData } = useQuery({
    queryKey: ['financier-summary'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${API_URL}/financier/summary/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      console.log('💰 Réponse API financier complète:', response.data)
      if (Array.isArray(response.data) && response.data.length > 0) {
        console.log('💰 Premier élément du tableau:', response.data[0])
        console.log('💰 Clés disponibles:', Object.keys(response.data[0]))
      }
      return response.data
    }
  })
  
  // Récupérer les données d'occupation
  const { data: occupationData, isLoading: occupationLoading, error: occupationError } = useQuery({
    queryKey: ['occupation-zones'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${API_URL}/occupation/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      console.log('📊 Réponse API occupation:', response.data)
      return response.data
    },
    retry: 2,
  })
  
  // Calculer le taux d'occupation moyen depuis les données d'occupation
  const tauxOccupationMoyen = React.useMemo(() => {
    const zonesData = occupationData?.results || occupationData?.data || occupationData || []
    
    if (!Array.isArray(zonesData) || zonesData.length === 0) {
      console.log('⚠️ Pas de zones pour calculer le taux d\'occupation')
      return 0
    }
    
    const validZones = zonesData.filter(zone => {
      const taux = zone.taux_occupation_pct || zone.occupation || zone.taux_occupation
      return taux !== null && taux !== undefined && !isNaN(taux)
    })
    
    if (validZones.length === 0) {
      console.log('⚠️ Aucune zone avec un taux d\'occupation valide')
      return 0
    }
    
    const total = validZones.reduce((sum, zone) => {
      const taux = parseFloat(zone.taux_occupation_pct || zone.occupation || zone.taux_occupation || 0)
      return sum + taux
    }, 0)
    
    const moyenne = total / validZones.length
    console.log(`✅ Taux d'occupation moyen calculé: ${moyenne.toFixed(2)}% (${validZones.length} zones)`)
    
    return isNaN(moyenne) ? 0 : moyenne
  }, [occupationData])
  
  // Calculer les métriques financières
  const financialMetrics = React.useMemo(() => {
    if (!financialData) {
      return { tauxImpaye: 0, delaiMoyen: 0 }
    }
    
    // L'API retourne maintenant un objet avec les agrégations
    const tauxPaiement = financialData.taux_paiement_moyen || 0
    const delai = financialData.delai_moyen_paiement || 0
    
    console.log('💰 Métriques financières:', {
      tauxPaiement: tauxPaiement.toFixed(2),
      delai: delai,
      allFields: Object.keys(financialData)
    })
    
    return {
      tauxImpaye: 100 - tauxPaiement,
      delaiMoyen: parseFloat(delai) || 0
    }
  }, [financialData])
  
  // Données pour les gauges avec vérifications
  const gaugesData = {
    impaye: {
      value: financialMetrics.tauxImpaye,
      max: 100,
      threshold: 40,
      warning: 25
    },
    occupation: {
      value: tauxOccupationMoyen,
      max: 100,
      threshold: 95,
      warning: 80
    },
    delai: {
      value: financialMetrics.delaiMoyen,
      max: 120,
      threshold: 90,
      warning: 60
    }
  }
  
  console.log('📊 Données des gauges:', {
    impaye: gaugesData.impaye.value.toFixed(2),
    occupation: gaugesData.occupation.value.toFixed(2),
    delai: gaugesData.delai.value.toFixed(2)
  })
  
  // Données pour la timeline
  const timelineData = React.useMemo(() => {
    if (!alerts || !Array.isArray(alerts)) return []
    
    return alerts.reduce((acc, alert) => {
      const date = new Date(alert.created_at).toLocaleDateString('fr-FR')
      const existing = acc.find(item => item.date === date)
      if (existing) {
        existing.count++
        if (alert.severity === 'critical') existing.critical++
        if (alert.severity === 'high') existing.warning++
      } else {
        acc.push({
          date,
          count: 1,
          critical: alert.severity === 'critical' ? 1 : 0,
          warning: alert.severity === 'high' ? 1 : 0
        })
      }
      return acc
    }, []).slice(-30)
  }, [alerts])
  
  // ...existing code...
  
  // Données heatmap par zone
  const heatmapData = React.useMemo(() => {
    // Vérifier plusieurs formats de réponse possibles
    const zonesData = occupationData?.results || occupationData?.data || occupationData || []
    
    if (!Array.isArray(zonesData)) {
      console.log('⚠️ Format de données inattendu:', occupationData)
      return []
    }
    
    if (zonesData.length === 0) {
      console.log('⚠️ Aucune zone trouvée dans la réponse')
      return []
    }
    
    console.log('✅ Données d\'occupation reçues:', zonesData.length, 'zones')
    console.log('📋 Exemple de zone:', zonesData[0])
    
    return zonesData.slice(0, 12).map(zone => ({
      zone: zone.nom_zone || zone.name || zone.zone_name || 'Zone inconnue',
      occupation: zone.taux_occupation_pct || zone.occupation || zone.taux_occupation || 0,
      risk: calculateRiskScore(zone.taux_occupation_pct || zone.occupation || zone.taux_occupation || 0)
    }))
  }, [occupationData, calculateRiskScore])
  
  // Distribution des alertes par sévérité
  const severityData = React.useMemo(() => {
    if (!alerts || !Array.isArray(alerts)) {
      return [
        { name: 'Critique', value: 0, color: '#ef4444' },
        { name: 'Élevé', value: 0, color: '#f59e0b' },
        { name: 'Moyen', value: 0, color: '#eab308' },
        { name: 'Faible', value: 0, color: '#3b82f6' }
      ]
    }
    
    return [
      { name: 'Critique', value: alerts.filter(a => a.severity === 'critical').length, color: '#ef4444' },
      { name: 'Élevé', value: alerts.filter(a => a.severity === 'high').length, color: '#f59e0b' },
      { name: 'Moyen', value: alerts.filter(a => a.severity === 'medium').length, color: '#eab308' },
      { name: 'Faible', value: alerts.filter(a => a.severity === 'low').length, color: '#3b82f6' }
    ]
  }, [alerts])
  
  if (alertsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des analytics...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Activity className="w-8 h-8 text-blue-600" />
            Analytics des Alertes
          </h1>
          <p className="text-gray-600 mt-1">
            Visualisation avancée et analyse des alertes du système
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="7">7 derniers jours</option>
            <option value="30">30 derniers jours</option>
            <option value="90">90 derniers jours</option>
          </select>
        </div>
      </div>
      
      {/* VUE PRINCIPALE */}
      <div className="space-y-6">
        
        {/* Section Heatmap des Zones */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Home className="w-6 h-6 text-blue-600" />
            Carte de Chaleur - Zones à Risque
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Score de risque basé sur le taux d'occupation des zones. 
            <span className="font-semibold">Zone optimale: 60-85%</span> | 
            Critique si &lt;30% (sous-occupation) ou &gt;95% (saturation)
          </p>
          {occupationLoading ? (
            <div className="text-center py-12 text-gray-500">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-sm">Chargement des données d'occupation...</p>
            </div>
          ) : occupationError ? (
            <div className="text-center py-12 text-red-500">
              <AlertTriangle className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p className="text-lg font-medium">Erreur de chargement</p>
              <p className="text-sm mt-2">{occupationError.message}</p>
            </div>
          ) : heatmapData.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Home className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p className="text-lg font-medium">Aucune donnée d'occupation disponible</p>
              <p className="text-sm mt-2">Vérifiez que l'endpoint /api/occupation/ retourne des données</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {heatmapData.map((item, index) => (
                <HeatmapCell
                  key={index}
                  zone={item.zone}
                  occupation={item.occupation}
                  value={item.risk}
                  onClick={() => setSelectedZone(item.zone)}
                />
              ))}
            </div>
          )}
          <div className="mt-4 flex items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span>Faible risque (&lt;40%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span>Risque modéré (40-60%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-orange-500 rounded"></div>
              <span>Risque élevé (60-80%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span>Risque critique (&gt;80%)</span>
            </div>
          </div>
        </div>
        
        {/* Section 3: Timeline */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-blue-600" />
            Historique des Alertes (30 derniers jours)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="critical"
                stackId="1"
                stroke="#ef4444"
                fill="#ef4444"
                name="Critiques"
              />
              <Area
                type="monotone"
                dataKey="warning"
                stackId="1"
                stroke="#f59e0b"
                fill="#f59e0b"
                name="Warnings"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* VUE DÉTAILLÉE */}
      {/* Les graphiques Treemap et PieChart ont été supprimés selon la demande. */}
      
      {/* Bullet Charts - KPIs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <DollarSign className="w-6 h-6 text-blue-600" />
          Indicateurs Clés de Performance
        </h2>
        <p className="text-sm text-gray-600 mb-6">
          Comparaison des indicateurs actuels avec les seuils configurés. 
          <span className="font-semibold"> Barre verte</span> = zone sûre, 
          <span className="font-semibold text-orange-600"> orange</span> = attention, 
          <span className="font-semibold text-red-600"> rouge</span> = alerte. 
          Le <span className="font-semibold text-blue-600">trait bleu</span> indique la cible optimale.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <BulletChart
              label="Taux d'Impayés"
              value={gaugesData.impaye.value}
              threshold={40}
              warning={25}
              target={15}
              max={100}
            />
            <p className="text-xs text-gray-500 mt-2 ml-2">
              📊 Pourcentage de factures non payées. Cible: &lt;15% | Critique si &gt;40%
            </p>
            <BulletChart
              label="Délai de Paiement (jours)"
              value={(gaugesData.delai.value / 120) * 100}
              threshold={75}
              warning={50}
              target={40}
              max={100}
            />
            <p className="text-xs text-gray-500 mt-2 ml-2">
              ⏱️ Temps moyen avant paiement. Cible: 48j (~40%) | Critique si &gt;90j (~75%)
            </p>
          </div>
          <div>
            <BulletChart
              label="Taux d'Occupation"
              value={gaugesData.occupation.value}
              threshold={95}
              warning={80}
              target={85}
              max={100}
            />
            <p className="text-xs text-gray-500 mt-2 ml-2">
              🏢 Taux moyen d'occupation des zones. Cible: 85% | Critique si &gt;95% (saturation)
            </p>
            <BulletChart
              label="Taux de Recouvrement"
              value={financialData?.taux_recouvrement_moyen || 0}
              threshold={60}
              warning={75}
              target={90}
              max={100}
            />
          </div>
        </div>
      </div>
      
      {/* Tableau détaillé des alertes */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Clock className="w-6 h-6 text-blue-600" />
          Liste Détaillée des Alertes
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sévérité
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Titre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Message
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {alerts && Array.isArray(alerts) && alerts.slice(0, 10).map((alert) => (
                <tr key={alert.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{alert.title}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500 max-w-xs truncate">{alert.message}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(alert.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      alert.status === 'active' ? 'bg-red-100 text-red-800' :
                      alert.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {alert.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
