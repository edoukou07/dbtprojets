import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar, AreaChart, Area
} from 'recharts'
import api from '../services/api'

// Couleurs pour les graphiques
const COLORS = {
  primary: '#3b82f6',
  success: '#22c55e',
  warning: '#eab308',
  danger: '#ef4444',
  info: '#06b6d4',
  purple: '#8b5cf6',
  orange: '#f97316',
  gray: '#6b7280'
}

const ALERT_COLORS = {
  'CRITIQUE': '#ef4444',
  'ALERTE': '#f97316',
  'ATTENTION': '#eab308',
  'NORMAL': '#22c55e',
  'TERMINE': '#6b7280'
}

// Composant KPI Card
const KPICard = ({ title, value, subtitle, icon, color = 'blue', trend }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200'
  }

  return (
    <div className={`rounded-xl border p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs mt-1 opacity-60">{subtitle}</p>}
        </div>
        {icon && <div className="text-3xl opacity-50">{icon}</div>}
      </div>
      {trend && (
        <div className={`text-xs mt-2 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs période précédente
        </div>
      )}
    </div>
  )
}

// Composant Score Gauge
const ScoreGauge = ({ score, label }) => {
  const getColor = (s) => {
    if (s >= 80) return '#22c55e'
    if (s >= 60) return '#84cc16'
    if (s >= 40) return '#eab308'
    return '#ef4444'
  }

  const data = [{ name: label, value: score, fill: getColor(score) }]

  return (
    <div className="text-center">
      <ResponsiveContainer width="100%" height={120}>
        <RadialBarChart 
          cx="50%" 
          cy="50%" 
          innerRadius="60%" 
          outerRadius="100%" 
          data={data}
          startAngle={180}
          endAngle={0}
        >
          <RadialBar
            minAngle={15}
            background
            clockWise
            dataKey="value"
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <p className="text-3xl font-bold" style={{ color: getColor(score) }}>{score}</p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  )
}

