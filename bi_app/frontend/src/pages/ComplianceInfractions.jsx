import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, AreaChart, Area, ComposedChart
} from 'recharts'
import {
  AlertTriangle, CheckCircle, Clock, TrendingUp, TrendingDown,
  AlertCircle, MapPin, Calendar, Filter, Download, Eye, EyeOff
} from 'lucide-react'
import api from '../services/api'
import StatsCard from '../components/StatsCard'
import ExportButton from '../components/ExportButton'

// Couleurs par gravité
const SEVERITY_COLORS = {
  mineure: '#10b981',      // Green
  moderee: '#f59e0b',      // Amber
  majeure: '#ef4444',      // Red
  critique: '#7c3aed'      // Purple
}

const SEVERITY_LABELS = {
  mineure: 'Mineure',
  moderee: 'Modérée',
  majeure: 'Majeure',
  critique: 'Critique'
}

export default function ComplianceInfractions() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [selectedZone, setSelectedZone] = useState('')
  const [selectedSeverity, setSelectedSeverity] = useState('')
  const [showResolved, setShowResolved] = useState(true)
  const [showUnresolved, setShowUnresolved] = useState(true)

  // API Calls
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['compliance-summary', selectedYear],
    queryFn: () => api.get('/compliance/summary/', {
      params: { annee: selectedYear }
    }).then(res => res.data),
  })

  const { data: tendancesAnnuelles } = useQuery({
    queryKey: ['compliance-tendances-annuelles'],
    queryFn: () => api.get('/compliance/tendances_annuelles/').then(res => res.data),
  })

  const { data: infractionsParZone } = useQuery({
    queryKey: ['compliance-par-zone', selectedYear],
    queryFn: () => api.get('/compliance/infractions_par_zone/', {
      params: { annee: selectedYear }
    }).then(res => res.data),
  })

  const { data: distributionGravite } = useQuery({
    queryKey: ['compliance-distribution-gravite', selectedYear],
    queryFn: () => api.get('/compliance/distribution_gravite/', {
      params: { annee: selectedYear }
    }).then(res => res.data),
  })

  const { data: resolutionStats } = useQuery({
    queryKey: ['compliance-resolution', selectedYear],
    queryFn: () => api.get('/compliance/resolution_stats/', {
      params: { annee: selectedYear }
    }).then(res => res.data),
  })

  const { data: infractionsDetail } = useQuery({
    queryKey: ['compliance-infractions-detail', selectedYear, selectedZone, selectedSeverity],
    queryFn: () => api.get('/compliance/infractions_detail/', {
      params: {
        annee: selectedYear,
        zone_id: selectedZone || undefined,
        gravite: selectedSeverity || undefined
      }
    }).then(res => res.data),
  })

  const { data: zones } = useQuery({
    queryKey: ['compliance-zones'],
    queryFn: () => api.get('/compliance/zones/').then(res => res.data),
  })

  // Format helpers
  const formatNumber = (value) => {
    if (!value && value !== 0) return '0'
    return new Intl.NumberFormat('fr-FR').format(value)
  }

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0%'
    return value.toFixed(1) + '%'
  }

  const formatDays = (value) => {
    if (!value && value !== 0) return '0 jours'
    return value.toFixed(1) + ' j'
  }

  // Prepare export data
  const exportData = [
    {
      'Métrique': 'Nombre Total Infractions',
      'Valeur': summary?.nombre_total_infractions || 0,
      'Format': formatNumber(summary?.nombre_total_infractions)
    },
    {
      'Métrique': 'Infractions Résolues',
      'Valeur': summary?.infractions_resolues || 0,
      'Format': formatNumber(summary?.infractions_resolues)
    },
    {
      'Métrique': 'Taux de Résolution',
      'Valeur': summary?.taux_resolution_moyen_pct || 0,
      'Format': formatPercent(summary?.taux_resolution_moyen_pct)
    },
    {
      'Métrique': 'Infractions Critiques',
      'Valeur': summary?.nombre_infractions_critiques || 0,
      'Format': formatNumber(summary?.nombre_infractions_critiques)
    },
    {
      'Métrique': 'Délai Moyen Résolution',
      'Valeur': summary?.delai_moyen_resolution || 0,
      'Format': formatDays(summary?.delai_moyen_resolution)
    },
    {
      'Métrique': 'Sévérité Moyenne',
      'Valeur': summary?.severite_moyenne || 0,
      'Format': summary?.severite_moyenne?.toFixed(2)
    }
  ]

  const isLoading = summaryLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des données de conformité...</p>
        </div>
      </div>
    )
  }

  // Zones for filter
  const zonesList = zones || []

  // Filter compliance detail data
  const filteredInfractions = infractionsDetail?.filter(inf => {
    if (selectedSeverity && inf.gravite !== selectedSeverity) return false
    return true
  }) || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Infractions</h2>
        <ExportButton
          data={exportData}
          filename="compliance_infractions"
          title="Rapport Infractions"
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Year Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Année</label>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {[2023, 2024, 2025, 2026].map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          {/* Zone Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Zone</label>
            <select
              value={selectedZone}
              onChange={(e) => setSelectedZone(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les zones</option>
              {zonesList.map(zone => (
                <option key={zone.zone_id} value={zone.zone_id}>{zone.zone_name}</option>
              ))}
            </select>
          </div>

          {/* Severity Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Gravité</label>
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Toutes les gravités</option>
              <option value="mineure">Mineure</option>
              <option value="moderee">Modérée</option>
              <option value="majeure">Majeure</option>
              <option value="critique">Critique</option>
            </select>
          </div>

          {/* Status Filters */}
          <div className="flex items-end gap-2">
            <button
              onClick={() => setShowResolved(!showResolved)}
              className={`flex-1 px-3 py-2 rounded-lg flex items-center justify-center gap-2 ${
                showResolved
                  ? 'bg-green-100 text-green-700 border border-green-300'
                  : 'bg-gray-100 text-gray-500 border border-gray-300'
              }`}
              title="Infractions résolues"
            >
              <CheckCircle className="w-4 h-4" />
              <span className="text-xs font-medium">Résolues</span>
            </button>
            <button
              onClick={() => setShowUnresolved(!showUnresolved)}
              className={`flex-1 px-3 py-2 rounded-lg flex items-center justify-center gap-2 ${
                showUnresolved
                  ? 'bg-red-100 text-red-700 border border-red-300'
                  : 'bg-gray-100 text-gray-500 border border-gray-300'
              }`}
              title="Infractions non résolues"
            >
              <AlertCircle className="w-4 h-4" />
              <span className="text-xs font-medium">Non résolues</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatsCard
          title="Total Infractions"
          value={formatNumber(summary?.nombre_total_infractions)}
          subtitle="Période sélectionnée"
          icon={AlertTriangle}
          trend={{
            value: summary?.variation_infractions_pct,
            direction: summary?.variation_infractions_pct < 0 ? 'down' : 'up'
          }}
        />

        <StatsCard
          title="Taux de Résolution"
          value={formatPercent(summary?.taux_resolution_moyen_pct)}
          subtitle="Infractions résolues"
          icon={CheckCircle}
          trend={{
            value: summary?.variation_resolution_pct,
            direction: summary?.variation_resolution_pct > 0 ? 'up' : 'down'
          }}
        />

        <StatsCard
          title="Délai Moyen"
          value={formatDays(summary?.delai_moyen_resolution)}
          subtitle="Temps de résolution"
          icon={Clock}
          trend={{
            value: summary?.variation_delai_pct,
            direction: summary?.variation_delai_pct < 0 ? 'down' : 'up'
          }}
        />

        <StatsCard
          title="Infractions Critiques"
          value={formatNumber(summary?.nombre_infractions_critiques)}
          subtitle="Priorité maximale"
          icon={AlertCircle}
          className="border-l-4 border-purple-500"
        />

        <StatsCard
          title="Zones Affectées"
          value={formatNumber(summary?.nombre_zones_affectees)}
          subtitle="Zones avec infractions"
          icon={MapPin}
        />

        <StatsCard
          title="Sévérité Moyenne"
          value={summary?.severite_moyenne?.toFixed(2) || '0'}
          subtitle="Score de 1 à 4"
          icon={TrendingUp}
        />
      </section>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tendance Annuelle */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Tendance Annuelle des Infractions</h3>
            <Calendar className="w-5 h-5 text-gray-400" />
          </div>
          {tendancesAnnuelles?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={tendancesAnnuelles}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="annee_mois" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#f3f4f6', border: '1px solid #e5e7eb' }}
                  formatter={(value) => formatNumber(value)}
                />
                <Legend />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="nombre_infractions"
                  fill="#fecaca"
                  stroke="#ef4444"
                  name="Total infractions"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="taux_resolution_pct"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="Taux résolution (%)"
                />
              </ComposedChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              Aucune donnée disponible
            </div>
          )}
        </div>

        {/* Distribution Gravité */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Distribution par Gravité</h3>
            <AlertTriangle className="w-5 h-5 text-gray-400" />
          </div>
          {distributionGravite?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={distributionGravite}
                  dataKey="nombre"
                  nameKey="gravite"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {distributionGravite.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[entry.gravite]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => formatNumber(value)}
                  labelFormatter={(label) => SEVERITY_LABELS[label] || label}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              Aucune donnée disponible
            </div>
          )}
        </div>
      </div>

      {/* Infractions par Zone */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Infractions par Zone</h3>
          <MapPin className="w-5 h-5 text-gray-400" />
        </div>
        {infractionsParZone?.length > 0 ? (
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={infractionsParZone}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="zone_name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip
                contentStyle={{ backgroundColor: '#f3f4f6', border: '1px solid #e5e7eb' }}
                formatter={(value) => formatNumber(value)}
              />
              <Legend />
              <Bar dataKey="infractions_mineures" stackId="a" fill="#10b981" name="Mineures" />
              <Bar dataKey="infractions_moderees" stackId="a" fill="#f59e0b" name="Modérées" />
              <Bar dataKey="infractions_majeures" stackId="a" fill="#ef4444" name="Majeures" />
              <Bar dataKey="infractions_critiques" stackId="a" fill="#7c3aed" name="Critiques" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-350 flex items-center justify-center text-gray-500">
            Aucune donnée disponible
          </div>
        )}
      </div>

      {/* Resolution Performance */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Performance de Résolution par Zone</h3>
          <CheckCircle className="w-5 h-5 text-gray-400" />
        </div>
        {resolutionStats?.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" dataKey="nombre_infractions" name="Total Infractions" />
              <YAxis type="number" dataKey="taux_resolution_pct" name="Taux Résolution (%)" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter
                name="Zones"
                data={resolutionStats}
                fill="#0ea5e9"
                shape="circle"
              />
            </ScatterChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-300 flex items-center justify-center text-gray-500">
            Aucune donnée disponible
          </div>
        )}
      </div>

      {/* Détail Infractions Table */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Détail des Infractions ({filteredInfractions.length})</h3>
          <Filter className="w-5 h-5 text-gray-400" />
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Zone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Gravité</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Statut</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Détection</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Délai (j)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredInfractions.slice(0, 20).map((inf, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 text-sm text-gray-900">{inf.zone_name}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{inf.type_infraction}</td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      style={{
                        backgroundColor: SEVERITY_COLORS[inf.gravite] + '20',
                        color: SEVERITY_COLORS[inf.gravite]
                      }}
                    >
                      {SEVERITY_LABELS[inf.gravite]}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {inf.est_resolue ? (
                      <span className="inline-flex items-center gap-1 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        Résolue
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-red-600">
                        <AlertCircle className="w-4 h-4" />
                        En cours
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {new Date(inf.date_detection).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {inf.jours_resolution?.toFixed(0) || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredInfractions.length > 20 && (
            <div className="px-6 py-4 text-center text-sm text-gray-500">
              +{filteredInfractions.length - 20} infractions supplémentaires
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
