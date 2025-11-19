import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts'
import { 
  Users, DollarSign, TrendingUp, AlertTriangle, 
  Award, Target, Activity, Building2, MapPin,
  CheckCircle, XCircle, Clock, BarChart3, ExternalLink
} from 'lucide-react'
import { clientsAPI } from '../services/api'
import StatsCard from '../components/StatsCard'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']
const RISK_COLORS = {
  'Risque faible': '#10b981',
  'Risque moyen': '#f59e0b',
  'Risque élevé': '#ef4444'
}

export default function Portefeuille() {
  const [selectedSegment, setSelectedSegment] = useState('all')
  const [topClientsPage, setTopClientsPage] = useState(0)
  const itemsPerPage = 10
  
  // Requêtes API
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['clients-summary'],
    queryFn: () => clientsAPI.getSummary().then(res => res.data),
  })

  const { data: segmentation } = useQuery({
    queryKey: ['clients-segmentation'],
    queryFn: () => clientsAPI.getSegmentation().then(res => res.data),
  })

  const { data: topClients } = useQuery({
    queryKey: ['clients-top'],
    queryFn: () => clientsAPI.getTopClients(10).then(res => res.data),
  })

  const { data: atRisk } = useQuery({
    queryKey: ['clients-at-risk'],
    queryFn: () => clientsAPI.getAtRisk().then(res => res.data),
  })

  const { data: comportement } = useQuery({
    queryKey: ['clients-comportement'],
    queryFn: () => clientsAPI.getAnalyseComportement().then(res => res.data),
  })

  const { data: occupation } = useQuery({
    queryKey: ['clients-occupation'],
    queryFn: () => clientsAPI.getAnalyseOccupation().then(res => res.data),
  })

  const formatCurrency = (value) => {
    if (!value && value !== 0) return '0 FCFA'
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value) + ' FCFA'
  }

  const formatCurrencyShort = (value) => {
    if (!value && value !== 0) return '0'
    return new Intl.NumberFormat('fr-FR', { 
      notation: 'compact',
      compactDisplay: 'short'
    }).format(value)
  }

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0%'
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0%'
    return numValue.toFixed(1) + '%'
  }

  const getSegmentColor = (segment) => {
    const colors = {
      'Premium': '#9333ea',      // Violet plus intense
      'VIP': '#f43f5e',          // Rose/Rouge vif
      'Standard': '#0284c7',      // Bleu profond
      'Basique': '#f59e0b',       // Orange doré
      'Nouveau': '#10b981'        // Vert émeraude (au cas où)
    }
    return colors[segment] || '#64748b'
  }

  return (
    <div className="space-y-8">
      {/* En-tête avec bouton */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Portefeuille Clients</h2>
          <p className="text-gray-600 mt-1">Analyse et segmentation du portefeuille</p>
        </div>
        <Link
          to="/clients"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
        >
          <Users className="w-5 h-5" />
          Liste des Clients
          <ExternalLink className="w-4 h-4" />
        </Link>
      </div>

      {/* KPIs Principaux - ONLY unique client metrics */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Users className="w-6 h-6 mr-2 text-blue-600" />
          Vue d'Ensemble du Portefeuille
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Clients"
            value={summary?.total_clients?.toLocaleString('fr-FR') || '0'}
            subtitle="Entreprises actives"
            icon={Users}
            color="blue"
            loading={summaryLoading}
          />
          <StatsCard
            title="Créances Totales"
            value={formatCurrencyShort(summary?.ca_impaye) + ' FCFA'}
            subtitle={formatPercent(summary?.taux_impaye_pct) + ' du CA'}
            icon={AlertTriangle}
            color="orange"
            loading={summaryLoading}
          />
          <StatsCard
            title="Délai Moyen Paiement"
            value={`${Math.round(summary?.delai_moyen_paiement || 0)} jours`}
            subtitle="Moyenne par client"
            icon={Clock}
            color="purple"
            loading={summaryLoading}
          />
          <StatsCard
            title="Factures en Retard"
            value={summary?.factures_retard_total?.toLocaleString('fr-FR') || '0'}
            subtitle="À relancer"
            icon={XCircle}
            color="red"
            loading={summaryLoading}
          />
        </div>
      </section>

      {/* Segmentation et Risque */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Segmentation Clients */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Award className="w-5 h-5 mr-2 text-blue-600" />
            Segmentation du Portefeuille
          </h4>
          {segmentation?.par_segment && segmentation.par_segment.length > 0 ? (
            <div className="space-y-4">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={segmentation.par_segment}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ segment_client, nombre_clients }) => 
                      `${segment_client}: ${nombre_clients}`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="nombre_clients"
                  >
                    {segmentation.par_segment.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={getSegmentColor(entry.segment_client)} 
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name, props) => [
                    `${value} clients - ${formatCurrency(props.payload.ca_total)}`,
                    props.payload.segment_client
                  ]} />
                </PieChart>
              </ResponsiveContainer>
              
              <div className="space-y-2">
                {segmentation.par_segment.map((segment, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: getSegmentColor(segment.segment_client) }}
                      ></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{segment.segment_client}</p>
                        <p className="text-xs text-gray-500">
                          {segment.nombre_clients} clients • Taux: {formatPercent(segment.taux_paiement_moyen)}
                        </p>
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-gray-700">
                      {formatCurrencyShort(segment.ca_total)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              Aucune donnée disponible
            </div>
          )}
        </div>

        {/* Analyse de Risque */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
            Répartition par Niveau de Risque
          </h4>
          {segmentation?.par_niveau_risque && segmentation.par_niveau_risque.length > 0 ? (
            <div className="space-y-4">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={segmentation.par_niveau_risque} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="niveau_risque" type="category" width={100} />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'nombre_clients' ? `${value} clients` : formatCurrency(value),
                      name === 'nombre_clients' ? 'Clients' : 'Créances'
                    ]}
                  />
                  <Bar dataKey="nombre_clients" fill="#0ea5e9" name="Clients" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
              
              <div className="space-y-2">
                {segmentation.par_niveau_risque.map((risque, index) => (
                  <div key={index} className="p-3 rounded-lg border-l-4" style={{
                    borderLeftColor: RISK_COLORS[risque.niveau_risque] || '#64748b',
                    backgroundColor: `${RISK_COLORS[risque.niveau_risque] || '#64748b'}10`
                  }}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-gray-900">
                        {risque.niveau_risque}
                      </span>
                      <span className="text-sm font-bold" style={{
                        color: RISK_COLORS[risque.niveau_risque] || '#64748b'
                      }}>
                        {risque.nombre_clients} clients
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <span>CA: {formatCurrencyShort(risque.ca_total)}</span>
                      <span>Créances: {formatCurrencyShort(risque.ca_impaye)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              Aucune donnée disponible
            </div>
          )}
        </div>
      </div>

      {/* Comportement de Paiement */}
      {comportement?.par_taux_paiement && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-blue-600" />
              Analyse du Comportement de Paiement
            </h4>

            {/* Cartes récapitulatives par catégorie */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {comportement.par_taux_paiement.map((cat, idx) => {
                const colors = ['bg-green-50 border-green-200', 'bg-blue-50 border-blue-200', 'bg-yellow-50 border-yellow-200', 'bg-red-50 border-red-200'];
                const icons = ['text-green-600', 'text-blue-600', 'text-yellow-600', 'text-red-600'];
                
                return (
                  <div key={idx} className={`rounded-lg border p-4 ${colors[idx]}`}>
                    <div className={`text-sm font-medium ${icons[idx]} mb-2`}>{cat.categorie}</div>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-600">Clients:</span>
                        <span className="font-semibold text-gray-900">{cat.count || 0}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-600">CA:</span>
                        <span className="font-semibold text-gray-900">{formatCurrency(cat.ca_total || 0)}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-600">Délai moyen:</span>
                        <span className="font-semibold text-gray-900">{cat.delai_moyen || 0}j</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Graphe: Nombre de clients par catégorie */}
            <div className="mb-8">
              <h5 className="text-sm font-medium text-gray-700 mb-4">Répartition des Clients par Taux de Paiement</h5>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={comportement.par_taux_paiement}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="categorie" angle={-15} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
                  <YAxis label={{ value: 'Nombre de clients', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    formatter={(value) => [`${value} clients`, 'Nombre']}
                  />
                  <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* Délai de Paiement */}
          {comportement.par_delai_paiement && comportement.par_delai_paiement.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-6">Distribution par Délai de Paiement</h4>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Graphe: Clients par délai */}
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-4">Nombre de Clients</h5>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={comportement.par_delai_paiement}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="plage_delai" angle={-15} textAnchor="end" height={60} tick={{ fontSize: 11 }} />
                      <YAxis label={{ value: 'Clients', angle: -90, position: 'insideLeft' }} />
                      <Tooltip formatter={(value) => [`${value} clients`, 'Nombre']} />
                      <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Graphe: Taux moyen par délai */}
                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-4">Taux de Paiement Moyen</h5>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={comportement.par_delai_paiement}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="plage_delai" angle={-15} textAnchor="end" height={60} tick={{ fontSize: 11 }} />
                      <YAxis label={{ value: 'Taux (%)', angle: -90, position: 'insideLeft' }} />
                      <Tooltip formatter={(value) => [formatPercent(value), 'Taux moyen']} />
                      <Bar dataKey="taux_paiement_moyen" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Top Clients et Clients à Risque */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Clients */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 flex items-center">
              <Award className="w-5 h-5 mr-2 text-blue-600" />
              Top Clients par CA
            </h4>
            <p className="text-sm text-gray-600 mt-1">
              Total: {topClients?.top_chiffre_affaires?.length || 0} clients
            </p>
          </div>
          <div className="overflow-x-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">CA Total</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Taux Paiement</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Segment</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topClients?.top_chiffre_affaires?.slice(
                  topClientsPage * itemsPerPage,
                  (topClientsPage + 1) * itemsPerPage
                ).map((client, index) => (
                  <tr key={client.entreprise_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                        {topClientsPage * itemsPerPage + index + 1}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{client.raison_sociale}</p>
                        <p className="text-xs text-gray-500">{client.secteur_activite || 'N/A'}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {formatCurrency(client.chiffre_affaires_total)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        client.taux_paiement_pct >= 90 ? 'bg-green-100 text-green-800' :
                        client.taux_paiement_pct >= 70 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {formatPercent(client.taux_paiement_pct)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      <span 
                        className="px-2 py-1 rounded text-xs font-medium text-white"
                        style={{ backgroundColor: getSegmentColor(client.segment_client) }}
                      >
                        {client.segment_client || 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Pagination */}
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {topClients?.top_chiffre_affaires?.length > 0 ? (
                <>
                  {topClientsPage * itemsPerPage + 1} à{' '}
                  {Math.min((topClientsPage + 1) * itemsPerPage, topClients.top_chiffre_affaires.length)}{' '}
                  sur {topClients.top_chiffre_affaires.length}
                </>
              ) : (
                'Aucun client'
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setTopClientsPage(Math.max(0, topClientsPage - 1))}
                disabled={topClientsPage === 0}
                className="px-3 py-1 rounded border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ← Précédent
              </button>
              <button
                onClick={() => setTopClientsPage(topClientsPage + 1)}
                disabled={(topClientsPage + 1) * itemsPerPage >= (topClients?.top_chiffre_affaires?.length || 0)}
                className="px-3 py-1 rounded border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Suivant →
              </button>
            </div>
          </div>
        </div>

        {/* Clients à Risque */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
              Clients à Risque ({atRisk?.nombre_total || 0})
            </h4>
            {atRisk?.total_creances && (
              <p className="text-sm text-gray-600 mt-1">
                Créances totales: {formatCurrency(atRisk.total_creances)}
              </p>
            )}
          </div>
          <div className="overflow-x-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-red-50 sticky top-0">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Créances</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Taux Paiement</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risque</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {atRisk?.clients_a_risque?.slice(0, 10).map((client) => (
                  <tr key={client.entreprise_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{client.raison_sociale}</p>
                        <p className="text-xs text-gray-500">{client.secteur_activite || 'N/A'}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-red-600">
                      {formatCurrency(client.ca_impaye)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        {formatPercent(client.taux_paiement_pct)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span 
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        style={{
                          backgroundColor: `${RISK_COLORS[client.niveau_risque] || '#64748b'}20`,
                          color: RISK_COLORS[client.niveau_risque] || '#64748b'
                        }}
                      >
                        {client.niveau_risque || 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Analyse Occupation des Lots */}
      {occupation && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
            <Building2 className="w-5 h-5 mr-2 text-blue-600" />
            Analyse de l'Occupation des Lots Industriels
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <CheckCircle className="w-8 h-8 text-blue-600" />
                <span className="text-2xl font-bold text-blue-600">
                  {occupation.avec_lots?.nombre_clients || 0}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-700">Clients avec Lots</p>
              <p className="text-xs text-gray-600 mt-1">
                {occupation.avec_lots?.total_lots || 0} lots • {occupation.avec_lots?.superficie_totale?.toLocaleString('fr-FR') || 0} m²
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <XCircle className="w-8 h-8 text-gray-600" />
                <span className="text-2xl font-bold text-gray-600">
                  {occupation.sans_lots?.nombre_clients || 0}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-700">Clients sans Lots</p>
              <p className="text-xs text-gray-600 mt-1">
                Prospects potentiels
              </p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center justify-between mb-2">
                <DollarSign className="w-8 h-8 text-green-600" />
                <span className="text-2xl font-bold text-green-600">
                  {formatCurrencyShort(occupation.avec_lots?.ca_moyen)}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-700">CA Moyen (avec lots)</p>
              <p className="text-xs text-gray-600 mt-1">
                Par client occupant
              </p>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
              <div className="flex items-center justify-between mb-2">
                <DollarSign className="w-8 h-8 text-orange-600" />
                <span className="text-2xl font-bold text-orange-600">
                  {formatCurrencyShort(occupation.sans_lots?.ca_moyen)}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-700">CA Moyen (sans lots)</p>
              <p className="text-xs text-gray-600 mt-1">
                Par client non-occupant
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Secteurs d'Activité */}
      {segmentation?.par_secteur && segmentation.par_secteur.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
            Top Secteurs d'Activité
          </h4>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={segmentation.par_secteur} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis 
                dataKey="secteur_activite" 
                type="category" 
                width={200}
                tick={{ fontSize: 12 }}
              />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'nombre_clients' ? `${value} clients` : formatCurrency(value),
                  name === 'nombre_clients' ? 'Clients' : 'Chiffre d\'Affaires'
                ]}
              />
              <Legend />
              <Bar dataKey="nombre_clients" fill="#0ea5e9" name="Nombre de clients" radius={[0, 8, 8, 0]} />
              <Bar dataKey="ca_total" fill="#10b981" name="CA Total" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