// Composant Table des dossiers critiques
const CriticalTable = ({ data }) => {
  if (!data || data.length === 0) {
    return <p className="text-gray-500 text-center py-4">Aucun dossier critique</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dossier</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Opérateur</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phase</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Durée (j)</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Alerte</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((item, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                {item.numero_dossier}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {item.nom_operateur?.substring(0, 20)}...
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {item.phase_actuelle_libelle?.replace('Phase ', 'P')}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {item.duree_totale_jours}
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  item.score_sante_dossier >= 80 ? 'bg-green-100 text-green-800' :
                  item.score_sante_dossier >= 60 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {item.score_sante_dossier}
                </span>
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <span 
                  className="px-2 py-1 text-xs rounded-full text-white"
                  style={{ backgroundColor: ALERT_COLORS[item.niveau_alerte] }}
                >
                  {item.niveau_alerte}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Impenses() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [summary, setSummary] = useState(null)
  const [byPhase, setByPhase] = useState([])
  const [byZone, setByZone] = useState([])
  const [byAlert, setByAlert] = useState([])
  const [byRole, setByRole] = useState([])
  const [slaData, setSlaData] = useState(null)
  const [performance, setPerformance] = useState(null)
  const [tempsPhase, setTempsPhase] = useState([])
  const [healthDist, setHealthDist] = useState([])
  const [criticalList, setCriticalList] = useState([])
  const [filters, setFilters] = useState({
    zone: '',
    phase: '',
    alerte: ''
  })

  // Fetch all data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [
          summaryRes,
          phaseRes,
          zoneRes,
          alertRes,
          roleRes,
          slaRes,
          perfRes,
          tempsRes,
          healthRes,
          criticalRes
        ] = await Promise.all([
          api.get('/impenses/summary/'),
          api.get('/impenses/by_phase/'),
          api.get('/impenses/by_zone/'),
          api.get('/impenses/by_alert_level/'),
          api.get('/impenses/by_role/'),
          api.get('/impenses/sla_compliance/'),
          api.get('/impenses/performance_metrics/'),
          api.get('/impenses/temps_par_phase/'),
          api.get('/impenses/health_distribution/'),
          api.get('/impenses/critical_list/')
        ])

        setSummary(summaryRes.data)
        setByPhase(phaseRes.data)
        setByZone(zoneRes.data)
        setByAlert(alertRes.data)
        setByRole(roleRes.data)
        setSlaData(slaRes.data)
        setPerformance(perfRes.data)
        setTempsPhase(tempsRes.data)
        setHealthDist(healthRes.data)
        setCriticalList(criticalRes.data)
      } catch (err) {
        console.error('Error fetching impenses data:', err)
        setError('Erreur lors du chargement des données')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [filters])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-600">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            📋 Tableau de Bord - Suivi des Impenses
          </h1>
          <p className="text-gray-500 mt-1">
            Vue consolidée du workflow des dossiers d'impenses
          </p>
        </div>
        <div className="text-sm text-gray-400">
          Dernière mise à jour: {new Date().toLocaleString('fr-FR')}
        </div>
      </div>

      {/* KPIs Row 1 - Volume */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <KPICard
          title="Total Dossiers"
          value={summary?.total_dossiers || 0}
          icon="📁"
          color="blue"
        />
        <KPICard
          title="En Cours"
          value={summary?.dossiers_en_cours || 0}
          icon="⏳"
          color="yellow"
        />
        <KPICard
          title="Clôturés"
          value={summary?.dossiers_clotures || 0}
          icon="✅"
          color="green"
        />
        <KPICard
          title="Critiques"
          value={summary?.dossiers_critiques || 0}
          icon="🚨"
          color="red"
        />
        <KPICard
          title="En Alerte"
          value={summary?.dossiers_en_alerte || 0}
          icon="⚠️"
          color="orange"
        />
        <KPICard
          title="En Retard"
          value={summary?.dossiers_en_retard || 0}
          icon="🐢"
          color="red"
        />
      </div>

      {/* KPIs Row 2 - Performance */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard
          title="Score Santé Moyen"
          value={`${summary?.score_sante_moyen || 0}/100`}
          icon="💪"
          color={summary?.score_sante_moyen >= 70 ? 'green' : summary?.score_sante_moyen >= 50 ? 'yellow' : 'red'}
        />
        <KPICard
          title="Taux First Pass"
          value={`${summary?.taux_first_pass_moyen || 0}%`}
          subtitle="Validé sans retour"
          icon="🎯"
          color="green"
        />
        <KPICard
          title="Durée Moyenne"
          value={`${summary?.duree_moyenne_jours || 0}j`}
          icon="📅"
          color="blue"
        />
        <KPICard
          title="Conformité SLA"
          value={`${summary?.taux_conformite_sla_moyen || 0}%`}
          icon="📊"
          color={summary?.taux_conformite_sla_moyen >= 80 ? 'green' : 'orange'}
        />
        <KPICard
          title="Actions Moy."
          value={summary?.nb_actions_moyen || 0}
          icon="🔄"
          color="purple"
        />
        <KPICard
          title="Allers-Retours Moy."
          value={summary?.nb_allers_retours_moyen || 0}
          icon="↩️"
          color="orange"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution par Phase */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">📊 Distribution par Phase</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byPhase}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="phase_actuelle" tickFormatter={(v) => `P${v}`} />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [value, name === 'count' ? 'Dossiers' : name]}
                labelFormatter={(label) => `Phase ${label}`}
              />
              <Legend />
              <Bar dataKey="count" name="Dossiers" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Distribution par Niveau d'Alerte */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">🚦 Niveaux d'Alerte</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={byAlert}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="count"
                nameKey="niveau_alerte"
                label={({ niveau_alerte, count }) => `${niveau_alerte}: ${count}`}
              >
                {byAlert.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || COLORS.gray} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Temps par Phase */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">⏱️ Temps Moyen par Phase (heures)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={tempsPhase} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="phase" type="category" width={100} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="heures" fill={COLORS.info} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Interventions par Rôle */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">👥 Interventions par Rôle</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={byRole}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="count"
                nameKey="role"
                label={({ role, percentage }) => `${role}: ${percentage}%`}
              >
                {byRole.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Distribution Santé */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">💚 Distribution Score Santé</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={healthDist}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="count"
                nameKey="category"
                label={({ category, count }) => `${count}`}
              >
                {healthDist.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* SLA Compliance */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">📋 Conformité SLA par Phase</h3>
          <div className="text-2xl font-bold text-blue-600">
            {slaData?.global_compliance || 0}% Global
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {slaData?.phases?.map((phase, idx) => (
            <div key={idx} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">{phase.phase}</span>
                <span className="text-xs text-gray-500">Max: {phase.sla_max_heures}h</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div 
                  className="h-4 rounded-full transition-all"
                  style={{ 
                    width: `${phase.taux}%`,
                    backgroundColor: phase.taux >= 80 ? COLORS.success : phase.taux >= 60 ? COLORS.warning : COLORS.danger
                  }}
                />
              </div>
              <div className="flex justify-between mt-1 text-xs text-gray-500">
                <span>{phase.respecte}/{phase.total} conformes</span>
                <span className="font-semibold">{phase.taux}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics */}
      {performance && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">📈 Métriques de Performance</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{performance.duree_moyenne_jours}j</p>
              <p className="text-xs text-gray-500">Durée moyenne</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">{performance.actions_moyennes}</p>
              <p className="text-xs text-gray-500">Actions/dossier</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-cyan-600">{performance.agents_moyens}</p>
              <p className="text-xs text-gray-500">Agents/dossier</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-600">{performance.allers_retours_moyens}</p>
              <p className="text-xs text-gray-500">Allers-retours</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{performance.taux_first_pass_global}%</p>
              <p className="text-xs text-gray-500">First Pass</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-red-600">{performance.taux_rejet_global}%</p>
              <p className="text-xs text-gray-500">Taux Rejet</p>
            </div>
          </div>
        </div>
      )}

      {/* Distribution par Zone */}
      {byZone.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">🗺️ Distribution par Zone Industrielle</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={byZone}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="zone_industrielle_code" />
              <YAxis />
              <Tooltip 
                labelFormatter={(label) => byZone.find(z => z.zone_industrielle_code === label)?.zone_industrielle_libelle || label}
              />
              <Legend />
              <Bar dataKey="count" name="Total" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
              <Bar dataKey="en_retard" name="En retard" fill={COLORS.warning} radius={[4, 4, 0, 0]} />
              <Bar dataKey="critiques" name="Critiques" fill={COLORS.danger} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Critical Dossiers Table */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">🚨 Dossiers Nécessitant Attention</h3>
        <CriticalTable data={criticalList} />
      </div>
    </div>
  )
}
