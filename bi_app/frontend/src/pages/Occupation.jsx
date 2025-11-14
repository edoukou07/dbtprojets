import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { 
  Building2, 
  MapPin, 
  TrendingUp, 
  TrendingDown, 
  Layers,
  AlertCircle,
  CheckCircle,
  Hash,
  ExternalLink,
  Search,
  X,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import { occupationAPI } from '../services/api'
import StatsCard from '../components/StatsCard'

export default function Occupation() {
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)
  const [sortField, setSortField] = useState('nom_zone')
  const [sortDirection, setSortDirection] = useState('asc')

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['occupation-summary'],
    queryFn: () => occupationAPI.getSummary().then(res => res.data),
  })

  const { data: allZonesData, isLoading: zonesLoading } = useQuery({
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

  // Tri des zones (sans filtrage)
  const sortedZones = useMemo(() => {
    if (!allZonesData || allZonesData.length === 0) return []
    
    const sorted = [...allZonesData].sort((a, b) => {
      let aValue, bValue
      
      switch (sortField) {
        case 'nom_zone':
          aValue = a.nom_zone || ''
          bValue = b.nom_zone || ''
          return sortDirection === 'asc' 
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue)
        
        case 'taux_occupation_pct':
          aValue = parseFloat(a.taux_occupation_pct) || 0
          bValue = parseFloat(b.taux_occupation_pct) || 0
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
        
        case 'nombre_total_lots':
          aValue = parseInt(a.nombre_total_lots) || 0
          bValue = parseInt(b.nombre_total_lots) || 0
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
        
        case 'lots_attribues':
          aValue = parseInt(a.lots_attribues) || 0
          bValue = parseInt(b.lots_attribues) || 0
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
        
        case 'lots_disponibles':
          aValue = parseInt(a.lots_disponibles) || 0
          bValue = parseInt(b.lots_disponibles) || 0
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
        
        case 'superficie_totale':
          aValue = parseFloat(a.superficie_totale) || 0
          bValue = parseFloat(b.superficie_totale) || 0
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
        
        default:
          return 0
      }
    })
    
    return sorted
  }, [allZonesData, sortField, sortDirection])

  // Calculs de pagination
  const totalPages = Math.ceil(sortedZones.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const zonesData = sortedZones.slice(startIndex, endIndex)

  // Fonction pour gérer le tri
  const handleSort = (field) => {
    if (sortField === field) {
      // Si on clique sur la même colonne, inverser la direction
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      // Nouvelle colonne, tri ascendant par défaut
      setSortField(field)
      setSortDirection('asc')
    }
  }

  // Icône de tri pour les en-têtes
  const SortIcon = ({ field }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-4 h-4 opacity-40" />
    }
    return sortDirection === 'asc' 
      ? <ArrowUp className="w-4 h-4" />
      : <ArrowDown className="w-4 h-4" />
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

        {/* Jauge du Taux d'Occupation Moyen */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-6 text-center">
            Taux d'Occupation Moyen
          </h4>
          <div className="flex flex-col items-center">
            {/* Gauge SVG */}
            <svg width="300" height="180" viewBox="0 0 300 180" className="mb-4">
              {/* Background arc (gris clair) */}
              <path
                d="M 40 150 A 110 110 0 0 1 260 150"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="30"
                strokeLinecap="round"
              />

              {/* Active arc based on occupation rate */}
              <path
                d={(() => {
                  const rate = summary?.taux_occupation_moyen || 0;
                  const angle = (rate / 100) * 180 - 180;
                  const radians = (angle * Math.PI) / 180;
                  const x = 150 + 110 * Math.cos(radians);
                  const y = 150 + 110 * Math.sin(radians);
                  const largeArc = rate > 50 ? 1 : 0;
                  return `M 40 150 A 110 110 0 ${largeArc} 1 ${x} ${y}`;
                })()}
                fill="none"
                stroke={(() => {
                  const rate = summary?.taux_occupation_moyen || 0;
                  if (rate >= 90) return '#ef4444';
                  if (rate >= 70) return '#f59e0b';
                  if (rate >= 50) return '#10b981';
                  return '#3b82f6';
                })()}
                strokeWidth="30"
                strokeLinecap="round"
              />

              {/* Center text - percentage */}
              <text
                x="150"
                y="130"
                textAnchor="middle"
                className="text-5xl font-bold"
                fill="#111827"
              >
                {formatPercent(summary?.taux_occupation_moyen)}
              </text>
              <text
                x="150"
                y="155"
                textAnchor="middle"
                className="text-sm"
                fill="#6b7280"
              >
                {(() => {
                  const rate = summary?.taux_occupation_moyen || 0;
                  if (rate >= 90) return 'Critique';
                  if (rate >= 70) return 'Élevée';
                  if (rate >= 50) return 'Normale';
                  return 'Faible';
                })()}
              </text>
            </svg>

            {/* Legend */}
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-blue-500 mr-2"></div>
                <span className="text-gray-600">Faible (&lt; 50%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
                <span className="text-gray-600">Normale (50-70%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-orange-500 mr-2"></div>
                <span className="text-gray-600">Élevée (70-90%)</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
                <span className="text-gray-600">Critique (&gt; 90%)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Cards - Zones Saturées et Sous-Occupées */}
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

      {/* Top Zones - Histogramme */}
      {topZones && (
        <section>
          <div className="grid grid-cols-1 gap-6">
            {/* Zones les moins occupées - Histogramme */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                <TrendingDown className="w-5 h-5 mr-2 text-blue-600" />
                Zones les Moins Occupées
              </h4>
              <div className="space-y-4">
                {topZones.moins_occupees?.slice(0, 5).map((zone, index) => {
                  const percentage = parseFloat(zone.taux_occupation_pct) || 0
                  const colors = [
                    { bg: 'bg-blue-500', border: 'border-blue-600' },
                    { bg: 'bg-blue-400', border: 'border-blue-500' },
                    { bg: 'bg-blue-300', border: 'border-blue-400' },
                    { bg: 'bg-blue-200', border: 'border-blue-300' },
                    { bg: 'bg-blue-100', border: 'border-blue-200' }
                  ]
                  
                  return (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-800 text-xs font-bold">
                            {index + 1}
                          </span>
                          <span className="font-medium text-gray-900">{zone.nom_zone}</span>
                        </div>
                        <span className="font-semibold text-blue-600">{formatPercent(percentage)}</span>
                      </div>
                      <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                        <div
                          className={`h-full ${colors[index].bg} ${colors[index].border} border-r-2 transition-all duration-500 flex items-center justify-end pr-3`}
                          style={{ width: `${percentage}%` }}
                        >
                          {percentage > 15 && (
                            <span className="text-xs font-semibold text-white drop-shadow-sm">
                              {formatPercent(percentage)}
                            </span>
                          )}
                        </div>
                        {percentage <= 15 && (
                          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-gray-600">
                            {formatPercent(percentage)}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{zone.lots_attribues || 0} lots attribués</span>
                        <span>{zone.lots_disponibles || 0} lots disponibles</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Tableau des Zones */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Hash className="w-6 h-6 mr-2 text-blue-600" />
          Détails par Zone
        </h3>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Top 5 des Zones */}
          {topZones && topZones.plus_occupees && topZones.plus_occupees.length > 0 && (
            <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
                Top 5 des Zones les Plus Occupées
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {topZones.plus_occupees.slice(0, 5).map((zone, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 shadow-sm border border-blue-100 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-2">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-sm">
                        {index + 1}
                      </div>
                      <span className="text-lg font-bold text-blue-600">
                        {formatPercent(zone.taux_occupation_pct)}
                      </span>
                    </div>
                    <Link
                      to={`/occupation/zone/${encodeURIComponent(zone.nom_zone)}`}
                      className="text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors line-clamp-2"
                    >
                      {zone.nom_zone}
                    </Link>
                    <div className="mt-2 text-xs text-gray-500">
                      {formatNumber(zone.lots_attribues)} / {formatNumber(zone.nombre_total_lots)} lots
                    </div>
                    {/* Barre de progression */}
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(parseFloat(zone.taux_occupation_pct) || 0, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Nombre de résultats et contrôles de pagination */}
          {!zonesLoading && (
            <div className="flex items-center justify-between py-4 px-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Afficher:</label>
                <select
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value))
                    setCurrentPage(1)
                  }}
                  className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                </select>
                <span className="text-sm text-gray-600">par page</span>
              </div>
              
              <p className="text-lg font-semibold text-gray-900">
                {sortedZones.length} {sortedZones.length > 1 ? 'zones' : 'zone'}
              </p>
              
              <div className="text-sm text-gray-600">
                {sortedZones.length > 0 && (
                  <>Affichage {startIndex + 1}-{Math.min(endIndex, sortedZones.length)} sur {sortedZones.length}</>
                )}
              </div>
            </div>
          )}

          {zonesLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-500 mt-4">Chargement des données...</p>
            </div>
          ) : zonesData && zonesData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gradient-to-r from-blue-600 to-blue-700">
                  <tr>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:bg-blue-800 transition-colors"
                      onClick={() => handleSort('nom_zone')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Zone</span>
                        <SortIcon field="nom_zone" />
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:bg-blue-800 transition-colors"
                      onClick={() => handleSort('taux_occupation_pct')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Taux Occupation</span>
                        <SortIcon field="taux_occupation_pct" />
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:bg-blue-800 transition-colors"
                      onClick={() => handleSort('nombre_total_lots')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Lots Total</span>
                        <SortIcon field="nombre_total_lots" />
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:bg-blue-800 transition-colors"
                      onClick={() => handleSort('lots_attribues')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Attribués</span>
                        <SortIcon field="lots_attribues" />
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:bg-blue-800 transition-colors"
                      onClick={() => handleSort('lots_disponibles')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Disponibles</span>
                        <SortIcon field="lots_disponibles" />
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer hover:bg-blue-800 transition-colors"
                      onClick={() => handleSort('superficie_totale')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Superficie</span>
                        <SortIcon field="superficie_totale" />
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
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
              <p className="text-gray-500">
                {hasActiveFilters 
                  ? 'Aucune zone ne correspond aux filtres sélectionnés' 
                  : 'Aucune donnée disponible'}
              </p>
              {hasActiveFilters && (
                <button
                  onClick={resetFilters}
                  className="mt-2 text-blue-600 hover:text-blue-800 text-sm inline-flex items-center gap-1"
                >
                  <X className="w-4 h-4" />
                  Réinitialiser les filtres
                </button>
              )}
            </div>
          )}
        </div>
      </section>
      
      {/* Pagination pour zones */}
      {!zonesLoading && sortedZones.length > 0 && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-white sm:px-6">
          <div className="flex justify-between items-center w-full">
            <div className="text-sm text-gray-700">
              Page <span className="font-medium">{currentPage}</span> sur{' '}
              <span className="font-medium">{totalPages}</span>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className={`px-3 py-1 rounded-lg flex items-center gap-1 ${
                  currentPage === 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                <ChevronLeft className="w-4 h-4" />
                Précédent
              </button>
              
              {/* Numéros de page */}
              <div className="flex gap-1">
                {[...Array(totalPages)].map((_, idx) => {
                  const pageNum = idx + 1
                  if (
                    pageNum === 1 ||
                    pageNum === totalPages ||
                    (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                  ) {
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`px-3 py-1 rounded-lg ${
                          currentPage === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  } else if (pageNum === currentPage - 2 || pageNum === currentPage + 2) {
                    return <span key={pageNum} className="px-2 py-1">...</span>
                  }
                  return null
                })}
              </div>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className={`px-3 py-1 rounded-lg flex items-center gap-1 ${
                  currentPage === totalPages
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                Suivant
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
