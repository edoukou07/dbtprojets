import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { 
  Users, TrendingUp, Target, Award, Clock, DollarSign,
  UserCheck, AlertCircle, Activity, BarChart3
} from 'lucide-react'
import rhAPI from '../services/rhAPI'
import StatsCard from '../components/StatsCard'
import ExportButton from '../components/ExportButton'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']

export default function RH() {
  const [selectedMetric, setSelectedMetric] = useState('montant_recouvre')
  const [topLimit, setTopLimit] = useState(10)

  // Requêtes API
  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ['rh-agents-productivite'],
    queryFn: () => rhAPI.getAgentsProductivite().then(res => res.data),
  })

  const { data: topAgents } = useQuery({
    queryKey: ['rh-top-agents', topLimit, selectedMetric],
    queryFn: () => rhAPI.getTopAgents(topLimit, selectedMetric).then(res => res.data),
  })

  const { data: performanceByType } = useQuery({
    queryKey: ['rh-performance-by-type'],
    queryFn: () => rhAPI.getPerformanceByType().then(res => res.data),
  })

  const { data: collectesAnalysis } = useQuery({
    queryKey: ['rh-collectes-analysis'],
    queryFn: () => rhAPI.getCollectesAnalysis().then(res => res.data),
  })

  const { data: efficiencyMetrics } = useQuery({
    queryKey: ['rh-efficiency-metrics'],
    queryFn: () => rhAPI.getEfficiencyMetrics().then(res => res.data),
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
    return value.toFixed(1) + '%'
  }

  const summary = agentsData?.summary || {}

  // Préparer les données pour les graphiques
  const typeAgentLabels = {
    1: 'Type 1',
    2: 'Type 2',
    3: 'Type 3',
    4: 'Type 4',
    5: 'Type 5'
  }

  const performanceTypeData = performanceByType?.performance_by_type?.map(item => ({
    ...item,
    type_label: typeAgentLabels[item.type_agent_id] || `Type ${item.type_agent_id}`,
    montant_recouvre_display: item.total_montant_recouvre || 0
  })) || []

  const distributionRangesData = collectesAnalysis?.distribution_by_ranges || []

  const performanceLevelsData = efficiencyMetrics?.performance_levels || []

  // Préparer données pour export
  const prepareExportData = () => {
    const data = []
    
    if (summary) {
      data.push({
        'Métrique': 'Nombre d\'agents',
        'Valeur': summary.total_agents || 0
      })
      data.push({
        'Métrique': 'Total collectes',
        'Valeur': summary.total_collectes || 0
      })
      data.push({
        'Métrique': 'Montant recouvré',
        'Valeur': formatCurrency(summary.montant_total_recouvre)
      })
      data.push({
        'Métrique': 'Taux recouvrement moyen',
        'Valeur': formatPercent(summary.taux_recouvrement_moyen)
      })
    }

    if (topAgents?.top_agents) {
      data.push({ 'Métrique': '', 'Valeur': '' })
      data.push({ 'Métrique': 'TOP AGENTS', 'Valeur': '' })
      topAgents.top_agents.forEach((agent, index) => {
        data.push({
          'Métrique': `${index + 1}. ${agent.nom_complet}`,
          'Valeur': formatCurrency(agent.montant_total_recouvre)
        })
      })
    }

    return data
  }

  const metricOptions = [
    { value: 'montant_recouvre', label: 'Montant recouvré' },
    { value: 'taux_recouvrement', label: 'Taux de recouvrement' },
    { value: 'nombre_collectes', label: 'Nombre de collectes' },
    { value: 'taux_cloture', label: 'Taux de clôture' }
  ]

  if (agentsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des données RH...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ressources Humaines</h1>
          <p className="text-gray-600 mt-1">Tableau de bord de productivité des agents</p>
        </div>
        <ExportButton 
          data={prepareExportData()} 
          filename="rh_productivite_agents"
        />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Agents"
          value={summary.total_agents || 0}
          icon={Users}
          trend={null}
          color="blue"
        />
        <StatsCard
          title="Total Collectes"
          value={summary.total_collectes || 0}
          icon={Activity}
          trend={null}
          color="green"
        />
        <StatsCard
          title="Montant Recouvré"
          value={formatCurrencyShort(summary.montant_total_recouvre)}
          subtitle={formatCurrency(summary.montant_total_recouvre)}
          icon={DollarSign}
          trend={null}
          color="purple"
        />
        <StatsCard
          title="Taux Recouvrement"
          value={formatPercent(summary.taux_recouvrement_moyen)}
          icon={Target}
          trend={null}
          color="orange"
        />
      </div>

      {/* Métriques d'efficacité */}
      {efficiencyMetrics?.global_metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <p className="text-sm text-gray-600">Délai Moyen Traitement</p>
                <p className="text-2xl font-bold text-gray-900">
                  {efficiencyMetrics.global_metrics.delai_moyen_global?.toFixed(1) || 0} jours
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-green-600 mr-3" />
              <div>
                <p className="text-sm text-gray-600">Montant Moyen / Collecte</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrencyShort(efficiencyMetrics.global_metrics.montant_moyen_collecte_global)}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <UserCheck className="h-8 w-8 text-purple-600 mr-3" />
              <div>
                <p className="text-sm text-gray-600">Taux Clôture Global</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatPercent(efficiencyMetrics.global_metrics.taux_cloture_global)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Agents */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Award className="h-6 w-6 text-yellow-500 mr-2" />
            Top Agents
          </h2>
          <div className="flex gap-4">
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {metricOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <select
              value={topLimit}
              onChange={(e) => setTopLimit(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={15}>Top 15</option>
              <option value={20}>Top 20</option>
            </select>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={topAgents?.top_agents || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="nom_complet" 
              angle={-45}
              textAnchor="end"
              height={120}
              fontSize={12}
            />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => {
                if (name.includes('montant')) return formatCurrency(value)
                if (name.includes('taux')) return formatPercent(value)
                return value
              }}
            />
            <Legend />
            {selectedMetric === 'montant_recouvre' && (
              <Bar dataKey="montant_total_recouvre" name="Montant recouvré" fill="#0ea5e9" />
            )}
            {selectedMetric === 'taux_recouvrement' && (
              <Bar dataKey="taux_recouvrement_moyen_pct" name="Taux recouvrement (%)" fill="#10b981" />
            )}
            {selectedMetric === 'nombre_collectes' && (
              <Bar dataKey="nombre_collectes" name="Nombre collectes" fill="#f59e0b" />
            )}
            {selectedMetric === 'taux_cloture' && (
              <Bar dataKey="taux_cloture_pct" name="Taux clôture (%)" fill="#8b5cf6" />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Performance par type d'agent */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <BarChart3 className="h-6 w-6 text-blue-600 mr-2" />
            Performance par Type d'Agent
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type_label" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrencyShort(value)} />
              <Legend />
              <Bar dataKey="montant_recouvre_display" name="Montant recouvré" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <Activity className="h-6 w-6 text-green-600 mr-2" />
            Niveaux de Performance
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={performanceLevelsData}
                dataKey="nombre_agents"
                nameKey="niveau_performance"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(entry) => `${entry.niveau_performance}: ${entry.nombre_agents}`}
              >
                {performanceLevelsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Distribution des collectes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Distribution des Collectes</h2>
          {collectesAnalysis?.distribution && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Total Collectes</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {collectesAnalysis.distribution.total_collectes || 0}
                  </p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Collectes Clôturées</p>
                  <p className="text-2xl font-bold text-green-600">
                    {collectesAnalysis.distribution.total_cloturees || 0}
                  </p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Collectes Ouvertes</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {collectesAnalysis.distribution.total_ouvertes || 0}
                  </p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Taux Clôture</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {formatPercent(collectesAnalysis.distribution.taux_cloture_moyen)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Recouvrement Global</h2>
          {collectesAnalysis?.recouvrement && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Montant à Recouvrer</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(collectesAnalysis.recouvrement.montant_total_a_recouvrer)}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Montant Recouvré</p>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(collectesAnalysis.recouvrement.montant_total_recouvre)}
                </p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Taux de Recouvrement Global</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatPercent(collectesAnalysis.recouvrement.taux_recouvrement_global)}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Distribution par ranges de collectes */}
      {distributionRangesData.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Distribution des Agents par Nombre de Collectes
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distributionRangesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range_collectes" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="nombre_agents" name="Nombre d'agents" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Table des agents */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Liste des Agents</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Matricule
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Collectes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Montant Recouvré
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Taux Recouvrement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rang
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {agentsData?.agents?.slice(0, 20).map((agent) => (
                <tr key={agent.agent_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{agent.nom_complet}</div>
                    <div className="text-sm text-gray-500">{agent.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {agent.matricule}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {agent.nombre_collectes || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrencyShort(agent.montant_total_recouvre)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      (agent.taux_recouvrement_moyen_pct || 0) >= 60 
                        ? 'bg-green-100 text-green-800'
                        : (agent.taux_recouvrement_moyen_pct || 0) >= 40
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {formatPercent(agent.taux_recouvrement_moyen_pct)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    #{agent.rang_productivite_global}
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
