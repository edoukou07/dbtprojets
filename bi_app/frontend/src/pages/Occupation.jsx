import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  Building2, 
  MapPin, 
  TrendingUp, 
  TrendingDown, 
  Layers,
  AlertCircle,
  CheckCircle,
  Hash,
  ExternalLink
} from 'lucide-react'
import { occupationAPI } from '../services/api'
import StatsCard from '../components/StatsCard'

export default function Occupation() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['occupation-summary'],
    queryFn: () => occupationAPI.getSummary().then(res => res.data),
  })

  const { data: zonesData, isLoading: zonesLoading } = useQuery({
    queryKey: ['occupation-by-zone'],
    queryFn: () => occupationAPI.getByZone().then(res => res.data),
  })

  const { data: disponibilite, isLoading: dispoLoading } = useQuery({
    queryKey: ['occupation-disponibilite'],
    queryFn: () => occupationAPI.getDisponibilite().then(res => res.data),
  })

  const { data: topZones } = useQuery({
    queryKey: ['occupation-top-zones'],
    queryFn: () => occupationAPI.getTopZones(5).then(res => res.data),
  })

  const formatNumber = (value) => {
    if (!value && value !== 0) return '0'
    return new Intl.NumberFormat('fr-FR').format(value)
  }

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0%'
    return value.toFixed(1) + '%'
  }

  const formatSuperficie = (value) => {
    if (!value && value !== 0) return '0 m²'
    return formatNumber(value) + ' m²'
  }

  const getOccupationColor = (rate) => {
    if (rate >= 90) return 'text-red-600 bg-red-50'
    if (rate >= 70) return 'text-orange-600 bg-orange-50'
    if (rate >= 50) return 'text-green-600 bg-green-50'
    return 'text-blue-600 bg-blue-50'
  }

  const getOccupationStatus = (rate) => {
    if (rate >= 90) return { label: 'Saturée', color: 'red' }
    if (rate >= 70) return { label: 'Élevée', color: 'orange' }
    if (rate >= 50) return { label: 'Normale', color: 'green' }
    return { label: 'Faible', color: 'blue' }
  }

  return (
    <div className="space-y-8">
      {/* KPIs Principaux */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Building2 className="w-6 h-6 mr-2 text-blue-600" />
          Vue d'Ensemble
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Zones Industrielles"
            value={formatNumber(summary?.nombre_zones)}
            subtitle="Zones actives"
            icon={MapPin}
            color="indigo"
            loading={summaryLoading}
          />
          <StatsCard
            title="Total Lots"
            value={formatNumber(summary?.total_lots)}
            subtitle="Capacité totale"
            icon={Building2}
            color="blue"
            loading={summaryLoading}
          />
          <StatsCard
            title="Lots Attribués"
            value={formatNumber(summary?.lots_attribues)}
            subtitle={`${formatPercent(summary?.taux_occupation_moyen)} occupés`}
            icon={CheckCircle}
            color="green"
            loading={summaryLoading}
          />
          <StatsCard
            title="Lots Disponibles"
            value={formatNumber(summary?.lots_disponibles)}
            subtitle="Prêts à l'attribution"
            icon={Layers}
            color="orange"
            loading={summaryLoading}
          />
        </div>
      </section>

      {/* Statistiques de Surface */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Layers className="w-6 h-6 mr-2 text-blue-600" />
          Superficies
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard
            title="Superficie Totale"
            value={formatSuperficie(summary?.superficie_totale)}
            subtitle="Surface industrielle"
            icon={Layers}
            color="purple"
            loading={summaryLoading}
          />
          <StatsCard
            title="Surface Attribuée"
            value={formatSuperficie(summary?.superficie_attribuee)}
            subtitle="En exploitation"
            icon={CheckCircle}
            color="green"
            loading={summaryLoading}
          />
          <StatsCard
            title="Surface Disponible"
            value={formatSuperficie(summary?.superficie_disponible)}
            subtitle="Disponible"
            icon={Building2}
            color="blue"
            loading={summaryLoading}
          />
        </div>
      </section>

      {/* Alertes et Zones Critiques */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <AlertCircle className="w-6 h-6 mr-2 text-blue-600" />
          Alertes d'Occupation
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Zones Saturées</p>
                <p className="text-3xl font-bold text-red-900 mt-2">
                  {formatNumber(summary?.zones_saturees)}
                </p>
                <p className="text-sm text-red-600 mt-1">Occupation &gt; 90%</p>
              </div>
              <div className="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Zones Sous-Occupées</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {formatNumber(summary?.zones_faible_occupation)}
                </p>
                <p className="text-sm text-blue-600 mt-1">Occupation &lt; 50%</p>
              </div>
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tableau des Zones */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Hash className="w-6 h-6 mr-2 text-blue-600" />
          Détails par Zone
        </h3>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {zonesLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-500 mt-4">Chargement des données...</p>
            </div>
          ) : zonesData && zonesData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Zone
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Taux Occupation
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lots Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Attribués
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Disponibles
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Superficie
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {zonesData.map((zone, index) => {
                    const status = getOccupationStatus(zone.taux_occupation_pct)
                    return (
                      <tr key={index} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <MapPin className="w-5 h-5 text-gray-400 mr-2" />
                              <span className="text-sm font-medium text-gray-900">
                                {zone.nom_zone || 'N/A'}
                              </span>
                            </div>
                            <Link
                              to={`/occupation/zone/${encodeURIComponent(zone.nom_zone)}`}
                              className="ml-3 text-blue-600 hover:text-blue-800"
                              title="Voir les détails"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </Link>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-1 max-w-32">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${
                                    zone.taux_occupation_pct >= 90 ? 'bg-red-600' :
                                    zone.taux_occupation_pct >= 70 ? 'bg-orange-500' :
                                    zone.taux_occupation_pct >= 50 ? 'bg-green-500' :
                                    'bg-blue-500'
                                  }`}
                                  style={{ width: `${Math.min(zone.taux_occupation_pct || 0, 100)}%` }}
                                ></div>
                              </div>
                            </div>
                            <span className="ml-3 text-sm font-semibold text-gray-900">
                              {formatPercent(zone.taux_occupation_pct)}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(zone.nombre_total_lots)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                          {formatNumber(zone.lots_attribues)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 font-medium">
                          {formatNumber(zone.lots_disponibles)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {formatSuperficie(zone.superficie_totale)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            status.color === 'red' ? 'bg-red-100 text-red-800' :
                            status.color === 'orange' ? 'bg-orange-100 text-orange-800' :
                            status.color === 'green' ? 'bg-green-100 text-green-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {status.label}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center">
              <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune donnée disponible</p>
            </div>
          )}
        </div>
      </section>

      {/* Top Zones */}
      {topZones && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Zones les plus occupées */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-red-600" />
              Zones les Plus Occupées
            </h4>
            <div className="space-y-3">
              {topZones.plus_occupees?.map((zone, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{zone.nom_zone}</p>
                      <p className="text-xs text-gray-500">
                        {formatNumber(zone.lots_attribues)} / {formatNumber(zone.nombre_total_lots)} lots
                      </p>
                    </div>
                  </div>
                  <span className="text-lg font-bold text-red-600">
                    {formatPercent(zone.taux_occupation_pct)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Zones les moins occupées */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingDown className="w-5 h-5 mr-2 text-blue-600" />
              Zones les Moins Occupées
            </h4>
            <div className="space-y-3">
              {topZones.moins_occupees?.map((zone, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{zone.nom_zone}</p>
                      <p className="text-xs text-gray-500">
                        {formatNumber(zone.lots_disponibles)} lots disponibles
                      </p>
                    </div>
                  </div>
                  <span className="text-lg font-bold text-blue-600">
                    {formatPercent(zone.taux_occupation_pct)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
