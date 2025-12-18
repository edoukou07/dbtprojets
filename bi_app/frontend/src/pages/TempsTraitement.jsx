import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell,
  ScatterChart, Scatter, ZAxis,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts'
import { 
  Clock, AlertTriangle, TrendingUp, Target, 
  ArrowUp, ArrowDown, Activity, Zap, Filter,
  ChevronDown, ChevronUp, RefreshCw, Search,
  Users, Award, UserCheck, Star, BarChart3, CheckCircle
} from 'lucide-react'
import StatsCard from '../components/StatsCard'
import ExportButton from '../components/ExportButton'
import api from '../services/api'

const COLORS_NIVEAU = {
  'CRITIQUE': '#ef4444',
  'MAJEUR': '#f97316', 
  'MODERE': '#eab308',
  'NORMAL': '#22c55e'
}

const COLORS_STABILITE = {
  'INSTABLE': '#ef4444',
  'VARIABLE': '#f97316',
  'MODEREE': '#eab308', 
  'STABLE': '#22c55e'
}

const COLORS_PERFORMANCE = {
  'EXCELLENT': '#22c55e',
  'BON': '#3b82f6',
  'STANDARD': '#eab308',
  'A_AMELIORER': '#f97316',
  'CRITIQUE': '#ef4444'
}

const CHART_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']

// Badge component for bottleneck level
const NiveauBadge = ({ niveau }) => {
  const colors = {
    'CRITIQUE': 'bg-red-100 text-red-800 border-red-200',
    'MAJEUR': 'bg-orange-100 text-orange-800 border-orange-200',
    'MODERE': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'NORMAL': 'bg-green-100 text-green-800 border-green-200'
  }
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${colors[niveau] || colors['NORMAL']}`}>
      {niveau}
    </span>
  )
}

// Stabilite Badge
const StabiliteBadge = ({ stabilite }) => {
  const colors = {
    'INSTABLE': 'bg-red-100 text-red-800',
    'VARIABLE': 'bg-orange-100 text-orange-800',
    'MODEREE': 'bg-yellow-100 text-yellow-800',
    'STABLE': 'bg-green-100 text-green-800'
  }
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[stabilite] || 'bg-gray-100 text-gray-800'}`}>
      {stabilite}
    </span>
  )
}

// Performance Badge
const PerformanceBadge = ({ classification }) => {
  const config = {
    'EXCELLENT': { color: 'bg-green-100 text-green-800 border-green-200', icon: '⭐' },
    'BON': { color: 'bg-blue-100 text-blue-800 border-blue-200', icon: '👍' },
    'STANDARD': { color: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: '📊' },
    'A_AMELIORER': { color: 'bg-orange-100 text-orange-800 border-orange-200', icon: '⚠️' },
    'CRITIQUE': { color: 'bg-red-100 text-red-800 border-red-200', icon: '🔴' }
  }
  const { color, icon } = config[classification] || config['STANDARD']
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${color}`}>
      {icon} {classification?.replace('_', ' ')}
    </span>
  )
}

// Format duration
const formatDuration = (minutes) => {
  if (!minutes) return '-'
  if (minutes < 60) return `${Math.round(minutes)} min`
  if (minutes < 1440) return `${(minutes / 60).toFixed(1)}h`
  return `${(minutes / 1440).toFixed(1)}j`
}

export default function TempsTraitement() {
  const [activeTab, setActiveTab] = useState('overview')
  const [filterNiveau, setFilterNiveau] = useState('')
  const [searchAction, setSearchAction] = useState('')
  const [expandedRows, setExpandedRows] = useState({})
  
  // Performance agents filters
  const [filterAgent, setFilterAgent] = useState('')
  const [filterClassification, setFilterClassification] = useState('')
  const [selectedEtapeKey, setSelectedEtapeKey] = useState(null)

  // Analyse dossier state
  const [searchDossier, setSearchDossier] = useState('')
  const [selectedDossierRef, setSelectedDossierRef] = useState(null)

  // Fetch summary data
  const { data: summaryData, isLoading: loadingSummary, refetch: refetchSummary } = useQuery({
    queryKey: ['temps-traitement-summary'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/summary/')
      return response.data
    }
  })

  // Fetch all dossiers for dropdown (loaded when tab is active)
  const { data: allDossiers, isLoading: loadingAllDossiers } = useQuery({
    queryKey: ['temps-traitement-all-dossiers'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/recherche_dossiers/?limit=100')
      return response.data
    },
    enabled: activeTab === 'analyse_dossier'
  })

  // Filter dossiers based on search (by reference)
  const filteredDossiers = useMemo(() => {
    if (!allDossiers?.dossiers) return []
    if (!searchDossier) return allDossiers.dossiers
    return allDossiers.dossiers.filter(d => 
      d.dossier_reference?.toLowerCase().includes(searchDossier.toLowerCase())
    )
  }, [allDossiers, searchDossier])

  // Fetch dossier analysis
  const { data: analyseDossierData, isLoading: loadingAnalyseDossier } = useQuery({
    queryKey: ['temps-traitement-analyse-dossier', selectedDossierRef],
    queryFn: async () => {
      const response = await api.get(`/temps-traitement/analyse_dossier/?dossier_ref=${selectedDossierRef}`)
      return response.data
    },
    enabled: !!selectedDossierRef && activeTab === 'analyse_dossier'
  })

  // Fetch detailed goulots
  const { data: goulotsData, isLoading: loadingGoulots } = useQuery({
    queryKey: ['temps-traitement-goulots', filterNiveau],
    queryFn: async () => {
      const params = filterNiveau ? `?niveau=${filterNiveau}` : ''
      const response = await api.get(`/temps-traitement/goulots/${params}`)
      return response.data
    }
  })

  // Fetch chart data
  const { data: chartData, isLoading: loadingCharts } = useQuery({
    queryKey: ['temps-traitement-charts'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/etapes_chart/')
      return response.data
    }
  })

  // Fetch recommendations
  const { data: recoData, isLoading: loadingReco } = useQuery({
    queryKey: ['temps-traitement-recommandations'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/recommandations/')
      return response.data
    }
  })

  // Fetch variability data
  const { data: variabiliteData, isLoading: loadingVariabilite } = useQuery({
    queryKey: ['temps-traitement-variabilite'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/variabilite/')
      return response.data
    }
  })

  // Fetch performance agents summary
  const { data: perfAgentsSummary, isLoading: loadingPerfSummary } = useQuery({
    queryKey: ['temps-traitement-perf-agents-summary'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/performance_agents_summary/')
      return response.data
    },
    enabled: activeTab === 'performance'
  })

  // Fetch performance agents details
  const { data: perfAgentsData, isLoading: loadingPerfAgents } = useQuery({
    queryKey: ['temps-traitement-perf-agents', filterAgent, filterClassification],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filterAgent) params.append('etape', filterAgent)
      if (filterClassification) params.append('classification', filterClassification)
      const response = await api.get(`/temps-traitement/performance_agents/?${params}`)
      return response.data
    },
    enabled: activeTab === 'performance'
  })

  // Fetch performance charts
  const { data: perfChartsData, isLoading: loadingPerfCharts } = useQuery({
    queryKey: ['temps-traitement-perf-charts'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/performance_agents_chart/')
      return response.data
    },
    enabled: activeTab === 'performance'
  })

  // Fetch performance by step
  const { data: perfByStepData } = useQuery({
    queryKey: ['temps-traitement-perf-by-step'],
    queryFn: async () => {
      const response = await api.get('/temps-traitement/performance_agents_by_step/')
      return response.data
    },
    enabled: activeTab === 'performance'
  })

  // Filter goulots by search
  const filteredGoulots = useMemo(() => {
    if (!goulotsData?.goulots) return []
    return goulotsData.goulots.filter(g => 
      g.action?.toLowerCase().includes(searchAction.toLowerCase())
    )
  }, [goulotsData, searchAction])

  // Toggle row expansion
  const toggleRow = (id) => {
    setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }))
  }

  // Prepare export data
  const prepareExportData = () => {
    if (!goulotsData?.goulots) return []
    return goulotsData.goulots.map(g => ({
      'Étape': g.action,
      'Niveau': g.niveau_goulot,
      'Durée Moyenne (min)': g.duree_moyenne_min,
      'Médiane (min)': g.mediane_min,
      '% Workflow': g.pct_workflow,
      'Score Goulot': g.score,
      'CV %': g.cv_pct,
      'Gain Potentiel (h)': g.gain_potentiel_h,
      'Nb Occurrences': g.nb_occurrences,
      'Recommandation': g.recommandation
    }))
  }

  // Prepare performance agents export data
  const preparePerformanceExportData = () => {
    if (!perfAgentsData?.performance) return []
    return perfAgentsData.performance.map(p => ({
      'Agent': p.nom_agent,
      'Étape': p.action_libelle,
      'Nb Traitements': p.nb_traitements,
      'Durée Moyenne (min)': p.duree_moyenne_min,
      'Benchmark (min)': p.moyenne_etape_min,
      'Durée Médiane (min)': p.duree_mediane_min,
      'Taux Réussite (%)': p.taux_reussite,
      'Score Rapidité': p.score_rapidite,
      'Score Régularité': p.score_regularite,
      'Score Volume': p.score_volume,
      'Score Global': p.score_global,
      'Classification': p.classification_performance,
      'Rang': `${p.rang_agent_etape}/${p.nb_agents_etape}`,
      'Écart vs Moyenne (%)': p.ecart_moyenne_pct
    }))
  }

  // Calculate benchmarks by task from performance data
  const benchmarksByTask = useMemo(() => {
    if (!perfAgentsData?.performance) return []
    const taskMap = new Map()
    perfAgentsData.performance.forEach(p => {
      if (!taskMap.has(p.action_libelle)) {
        taskMap.set(p.action_libelle, {
          action: p.action_libelle,
          categorie: p.categorie_etape,
          benchmark_min: p.moyenne_etape_min,
          nb_agents: p.nb_agents_etape,
          etape_key: p.etape_key
        })
      }
    })
    return Array.from(taskMap.values()).sort((a, b) => b.benchmark_min - a.benchmark_min)
  }, [perfAgentsData])

  const isLoading = loadingSummary || loadingGoulots

  if (isLoading && !summaryData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Chargement des données...</span>
      </div>
    )
  }

  const kpis = summaryData?.kpis || {}
  const distribution = summaryData?.distribution || []
  const topGoulots = summaryData?.top_goulots || []

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            ⏱️ Temps de Traitement & Goulots d'Étranglement
          </h1>
          <p className="text-gray-500 mt-1">
            Analyse des délais de traitement et identification des bottlenecks
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => refetchSummary()}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
          <ExportButton
            data={prepareExportData()}
            filename="temps_traitement_goulots"
            title="Analyse Temps Traitement"
          />
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatsCard
          title="Étapes Analysées"
          value={kpis.total_etapes || 0}
          icon={Activity}
          color="blue"
        />
        <StatsCard
          title="Goulots Identifiés"
          value={kpis.nb_goulots || 0}
          subtitle={`${kpis.nb_critiques || 0} critiques`}
          icon={AlertTriangle}
          color="red"
          trend={kpis.nb_critiques > 0 ? 'down' : 'up'}
        />
        <StatsCard
          title="Durée Moyenne"
          value={formatDuration(kpis.duree_moyenne_globale_min)}
          icon={Clock}
          color="purple"
        />
        <StatsCard
          title="Temps Total Workflow"
          value={`${kpis.temps_total_workflow_heures || 0}h`}
          icon={TrendingUp}
          color="indigo"
        />
        <StatsCard
          title="Gain Potentiel"
          value={`${kpis.gain_potentiel_total_heures || 0}h`}
          subtitle="si optimisation 50%"
          icon={Zap}
          color="green"
        />
      </div>

      {/* Alert for critical bottlenecks */}
      {kpis.nb_critiques > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
            <span className="font-medium text-red-800">
              {kpis.nb_critiques} goulot(s) critique(s) détecté(s)
            </span>
          </div>
          <p className="text-red-700 text-sm mt-1">
            Ces étapes consomment une part disproportionnée du temps de traitement et nécessitent une action urgente.
          </p>
        </div>
      )}

      {/* Top Bottlenecks Summary */}
      {topGoulots.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-red-500" />
            Principaux Goulots d'Étranglement
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {topGoulots.map((goulot, idx) => (
              <div 
                key={idx} 
                className={`p-4 rounded-lg border-2 ${
                  goulot.niveau_goulot === 'CRITIQUE' 
                    ? 'border-red-200 bg-red-50' 
                    : 'border-orange-200 bg-orange-50'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-2xl font-bold text-gray-400">#{idx + 1}</span>
                  <NiveauBadge niveau={goulot.niveau_goulot} />
                </div>
                <h3 className="font-medium text-gray-800 truncate" title={goulot.action}>
                  {goulot.action}
                </h3>
                <div className="mt-2 space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Durée moyenne:</span>
                    <span className="font-medium">{formatDuration(goulot.duree_moyenne_min)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">% Workflow:</span>
                    <span className="font-medium text-red-600">{goulot.pct_workflow}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Score:</span>
                    <span className="font-medium">{goulot.score}/100</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-4 px-6" aria-label="Tabs">
            {[
              { id: 'overview', label: 'Vue d\'ensemble', icon: Activity },
              { id: 'details', label: 'Détails par Étape', icon: Clock },
              { id: 'analyse_dossier', label: 'Analyse Dossier', icon: Search },
              { id: 'variabilite', label: 'Variabilité', icon: TrendingUp },
              { id: 'performance', label: 'Performance Agents', icon: Users },
              { id: 'recommandations', label: 'Recommandations', icon: Zap }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {/* Overview Tab - Modern Redesign */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Hero Header */}
              <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 rounded-2xl p-8 text-white">
                <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full -translate-y-48 translate-x-48"></div>
                <div className="absolute bottom-0 left-0 w-72 h-72 bg-indigo-500/20 rounded-full translate-y-36 -translate-x-36"></div>
                <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-purple-400/10 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
                
                <div className="relative z-10">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl">
                      <Activity className="w-8 h-8 text-blue-300" />
                    </div>
                    <div>
                      <p className="text-blue-200 text-sm font-medium">Tableau de bord</p>
                      <h2 className="text-3xl font-bold tracking-tight">Vue d'ensemble</h2>
                    </div>
                  </div>
                  
                  {/* Quick Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-all duration-300 hover:scale-[1.02]">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-red-500/30 rounded-lg">
                          <AlertTriangle className="w-5 h-5 text-red-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">{kpis.nb_critiques || 0}</p>
                          <p className="text-red-200 text-xs">Goulots critiques</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-all duration-300 hover:scale-[1.02]">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-orange-500/30 rounded-lg">
                          <TrendingUp className="w-5 h-5 text-orange-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">{kpis.nb_majeurs || 0}</p>
                          <p className="text-orange-200 text-xs">Goulots majeurs</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-all duration-300 hover:scale-[1.02]">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500/30 rounded-lg">
                          <Clock className="w-5 h-5 text-blue-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">{formatDuration(kpis.duree_moyenne_globale_min)}</p>
                          <p className="text-blue-200 text-xs">Durée moyenne</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-all duration-300 hover:scale-[1.02]">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-emerald-500/30 rounded-lg">
                          <Zap className="w-5 h-5 text-emerald-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">{kpis.gain_potentiel_total_heures || 0}h</p>
                          <p className="text-emerald-200 text-xs">Gain potentiel</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Bar Chart - Duration by Step */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                  <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Durée moyenne par étape (Top 15)
                    </h3>
                  </div>
                  <div className="p-6">
                    {loadingCharts ? (
                      <div className="h-80 flex items-center justify-center">
                        <div className="text-center">
                          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
                          <p className="text-gray-500 text-sm">Chargement...</p>
                        </div>
                      </div>
                    ) : (
                      <ResponsiveContainer width="100%" height={320}>
                        <BarChart 
                          data={chartData?.bar_chart || []} 
                          layout="vertical"
                          margin={{ left: 20, right: 20 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis type="number" tick={{ fontSize: 11, fill: '#6b7280' }} />
                          <YAxis 
                            type="category" 
                            dataKey="name" 
                            width={150}
                            tick={{ fontSize: 11, fill: '#6b7280' }}
                          />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1f2937', 
                              border: 'none', 
                              borderRadius: '12px', 
                              color: 'white',
                              boxShadow: '0 10px 40px rgba(0,0,0,0.2)'
                            }}
                            formatter={(value) => [`${value} min`, 'Durée']}
                          />
                          <Bar 
                            dataKey="duree_min" 
                            name="Durée (min)"
                            radius={[0, 8, 8, 0]}
                          >
                            {(chartData?.bar_chart || []).map((entry, index) => (
                              <Cell 
                                key={`cell-${index}`} 
                                fill={index < 3 ? '#ef4444' : index < 7 ? '#f97316' : '#3b82f6'}
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </div>

                {/* Pie Chart - Workflow Distribution */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                  <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Target className="w-5 h-5" />
                      Répartition du temps dans le workflow
                    </h3>
                  </div>
                  <div className="p-6">
                    {loadingCharts ? (
                      <div className="h-80 flex items-center justify-center">
                        <div className="text-center">
                          <RefreshCw className="w-8 h-8 animate-spin text-purple-500 mx-auto mb-2" />
                          <p className="text-gray-500 text-sm">Chargement...</p>
                        </div>
                      </div>
                    ) : (
                      <ResponsiveContainer width="100%" height={320}>
                        <PieChart>
                          <Pie
                            data={chartData?.pie_chart || []}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={2}
                            label={({ name, value }) => `${value}%`}
                          >
                            {(chartData?.pie_chart || []).map((entry, index) => (
                              <Cell 
                                key={`cell-${index}`} 
                                fill={CHART_COLORS[index % CHART_COLORS.length]}
                                stroke="white"
                                strokeWidth={2}
                              />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1f2937', 
                              border: 'none', 
                              borderRadius: '12px', 
                              color: 'white' 
                            }}
                            formatter={(value) => [`${value}%`, 'Part']} 
                          />
                          <Legend 
                            wrapperStyle={{ paddingTop: '20px' }}
                            formatter={(value) => <span className="text-gray-700 text-sm">{value}</span>}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </div>
              </div>

              {/* Scatter Chart - Variability vs Duration */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-amber-500 to-orange-600 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Activity className="w-5 h-5" />
                      Matrice Durée vs Variabilité
                    </h3>
                    <span className="bg-white/20 text-white text-xs px-3 py-1 rounded-full">
                      Identifier les processus instables
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  {loadingCharts ? (
                    <div className="h-80 flex items-center justify-center">
                      <div className="text-center">
                        <RefreshCw className="w-8 h-8 animate-spin text-orange-500 mx-auto mb-2" />
                        <p className="text-gray-500 text-sm">Chargement...</p>
                      </div>
                    </div>
                  ) : (
                    <>
                      <ResponsiveContainer width="100%" height={350}>
                        <ScatterChart margin={{ bottom: 40, left: 20, right: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis 
                            type="number" 
                            dataKey="x" 
                            name="Durée"
                            tick={{ fontSize: 11, fill: '#6b7280' }}
                            label={{ 
                              value: 'Durée moyenne (min)', 
                              position: 'bottom', 
                              offset: 20,
                              style: { fontSize: 12, fill: '#6b7280' }
                            }}
                          />
                          <YAxis 
                            type="number" 
                            dataKey="y" 
                            name="CV%"
                            tick={{ fontSize: 11, fill: '#6b7280' }}
                            label={{ 
                              value: 'Coefficient de Variation (%)', 
                              angle: -90, 
                              position: 'insideLeft',
                              style: { fontSize: 12, fill: '#6b7280' }
                            }}
                          />
                          <ZAxis type="number" dataKey="size" range={[60, 500]} />
                          <Tooltip 
                            content={({ payload }) => {
                              if (payload && payload.length) {
                                const data = payload[0].payload
                                return (
                                  <div className="bg-gray-900 text-white p-4 rounded-xl shadow-xl border border-gray-700">
                                    <p className="font-bold text-lg mb-2">{data.name}</p>
                                    <div className="space-y-1 text-sm">
                                      <p className="flex justify-between gap-4">
                                        <span className="text-gray-400">Durée:</span>
                                        <span className="font-medium">{data.x} min</span>
                                      </p>
                                      <p className="flex justify-between gap-4">
                                        <span className="text-gray-400">CV:</span>
                                        <span className="font-medium">{data.y}%</span>
                                      </p>
                                      <p className="flex justify-between gap-4">
                                        <span className="text-gray-400">Occurrences:</span>
                                        <span className="font-medium">{data.size}</span>
                                      </p>
                                    </div>
                                    <div className="mt-2 pt-2 border-t border-gray-700">
                                      <NiveauBadge niveau={data.niveau_goulot} />
                                    </div>
                                  </div>
                                )
                              }
                              return null
                            }}
                          />
                          <Scatter 
                            data={chartData?.scatter_chart || []} 
                            fill="#8884d8"
                          >
                            {(chartData?.scatter_chart || []).map((entry, index) => (
                              <Cell 
                                key={`cell-${index}`} 
                                fill={COLORS_NIVEAU[entry.niveau_goulot] || '#22c55e'} 
                              />
                            ))}
                          </Scatter>
                        </ScatterChart>
                      </ResponsiveContainer>
                      
                      {/* Zone indicator */}
                      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
                        <div className="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-full">
                          <div className="w-3 h-3 rounded-full bg-red-500"></div>
                          <span className="text-red-700">Zone critique: coin supérieur droit</span>
                        </div>
                        <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-full">
                          <div className="w-3 h-3 rounded-full bg-green-500"></div>
                          <span className="text-green-700">Zone optimale: coin inférieur gauche</span>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Distribution by Level - Modern Cards */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Target className="w-5 h-5" />
                      Distribution par niveau de goulot
                    </h3>
                    <span className="text-slate-300 text-sm">{distribution?.length || 0} niveaux</span>
                  </div>
                </div>
                <div className="p-6">
                  {/* Modern Progress Bar */}
                  <div className="mb-8">
                    <p className="text-sm text-gray-500 mb-3">Répartition du temps total de traitement</p>
                    <div className="relative">
                      <div className="flex h-6 rounded-full overflow-hidden bg-gray-100 shadow-inner">
                        {distribution.map((item, idx) => (
                          <div 
                            key={idx}
                            className="relative group transition-all duration-500 hover:opacity-90"
                            style={{ 
                              width: `${item.pct_temps_total}%`,
                              backgroundColor: COLORS_NIVEAU[item.niveau_goulot],
                              minWidth: item.pct_temps_total > 0 ? '30px' : '0'
                            }}
                          >
                            {item.pct_temps_total >= 10 && (
                              <span className="absolute inset-0 flex items-center justify-center text-white text-xs font-bold">
                                {item.pct_temps_total}%
                              </span>
                            )}
                            {/* Tooltip */}
                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                              <div className="bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                                {item.niveau_goulot}: {item.pct_temps_total}%
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="flex justify-between mt-2 text-xs text-gray-400">
                        <span>0%</span>
                        <span>100%</span>
                      </div>
                    </div>
                  </div>

                  {/* Distribution Cards Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {distribution.map((item, idx) => {
                      const icons = {
                        'CRITIQUE': { emoji: '🔴', bg: 'from-red-500 to-rose-600' },
                        'MAJEUR': { emoji: '🟠', bg: 'from-orange-500 to-amber-600' }, 
                        'MODERE': { emoji: '🟡', bg: 'from-yellow-500 to-amber-500' },
                        'NORMAL': { emoji: '🟢', bg: 'from-green-500 to-emerald-600' }
                      }
                      const config = icons[item.niveau_goulot] || { emoji: '⚪', bg: 'from-gray-500 to-gray-600' }
                      
                      return (
                        <div 
                          key={idx}
                          className="group relative overflow-hidden rounded-2xl transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
                        >
                          {/* Gradient Background */}
                          <div className={`absolute inset-0 bg-gradient-to-br ${config.bg} opacity-10 group-hover:opacity-20 transition-opacity`}></div>
                          
                          {/* Border */}
                          <div 
                            className="absolute inset-0 rounded-2xl border-2 transition-colors"
                            style={{ borderColor: COLORS_NIVEAU[item.niveau_goulot] }}
                          ></div>
                          
                          <div className="relative p-5">
                            {/* Header */}
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">{config.emoji}</span>
                                <span 
                                  className="font-bold text-sm uppercase tracking-wide"
                                  style={{ color: COLORS_NIVEAU[item.niveau_goulot] }}
                                >
                                  {item.niveau_goulot}
                                </span>
                              </div>
                              <div 
                                className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${config.bg} flex items-center justify-center text-white text-2xl font-bold shadow-lg`}
                              >
                                {item.count}
                              </div>
                            </div>
                            
                            {/* Stats */}
                            <div className="space-y-3">
                              {/* Percentage */}
                              <div>
                                <div className="flex justify-between text-sm mb-1.5">
                                  <span className="text-gray-500">Part du workflow</span>
                                  <span className="font-bold" style={{ color: COLORS_NIVEAU[item.niveau_goulot] }}>
                                    {item.pct_temps_total}%
                                  </span>
                                </div>
                                <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                                  <div 
                                    className={`h-full rounded-full bg-gradient-to-r ${config.bg} transition-all duration-700`}
                                    style={{ width: `${Math.min(item.pct_temps_total, 100)}%` }}
                                  />
                                </div>
                              </div>
                              
                              {/* Duration */}
                              <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                                <div className="flex items-center gap-1.5 text-gray-500">
                                  <Clock className="w-4 h-4" />
                                  <span className="text-sm">Durée moy.</span>
                                </div>
                                <span className="font-bold text-gray-800 text-lg">
                                  {formatDuration(item.duree_moyenne_min)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  
                  {/* Legend */}
                  <div className="mt-8 pt-6 border-t border-gray-100">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center gap-2 p-3 bg-red-50 rounded-xl">
                        <span className="text-xl">🔴</span>
                        <div>
                          <p className="font-medium text-red-800">Critique</p>
                          <p className="text-red-600 text-xs">Action urgente requise</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-xl">
                        <span className="text-xl">🟠</span>
                        <div>
                          <p className="font-medium text-orange-800">Majeur</p>
                          <p className="text-orange-600 text-xs">À optimiser</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 p-3 bg-yellow-50 rounded-xl">
                        <span className="text-xl">🟡</span>
                        <div>
                          <p className="font-medium text-yellow-800">Modéré</p>
                          <p className="text-yellow-600 text-xs">À surveiller</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 p-3 bg-green-50 rounded-xl">
                        <span className="text-xl">🟢</span>
                        <div>
                          <p className="font-medium text-green-800">Normal</p>
                          <p className="text-green-600 text-xs">Processus optimal</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Details Tab */}
          {activeTab === 'details' && (
            <div className="space-y-4">
              {/* Filters */}
              <div className="flex flex-wrap gap-4 items-center">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Rechercher une étape..."
                    value={searchAction}
                    onChange={(e) => setSearchAction(e.target.value)}
                    className="pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <select
                  value={filterNiveau}
                  onChange={(e) => setFilterNiveau(e.target.value)}
                  className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Tous les niveaux</option>
                  <option value="CRITIQUE">Critique</option>
                  <option value="MAJEUR">Majeur</option>
                  <option value="MODERE">Modéré</option>
                  <option value="NORMAL">Normal</option>
                </select>
                <span className="text-sm text-gray-500">
                  {filteredGoulots.length} étape(s)
                </span>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Étape
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Niveau
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Durée Moy.
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        % Workflow
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Score
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        CV %
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Gain Pot.
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Détails
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredGoulots.map((goulot) => (
                      <>
                        <tr 
                          key={goulot.etape_id}
                          className={`hover:bg-gray-50 ${goulot.est_goulot ? 'bg-red-50/30' : ''}`}
                        >
                          <td className="px-4 py-3">
                            <div className="font-medium text-gray-900 truncate max-w-xs" title={goulot.action}>
                              {goulot.action}
                            </div>
                            <div className="text-xs text-gray-500">
                              {goulot.nb_occurrences} occurrences
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <NiveauBadge niveau={goulot.niveau_goulot} />
                          </td>
                          <td className="px-4 py-3 text-right font-medium">
                            {formatDuration(goulot.duree_moyenne_min)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <span className={goulot.pct_workflow > 10 ? 'text-red-600 font-medium' : ''}>
                              {goulot.pct_workflow}%
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <div 
                                className="w-12 bg-gray-200 rounded-full h-2"
                                title={`Score: ${goulot.score}/100`}
                              >
                                <div 
                                  className="h-2 rounded-full"
                                  style={{ 
                                    width: `${Math.min(goulot.score || 0, 100)}%`,
                                    backgroundColor: COLORS_NIVEAU[goulot.niveau_goulot]
                                  }}
                                />
                              </div>
                              <span className="text-sm">{goulot.score}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <span className={goulot.cv_pct > 100 ? 'text-orange-600' : ''}>
                              {goulot.cv_pct || '-'}%
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right text-green-600 font-medium">
                            {goulot.gain_potentiel_h}h
                          </td>
                          <td className="px-4 py-3 text-center">
                            <button
                              onClick={() => toggleRow(goulot.etape_id)}
                              className="p-1 hover:bg-gray-200 rounded"
                            >
                              {expandedRows[goulot.etape_id] ? (
                                <ChevronUp className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                            </button>
                          </td>
                        </tr>
                        {expandedRows[goulot.etape_id] && (
                          <tr className="bg-gray-50">
                            <td colSpan="8" className="px-4 py-4">
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div>
                                  <span className="text-gray-500">Médiane:</span>
                                  <span className="ml-2 font-medium">{formatDuration(goulot.mediane_min)}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Min:</span>
                                  <span className="ml-2 font-medium">{formatDuration(goulot.min_min)}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Max:</span>
                                  <span className="ml-2 font-medium">{formatDuration(goulot.max_min)}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">P90:</span>
                                  <span className="ml-2 font-medium">{formatDuration(goulot.p90_min)}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Dossiers:</span>
                                  <span className="ml-2 font-medium">{goulot.nb_dossiers_distincts}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Agents:</span>
                                  <span className="ml-2 font-medium">{goulot.nb_agents_impliques}</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Ratio moyenne:</span>
                                  <span className="ml-2 font-medium">{goulot.ratio_moyenne}x</span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Temps total:</span>
                                  <span className="ml-2 font-medium">{goulot.temps_total_h}h</span>
                                </div>
                              </div>
                              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                                <span className="text-blue-800 font-medium">Recommandation:</span>
                                <p className="text-blue-700 mt-1">{goulot.recommandation}</p>
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Variability Tab */}
          {activeTab === 'variabilite' && (
            <div className="space-y-6">
              {/* Stability Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {variabiliteData?.stabilite_summary?.map((item, idx) => (
                  <div 
                    key={idx}
                    className="bg-white rounded-lg p-4 border-l-4"
                    style={{ borderColor: COLORS_STABILITE[item.stabilite] }}
                  >
                    <StabiliteBadge stabilite={item.stabilite} />
                    <p className="text-2xl font-bold mt-2">{item.count}</p>
                    <p className="text-sm text-gray-500">processus</p>
                  </div>
                ))}
              </div>

              {/* Variability Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Étape</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Stabilité</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">CV %</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Moyenne</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Médiane</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Écart-type</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Min → Max</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">P90</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {variabiliteData?.variabilite?.map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium truncate max-w-xs" title={item.action}>
                          {item.action}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <StabiliteBadge stabilite={item.stabilite} />
                        </td>
                        <td className="px-4 py-3 text-right font-medium">
                          <span className={item.cv_pct > 100 ? 'text-red-600' : ''}>
                            {item.cv_pct}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">{formatDuration(item.moyenne_min)}</td>
                        <td className="px-4 py-3 text-right">{formatDuration(item.mediane_min)}</td>
                        <td className="px-4 py-3 text-right">{formatDuration(item.ecart_type_min)}</td>
                        <td className="px-4 py-3 text-right text-sm">
                          {formatDuration(item.min_min)} → {formatDuration(item.max_min)}
                        </td>
                        <td className="px-4 py-3 text-right">{formatDuration(item.p90_min)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Performance Agents Tab - Redesigned */}
          {activeTab === 'performance' && (
            <div className="space-y-6">
              {/* Performance KPIs */}
              {loadingPerfSummary ? (
                <div className="bg-gradient-to-br from-indigo-50 to-purple-100 rounded-2xl p-12 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                  <p className="text-gray-600 font-medium">Analyse des performances en cours...</p>
                </div>
              ) : (
                <>
                  {/* Hero Stats Section */}
                  <div className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-purple-900 to-violet-900 rounded-2xl p-8 text-white">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full -translate-y-48 translate-x-48"></div>
                    <div className="absolute bottom-0 left-0 w-72 h-72 bg-indigo-500/10 rounded-full translate-y-36 -translate-x-36"></div>
                    <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-violet-500/5 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
                    
                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-8">
                        <div>
                          <p className="text-purple-200 text-sm font-medium mb-1">Tableau de Bord</p>
                          <h2 className="text-3xl font-bold tracking-tight">Performance des Agents</h2>
                        </div>
                        <ExportButton
                          data={preparePerformanceExportData()}
                          filename="performance_agents"
                          title="Performance Agents"
                        />
                      </div>
                      
                      {/* Key Metrics */}
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="p-3 bg-blue-500/30 rounded-xl">
                              <Users className="w-6 h-6 text-blue-300" />
                            </div>
                            <div>
                              <p className="text-4xl font-bold">{perfAgentsSummary?.kpis?.nb_agents || 0}</p>
                              <p className="text-blue-200 text-sm">Agents</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="p-3 bg-purple-500/30 rounded-xl">
                              <Activity className="w-6 h-6 text-purple-300" />
                            </div>
                            <div>
                              <p className="text-4xl font-bold">{perfAgentsSummary?.kpis?.nb_etapes_analysees || 0}</p>
                              <p className="text-purple-200 text-sm">Étapes</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="p-3 bg-indigo-500/30 rounded-xl">
                              <Target className="w-6 h-6 text-indigo-300" />
                            </div>
                            <div>
                              <p className="text-4xl font-bold">{perfAgentsSummary?.kpis?.total_traitements || 0}</p>
                              <p className="text-indigo-200 text-sm">Traitements</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 border-l-4 border-l-green-400 hover:bg-white/15 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="p-3 bg-green-500/30 rounded-xl">
                              <Star className="w-6 h-6 text-green-300" />
                            </div>
                            <div>
                              <p className="text-4xl font-bold text-green-300">{perfAgentsSummary?.kpis?.nb_excellent || 0}</p>
                              <p className="text-green-200 text-sm">Excellents</p>
                              <p className="text-xs text-green-300/70">+{perfAgentsSummary?.kpis?.nb_bon || 0} bons</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 border-l-4 border-l-orange-400 hover:bg-white/15 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="p-3 bg-orange-500/30 rounded-xl">
                              <AlertTriangle className="w-6 h-6 text-orange-300" />
                            </div>
                            <div>
                              <p className="text-4xl font-bold text-orange-300">
                                {(perfAgentsSummary?.kpis?.nb_ameliorer || 0) + (perfAgentsSummary?.kpis?.nb_critique || 0)}
                              </p>
                              <p className="text-orange-200 text-sm">À améliorer</p>
                              {(perfAgentsSummary?.kpis?.nb_critique || 0) > 0 && (
                                <p className="text-xs text-red-300">{perfAgentsSummary?.kpis?.nb_critique} critique(s)</p>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Distribution Chart - Modern Design */}
                  <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Activity className="w-5 h-5" />
                        Répartition des Performances
                      </h3>
                    </div>
                    <div className="p-6">
                      {/* Visual Progress Bar */}
                      <div className="mb-8">
                        <div className="flex h-8 rounded-xl overflow-hidden shadow-inner bg-gray-100">
                          {perfAgentsSummary?.distribution?.map((item, idx) => {
                            const total = perfAgentsSummary.distribution.reduce((sum, d) => sum + d.count, 0)
                            const pct = total > 0 ? (item.count / total * 100) : 0
                            return (
                              <div 
                                key={idx}
                                className="flex items-center justify-center text-xs font-bold text-white transition-all duration-700 hover:opacity-90"
                                style={{ 
                                  width: `${pct}%`,
                                  backgroundColor: COLORS_PERFORMANCE[item.classification_performance],
                                  minWidth: pct > 0 ? '50px' : '0'
                                }}
                                title={`${item.classification_performance}: ${item.count} (${Math.round(pct)}%)`}
                              >
                                {pct > 10 ? `${Math.round(pct)}%` : ''}
                              </div>
                            )
                          })}
                        </div>
                      </div>

                      {/* Distribution Cards */}
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        {perfAgentsSummary?.distribution?.map((item, idx) => {
                          const total = perfAgentsSummary.distribution.reduce((sum, d) => sum + d.count, 0)
                          const pct = total > 0 ? (item.count / total * 100) : 0
                          return (
                            <div 
                              key={idx}
                              className="group relative rounded-2xl p-5 text-center border-2 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
                              style={{ borderColor: COLORS_PERFORMANCE[item.classification_performance] }}
                            >
                              <div 
                                className="w-16 h-16 rounded-2xl mx-auto flex items-center justify-center text-white text-2xl font-bold mb-3 transition-transform group-hover:scale-110"
                                style={{ backgroundColor: COLORS_PERFORMANCE[item.classification_performance] }}
                              >
                                {item.count}
                              </div>
                              <p className="font-bold text-base mb-1" style={{ color: COLORS_PERFORMANCE[item.classification_performance] }}>
                                {item.classification_performance === 'A_AMELIORER' ? 'À Améliorer' : item.classification_performance}
                              </p>
                              <p className="text-sm text-gray-500">{Math.round(pct)}% du total</p>
                              <div className="mt-2 pt-2 border-t border-gray-100">
                                <p className="text-xs text-gray-400">Score moyen</p>
                                <p className="font-semibold text-gray-700">{item.score_moyen}</p>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  </div>

                  {/* Top Performers & Need Improvement - Modern Cards */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Top Performers */}
                    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                      <div className="bg-gradient-to-r from-emerald-500 to-green-600 px-6 py-4">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                          <Award className="w-5 h-5" />
                          🏆 Top Performers
                        </h3>
                      </div>
                      <div className="p-6">
                        <div className="space-y-3">
                          {perfAgentsSummary?.top_performers?.map((perf, idx) => (
                            <div 
                              key={idx} 
                              className="group relative bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4 border border-green-100 hover:shadow-md hover:border-green-300 transition-all duration-300"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-white shadow-lg ${
                                    idx === 0 ? 'bg-gradient-to-br from-yellow-400 to-amber-500' :
                                    idx === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-400' :
                                    idx === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-500' :
                                    'bg-gradient-to-br from-green-400 to-green-500'
                                  }`}>
                                    {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`}
                                  </div>
                                  <div>
                                    <p className="font-bold text-gray-800">{perf.nom_agent}</p>
                                    <p className="text-sm text-gray-500 line-clamp-1">{perf.etape}</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <p className="text-2xl font-bold text-green-600">{perf.score}</p>
                                  <PerformanceBadge classification={perf.classification_performance} />
                                </div>
                              </div>
                              {/* Progress indicator */}
                              <div className="mt-3 h-1.5 bg-green-100 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full transition-all duration-500"
                                  style={{ width: `${perf.score}%` }}
                                />
                              </div>
                            </div>
                          ))}
                          {(!perfAgentsSummary?.top_performers || perfAgentsSummary.top_performers.length === 0) && (
                            <div className="text-center py-8 text-gray-400">
                              <Award className="w-12 h-12 mx-auto mb-2 opacity-50" />
                              <p>Aucun top performer identifié</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Need Improvement */}
                    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                      <div className="bg-gradient-to-r from-orange-500 to-red-500 px-6 py-4">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                          <AlertTriangle className="w-5 h-5" />
                          ⚠️ Nécessitent Amélioration
                        </h3>
                      </div>
                      <div className="p-6">
                        <div className="space-y-3">
                          {perfAgentsSummary?.need_improvement?.map((perf, idx) => (
                            <div 
                              key={idx} 
                              className="group relative bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-4 border border-orange-100 hover:shadow-md hover:border-orange-300 transition-all duration-300"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center text-white font-bold shadow-lg">
                                    {idx + 1}
                                  </div>
                                  <div>
                                    <p className="font-bold text-gray-800">{perf.nom_agent}</p>
                                    <p className="text-sm text-gray-500 line-clamp-1">{perf.etape}</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <p className={`text-lg font-bold ${
                                    perf.ecart_moyenne_pct > 50 ? 'text-red-600' : 'text-orange-600'
                                  }`}>
                                    {perf.ecart_moyenne_pct > 0 ? '+' : ''}{perf.ecart_moyenne_pct}%
                                  </p>
                                  <p className="text-xs text-gray-500">vs moyenne</p>
                                  <PerformanceBadge classification={perf.classification_performance} />
                                </div>
                              </div>
                            </div>
                          ))}
                          {(!perfAgentsSummary?.need_improvement || perfAgentsSummary.need_improvement.length === 0) && (
                            <div className="text-center py-8 text-gray-400">
                              <UserCheck className="w-12 h-12 mx-auto mb-2 opacity-50" />
                              <p>Aucun agent nécessitant une amélioration urgente</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* Charts Section - Modern Design */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Bar Chart - Agent Scores */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                  <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-6 py-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Scores par Composante
                    </h3>
                  </div>
                  <div className="p-6">
                    {loadingPerfCharts ? (
                      <div className="h-80 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                      </div>
                    ) : (
                      <ResponsiveContainer width="100%" height={320}>
                        <BarChart data={perfChartsData?.bar_chart || []}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis dataKey="nom_agent" tick={{ fontSize: 11, fill: '#6b7280' }} />
                          <YAxis domain={[0, 100]} tick={{ fill: '#6b7280' }} />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1f2937', 
                              border: 'none', 
                              borderRadius: '12px', 
                              color: 'white',
                              boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
                            }}
                          />
                          <Legend />
                          <Bar dataKey="rapidite" name="⚡ Rapidité" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="regularite" name="📊 Régularité" fill="#22c55e" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="volume" name="📈 Volume" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </div>

                {/* Score Global Bar Chart */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                  <div className="bg-gradient-to-r from-violet-600 to-purple-600 px-6 py-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Star className="w-5 h-5" />
                      Classement Global
                    </h3>
                  </div>
                  <div className="p-6">
                    {loadingPerfCharts ? (
                      <div className="h-80 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600"></div>
                      </div>
                    ) : (
                      <ResponsiveContainer width="100%" height={320}>
                        <BarChart data={perfChartsData?.bar_chart || []} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis type="number" domain={[0, 100]} tick={{ fill: '#6b7280' }} />
                          <YAxis type="category" dataKey="nom_agent" width={120} tick={{ fontSize: 11, fill: '#6b7280' }} />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1f2937', 
                              border: 'none', 
                              borderRadius: '12px', 
                              color: 'white' 
                            }}
                            formatter={(value) => [`${value}/100`, 'Score Global']}
                          />
                          <Bar dataKey="global" name="Score Global" radius={[0, 8, 8, 0]}>
                            {(perfChartsData?.bar_chart || []).map((entry, index) => (
                              <Cell 
                                key={`cell-${index}`}
                                fill={
                                  entry.global >= 80 ? '#22c55e' :
                                  entry.global >= 60 ? '#3b82f6' :
                                  entry.global >= 40 ? '#eab308' :
                                  entry.global >= 20 ? '#f97316' :
                                  '#ef4444'
                                }
                              />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </div>
              </div>

              {/* Filters & Search */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Filter className="w-5 h-5" />
                    Analyse Détaillée
                  </h3>
                </div>
                <div className="p-6">
                  {/* Search & Filter Controls */}
                  <div className="flex flex-wrap gap-4 items-center mb-6">
                    <div className="relative flex-1 min-w-[250px]">
                      <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        placeholder="🔍 Rechercher une étape ou un agent..."
                        value={filterAgent}
                        onChange={(e) => setFilterAgent(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                      />
                    </div>
                    <select
                      value={filterClassification}
                      onChange={(e) => setFilterClassification(e.target.value)}
                      className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white min-w-[180px]"
                    >
                      <option value="">📊 Toutes classifications</option>
                      <option value="EXCELLENT">⭐ Excellent</option>
                      <option value="BON">👍 Bon</option>
                      <option value="STANDARD">📈 Standard</option>
                      <option value="A_AMELIORER">⚠️ À Améliorer</option>
                      <option value="CRITIQUE">🔴 Critique</option>
                    </select>
                  </div>

                  {/* Benchmarks by Task Summary */}
                  {benchmarksByTask.length > 0 && (
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-semibold text-gray-700 flex items-center gap-2">
                          <Target className="w-5 h-5 text-indigo-500" />
                          Benchmarks par Tâche
                        </h4>
                        <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                          Cliquez pour filtrer
                        </span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                        {benchmarksByTask.slice(0, 12).map((task, idx) => (
                          <div 
                            key={idx}
                            className="group bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-3 border border-indigo-100 hover:shadow-lg hover:border-indigo-300 transition-all cursor-pointer"
                            onClick={() => setFilterAgent(task.action)}
                            title={`Cliquer pour filtrer par ${task.action}`}
                          >
                            <div className="text-xs text-gray-500 truncate mb-2 font-medium" title={task.action}>
                              {task.action}
                            </div>
                            <div className="flex items-baseline gap-1">
                              <span className="text-xl font-bold text-indigo-600 group-hover:text-indigo-700">
                                {formatDuration(task.benchmark_min)}
                              </span>
                            </div>
                            <div className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {task.nb_agents} agent{task.nb_agents > 1 ? 's' : ''}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Performance Table - Modern */}
                  <div className="overflow-x-auto rounded-xl border border-gray-200">
                    <table className="min-w-full">
                      <thead>
                        <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                          <th className="px-4 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Agent
                          </th>
                          <th className="px-4 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Étape
                          </th>
                          <th className="px-4 py-4 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Niveau
                          </th>
                          <th className="px-4 py-4 text-right text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Actions
                          </th>
                          <th className="px-4 py-4 text-right text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Durée Agent
                          </th>
                          <th className="px-4 py-4 text-right text-xs font-bold text-gray-600 uppercase tracking-wider">
                            <span className="flex items-center justify-end gap-1">
                              Benchmark
                              <span className="text-indigo-500 text-lg" title="Temps de référence moyen">ⓘ</span>
                            </span>
                          </th>
                          <th className="px-4 py-4 text-right text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Écart
                          </th>
                          <th className="px-4 py-4 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Score
                          </th>
                          <th className="px-4 py-4 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">
                            Rang
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {loadingPerfAgents ? (
                          <tr>
                            <td colSpan="9" className="px-4 py-12 text-center">
                              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto"></div>
                              <p className="mt-3 text-gray-500">Chargement des données...</p>
                            </td>
                          </tr>
                        ) : (
                          perfAgentsData?.performance?.map((perf, idx) => (
                            <tr 
                              key={idx} 
                              className={`hover:bg-gray-50 transition-colors ${
                                perf.est_meilleur_etape ? 'bg-gradient-to-r from-green-50/50 to-transparent' : 
                                perf.est_moins_bon_etape ? 'bg-gradient-to-r from-red-50/50 to-transparent' : ''
                              }`}
                            >
                              <td className="px-4 py-4">
                                <div className="flex items-center gap-2">
                                  {perf.est_meilleur_etape && (
                                    <span className="text-lg" title="Meilleur sur cette étape">🏆</span>
                                  )}
                                  {perf.est_moins_bon_etape && (
                                    <span className="text-lg" title="Moins bon sur cette étape">📉</span>
                                  )}
                                  <div>
                                    <p className="font-semibold text-gray-800">{perf.nom_agent}</p>
                                  </div>
                                </div>
                              </td>
                              <td className="px-4 py-4">
                                <div>
                                  <p className="text-gray-800 truncate max-w-[200px]" title={perf.action_libelle}>
                                    {perf.action_libelle}
                                  </p>
                                  <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full mt-1">
                                    {perf.categorie_etape}
                                  </span>
                                </div>
                              </td>
                              <td className="px-4 py-4 text-center">
                                <PerformanceBadge classification={perf.classification_performance} />
                              </td>
                              <td className="px-4 py-4 text-right">
                                <span className="inline-flex items-center px-3 py-1 bg-indigo-50 text-indigo-700 rounded-lg font-semibold">
                                  {perf.nb_traitements}
                                </span>
                              </td>
                              <td className="px-4 py-4 text-right">
                                <p className="font-semibold text-gray-800">{formatDuration(perf.duree_moyenne_min)}</p>
                                <p className="text-xs text-gray-400">méd: {formatDuration(perf.duree_mediane_min)}</p>
                              </td>
                              <td className="px-4 py-4 text-right">
                                <p className="font-semibold text-indigo-600">{formatDuration(perf.moyenne_etape_min)}</p>
                                <p className="text-xs text-gray-400">{perf.nb_agents_etape} agents</p>
                              </td>
                              <td className="px-4 py-4 text-right">
                                <p className={`font-bold text-lg ${
                                  perf.ecart_moyenne_pct < -20 ? 'text-green-600' :
                                  perf.ecart_moyenne_pct > 20 ? 'text-red-600' :
                                  'text-gray-600'
                                }`}>
                                  {perf.ecart_moyenne_pct > 0 ? '+' : ''}{perf.ecart_moyenne_pct}%
                                </p>
                              </td>
                              <td className="px-4 py-4">
                                <div className="flex items-center justify-center gap-2">
                                  <div className="relative w-20 h-3 bg-gray-200 rounded-full overflow-hidden">
                                    <div 
                                      className="absolute top-0 left-0 h-full rounded-full transition-all duration-500"
                                      style={{ 
                                        width: `${Math.min(perf.score_global || 0, 100)}%`,
                                        backgroundColor: COLORS_PERFORMANCE[perf.classification_performance]
                                      }}
                                    />
                                  </div>
                                  <span className="font-bold text-gray-700 w-8">{perf.score_global}</span>
                                </div>
                              </td>
                              <td className="px-4 py-4 text-center">
                                <span className={`inline-flex items-center justify-center w-12 h-8 rounded-lg text-sm font-bold ${
                                  perf.rang_agent_etape === 1 
                                    ? 'bg-gradient-to-r from-yellow-400 to-amber-500 text-white' 
                                    : perf.rang_agent_etape === perf.nb_agents_etape 
                                      ? 'bg-gradient-to-r from-red-400 to-red-500 text-white' 
                                      : 'bg-gray-100 text-gray-700'
                                }`}>
                                  {perf.rang_agent_etape}/{perf.nb_agents_etape}
                                </span>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations Tab - Modern Redesign */}
          {activeTab === 'recommandations' && (
            <div className="space-y-6">
              {/* Hero Header */}
              <div className="relative overflow-hidden bg-gradient-to-br from-emerald-900 via-teal-800 to-cyan-900 rounded-2xl p-8 text-white">
                <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/20 rounded-full -translate-y-40 translate-x-40"></div>
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-cyan-500/20 rounded-full translate-y-32 -translate-x-32"></div>
                <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-teal-400/10 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
                
                <div className="relative z-10">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl">
                          <Zap className="w-8 h-8 text-emerald-300" />
                        </div>
                        <div>
                          <p className="text-emerald-200 text-sm font-medium">Optimisation des processus</p>
                          <h2 className="text-3xl font-bold tracking-tight">Recommandations</h2>
                        </div>
                      </div>
                      <p className="text-emerald-100/80 text-sm max-w-md mt-2">
                        Identifiez les goulots d'étranglement et optimisez vos temps de traitement
                      </p>
                    </div>
                    
                    {/* Total Gain Highlight */}
                    <div className="flex items-center gap-4">
                      <div className="relative">
                        <div className="absolute inset-0 bg-emerald-400/30 blur-xl rounded-full"></div>
                        <div className="relative bg-gradient-to-br from-emerald-400 to-teal-500 rounded-2xl p-6 text-center shadow-xl">
                          <p className="text-5xl font-black text-white">
                            {recoData?.total_gain_heures || 0}h
                          </p>
                          <p className="text-emerald-100 text-sm font-medium mt-1">Gain potentiel</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* KPI Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-red-500/30 rounded-lg">
                          <AlertTriangle className="w-5 h-5 text-red-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">
                            {recoData?.recommandations?.filter(r => r.niveau_goulot === 'CRITIQUE').length || 0}
                          </p>
                          <p className="text-red-200 text-xs">Critiques</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-orange-500/30 rounded-lg">
                          <TrendingUp className="w-5 h-5 text-orange-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">
                            {recoData?.recommandations?.filter(r => r.niveau_goulot === 'MAJEUR').length || 0}
                          </p>
                          <p className="text-orange-200 text-xs">Majeurs</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-yellow-500/30 rounded-lg">
                          <Activity className="w-5 h-5 text-yellow-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">
                            {recoData?.recommandations?.filter(r => r.niveau_goulot === 'MINEUR').length || 0}
                          </p>
                          <p className="text-yellow-200 text-xs">Mineurs</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 hover:bg-white/15 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-cyan-500/30 rounded-lg">
                          <Target className="w-5 h-5 text-cyan-300" />
                        </div>
                        <div>
                          <p className="text-3xl font-bold">{recoData?.nb_actions_requises || 0}</p>
                          <p className="text-cyan-200 text-xs">Actions totales</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Impact Overview Chart */}
              {recoData?.recommandations?.length > 0 && (
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                  <div className="bg-gradient-to-r from-teal-600 to-emerald-600 px-6 py-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Vue d'ensemble des impacts
                    </h3>
                  </div>
                  <div className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart 
                        data={recoData?.recommandations?.slice(0, 8).map(r => ({
                          name: (r.action || '').substring(0, 20) + ((r.action || '').length > 20 ? '...' : ''),
                          fullName: r.action,
                          gain: r.gain_potentiel_h || 0,
                          score: r.score || 0,
                          niveau: r.niveau_goulot
                        })) || []}
                        margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis 
                          dataKey="name" 
                          tick={{ fontSize: 11, fill: '#6b7280' }}
                          angle={-45}
                          textAnchor="end"
                          height={80}
                        />
                        <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#1f2937', 
                            border: 'none', 
                            borderRadius: '12px', 
                            color: 'white',
                            boxShadow: '0 10px 40px rgba(0,0,0,0.2)'
                          }}
                          formatter={(value, name) => [
                            name === 'gain' ? `${value}h` : value,
                            name === 'gain' ? 'Gain potentiel' : 'Score'
                          ]}
                          labelFormatter={(label, payload) => payload[0]?.payload?.fullName || label}
                        />
                        <Bar 
                          dataKey="gain" 
                          radius={[8, 8, 0, 0]} 
                          name="gain"
                        >
                          {recoData?.recommandations?.slice(0, 8).map((entry, index) => (
                            <Cell 
                              key={`cell-${index}`} 
                              fill={
                                entry.niveau_goulot === 'CRITIQUE' ? '#ef4444' :
                                entry.niveau_goulot === 'MAJEUR' ? '#f97316' :
                                '#eab308'
                              }
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Recommendations List - Modern Cards */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-emerald-600" />
                    {recoData?.recommandations?.length || 0} Recommandations identifiées
                  </h3>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-red-500"></span>
                      <span className="text-gray-600">Critique</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-orange-500"></span>
                      <span className="text-gray-600">Majeur</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                      <span className="text-gray-600">Mineur</span>
                    </span>
                  </div>
                </div>

                {recoData?.recommandations?.map((reco, idx) => (
                  <div 
                    key={idx}
                    className={`group relative bg-white rounded-2xl shadow-lg border overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                      reco.niveau_goulot === 'CRITIQUE' 
                        ? 'border-red-200 hover:border-red-300' 
                        : reco.niveau_goulot === 'MAJEUR'
                        ? 'border-orange-200 hover:border-orange-300'
                        : 'border-yellow-200 hover:border-yellow-300'
                    }`}
                  >
                    {/* Priority Indicator Bar */}
                    <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${
                      reco.niveau_goulot === 'CRITIQUE' 
                        ? 'bg-gradient-to-b from-red-400 to-red-600' 
                        : reco.niveau_goulot === 'MAJEUR'
                        ? 'bg-gradient-to-b from-orange-400 to-orange-600'
                        : 'bg-gradient-to-b from-yellow-400 to-yellow-600'
                    }`}></div>
                    
                    <div className="p-6 pl-8">
                      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                        {/* Main Content */}
                        <div className="flex-1">
                          {/* Header */}
                          <div className="flex flex-wrap items-center gap-3 mb-3">
                            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                              reco.niveau_goulot === 'CRITIQUE' 
                                ? 'bg-red-100 text-red-700 ring-1 ring-red-200' 
                                : reco.niveau_goulot === 'MAJEUR'
                                ? 'bg-orange-100 text-orange-700 ring-1 ring-orange-200'
                                : 'bg-yellow-100 text-yellow-700 ring-1 ring-yellow-200'
                            }`}>
                              {reco.niveau_goulot === 'CRITIQUE' && <AlertTriangle className="w-3 h-3" />}
                              {reco.niveau_goulot === 'MAJEUR' && <TrendingUp className="w-3 h-3" />}
                              {reco.niveau_goulot === 'MINEUR' && <Activity className="w-3 h-3" />}
                              {reco.niveau_goulot}
                            </span>
                            <span className="text-sm text-gray-400">#{idx + 1}</span>
                          </div>
                          
                          {/* Action Title */}
                          <h3 className="text-lg font-bold text-gray-800 mb-2 group-hover:text-emerald-700 transition-colors">
                            {reco.action}
                          </h3>
                          
                          {/* Recommendation Text */}
                          <p className="text-gray-600 mb-4 leading-relaxed">{reco.recommandation}</p>
                          
                          {/* Metrics Grid */}
                          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                            <div className="bg-gray-50 rounded-xl p-3 text-center">
                              <p className="text-xs text-gray-500 mb-1">Score</p>
                              <p className="text-lg font-bold text-gray-800">{reco.score}</p>
                            </div>
                            <div className="bg-gray-50 rounded-xl p-3 text-center">
                              <p className="text-xs text-gray-500 mb-1">% Workflow</p>
                              <p className="text-lg font-bold text-gray-800">{reco.pct_workflow}%</p>
                            </div>
                            <div className="bg-gray-50 rounded-xl p-3 text-center">
                              <p className="text-xs text-gray-500 mb-1">Variabilité</p>
                              <p className="text-lg font-bold text-gray-800">{reco.cv_pct}%</p>
                            </div>
                            <div className="bg-gray-50 rounded-xl p-3 text-center">
                              <p className="text-xs text-gray-500 mb-1">Occurrences</p>
                              <p className="text-lg font-bold text-gray-800">{reco.nb_occurrences}</p>
                            </div>
                            <div className="bg-gray-50 rounded-xl p-3 text-center">
                              <p className="text-xs text-gray-500 mb-1">Agents</p>
                              <p className="text-lg font-bold text-gray-800">{reco.nb_agents_impliques}</p>
                            </div>
                          </div>
                        </div>
                        
                        {/* Gain Potentiel Card */}
                        <div className="lg:ml-6 flex-shrink-0">
                          <div className={`relative overflow-hidden rounded-2xl p-5 text-center min-w-[140px] ${
                            reco.niveau_goulot === 'CRITIQUE' 
                              ? 'bg-gradient-to-br from-red-500 to-rose-600' 
                              : reco.niveau_goulot === 'MAJEUR'
                              ? 'bg-gradient-to-br from-orange-500 to-amber-600'
                              : 'bg-gradient-to-br from-yellow-500 to-amber-500'
                          }`}>
                            <div className="absolute top-0 right-0 w-16 h-16 bg-white/10 rounded-full -translate-y-8 translate-x-8"></div>
                            <div className="relative z-10">
                              <p className="text-white/80 text-xs font-medium mb-1">Gain potentiel</p>
                              <p className="text-4xl font-black text-white">
                                +{reco.gain_potentiel_h}h
                              </p>
                              <div className="mt-2 pt-2 border-t border-white/20">
                                <p className="text-white/70 text-xs">
                                  {((reco.gain_potentiel_h / (recoData?.total_gain_heures || 1)) * 100).toFixed(0)}% du total
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Empty State */}
              {(!recoData?.recommandations || recoData.recommandations.length === 0) && (
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-12 text-center">
                  <div className="w-20 h-20 bg-emerald-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <CheckCircle className="w-10 h-10 text-emerald-500" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">Excellent travail !</h3>
                  <p className="text-gray-500 max-w-md mx-auto">
                    Aucune recommandation d'optimisation n'a été identifiée. Vos processus semblent fonctionner efficacement.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Analyse Dossier Tab */}
          {activeTab === 'analyse_dossier' && (
            <div className="space-y-6">
              {/* Search Section */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  Rechercher un dossier
                </h3>
                <div className="flex gap-4">
                  <div className="flex-1">
                    <input
                      type="text"
                      value={searchDossier}
                      onChange={(e) => setSearchDossier(e.target.value)}
                      placeholder="Filtrer par référence (ex: DAZI-2025-0018)..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  {selectedDossierRef && (
                    <button
                      onClick={() => {
                        setSelectedDossierRef(null)
                        setSearchDossier('')
                      }}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                    >
                      Nouvelle recherche
                    </button>
                  )}
                </div>

                {/* Dossiers List */}
                {loadingAllDossiers && (
                  <div className="mt-4 text-center text-gray-500">Chargement des dossiers...</div>
                )}
                
                {!loadingAllDossiers && !selectedDossierRef && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-500 mb-2">{filteredDossiers.length} dossier(s) {searchDossier ? 'correspondant(s)' : 'disponible(s)'}</p>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {filteredDossiers.map((dossier) => (
                        <div
                          key={dossier.dossier_reference}
                          onClick={() => setSelectedDossierRef(dossier.dossier_reference)}
                          className={`p-3 border rounded-lg cursor-pointer hover:bg-blue-50 transition-colors ${
                            dossier.a_des_retards ? 'border-orange-300 bg-orange-50' : 'border-gray-200'
                          }`}
                        >
                          <div className="flex justify-between items-center">
                            <div>
                              <span className="font-medium text-blue-600">{dossier.dossier_reference}</span>
                              <span className="text-gray-500 text-sm ml-2">
                                {dossier.nb_etapes} étapes
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-sm text-gray-600">
                                Durée totale: {dossier.duree_totale_minutes ? Math.round(dossier.duree_totale_minutes) + ' min' : '-'}
                              </span>
                              {dossier.a_des_retards && (
                                <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-xs">
                                  Retards détectés
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Dossier Analysis - Redesigned */}
              {selectedDossierRef && (
                <div className="space-y-6">
                  {loadingAnalyseDossier ? (
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl p-12 text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                      <p className="text-gray-600 font-medium">Analyse en cours...</p>
                    </div>
                  ) : analyseDossierData ? (
                    <>
                      {/* Hero Header Section */}
                      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 rounded-2xl p-8 text-white">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full -translate-y-32 translate-x-32"></div>
                        <div className="absolute bottom-0 left-0 w-48 h-48 bg-indigo-500/20 rounded-full translate-y-24 -translate-x-24"></div>
                        
                        <div className="relative z-10">
                          <div className="flex items-center justify-between mb-6">
                            <div>
                              <p className="text-blue-200 text-sm font-medium mb-1">Dossier en analyse</p>
                              <h2 className="text-3xl font-bold tracking-tight">{selectedDossierRef}</h2>
                            </div>
                            <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
                              (analyseDossierData.resume?.nb_retards_critiques || 0) > 0 
                                ? 'bg-red-500/20 text-red-300 border border-red-400/30'
                                : (analyseDossierData.resume?.nb_retards || 0) > 0
                                  ? 'bg-orange-500/20 text-orange-300 border border-orange-400/30'
                                  : 'bg-green-500/20 text-green-300 border border-green-400/30'
                            }`}>
                              {(analyseDossierData.resume?.nb_retards_critiques || 0) > 0 
                                ? `🔴 ${analyseDossierData.resume.nb_retards_critiques} retard(s) critique(s)`
                                : (analyseDossierData.resume?.nb_retards || 0) > 0
                                  ? `⚠️ ${analyseDossierData.resume.nb_retards} retard(s) détecté(s)`
                                  : '✅ Aucun retard'}
                            </div>
                          </div>
                          
                          {/* Key Metrics Grid */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                              <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-500/30 rounded-lg">
                                  <Activity className="w-5 h-5 text-blue-300" />
                                </div>
                                <div>
                                  <p className="text-3xl font-bold">{analyseDossierData.resume?.nb_etapes || 0}</p>
                                  <p className="text-blue-200 text-xs">Étapes</p>
                                </div>
                              </div>
                            </div>
                            
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                              <div className="flex items-center gap-3">
                                <div className="p-2 bg-purple-500/30 rounded-lg">
                                  <Clock className="w-5 h-5 text-purple-300" />
                                </div>
                                <div>
                                  <p className="text-3xl font-bold">
                                    {analyseDossierData.resume?.temps_total_reel_heures 
                                      ? `${analyseDossierData.resume.temps_total_reel_heures.toFixed(1)}h`
                                      : `${Math.round(analyseDossierData.resume?.temps_total_reel_min || 0)}m`}
                                  </p>
                                  <p className="text-purple-200 text-xs">Durée réelle</p>
                                </div>
                              </div>
                            </div>
                            
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                              <div className="flex items-center gap-3">
                                <div className="p-2 bg-green-500/30 rounded-lg">
                                  <Target className="w-5 h-5 text-green-300" />
                                </div>
                                <div>
                                  <p className="text-3xl font-bold">
                                    {analyseDossierData.resume?.temps_total_benchmark_heures 
                                      ? `${analyseDossierData.resume.temps_total_benchmark_heures.toFixed(1)}h`
                                      : `${Math.round(analyseDossierData.resume?.temps_total_benchmark_min || 0)}m`}
                                  </p>
                                  <p className="text-green-200 text-xs">Benchmark</p>
                                </div>
                              </div>
                            </div>
                            
                            <div className={`bg-white/10 backdrop-blur-sm rounded-xl p-4 border ${
                              (analyseDossierData.resume?.ecart_total_min || 0) > 0 
                                ? 'border-red-400/30' : 'border-green-400/30'
                            }`}>
                              <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${
                                  (analyseDossierData.resume?.ecart_total_min || 0) > 0 
                                    ? 'bg-red-500/30' : 'bg-green-500/30'
                                }`}>
                                  {(analyseDossierData.resume?.ecart_total_min || 0) > 0 
                                    ? <ArrowUp className="w-5 h-5 text-red-300" />
                                    : <ArrowDown className="w-5 h-5 text-green-300" />}
                                </div>
                                <div>
                                  <p className={`text-3xl font-bold ${
                                    (analyseDossierData.resume?.ecart_total_min || 0) > 0 
                                      ? 'text-red-300' : 'text-green-300'
                                  }`}>
                                    {(analyseDossierData.resume?.ecart_total_min || 0) > 0 ? '+' : ''}
                                    {analyseDossierData.resume?.ecart_total_pct 
                                      ? `${Math.round(analyseDossierData.resume.ecart_total_pct)}%`
                                      : `${Math.round(analyseDossierData.resume?.ecart_total_min || 0)}m`}
                                  </p>
                                  <p className={`text-xs ${
                                    (analyseDossierData.resume?.ecart_total_min || 0) > 0 
                                      ? 'text-red-200' : 'text-green-200'
                                  }`}>Écart</p>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Timeline Info */}
                          {analyseDossierData.resume?.date_debut && (
                            <div className="mt-6 flex items-center gap-4 text-sm text-blue-200">
                              <span>📅 Début: {new Date(analyseDossierData.resume.date_debut).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                              {analyseDossierData.resume?.date_fin && (
                                <span>→ Fin: {new Date(analyseDossierData.resume.date_fin).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Points de Retard - Modern Cards */}
                      {analyseDossierData.points_retard?.length > 0 && (
                        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                          <div className="bg-gradient-to-r from-red-500 to-orange-500 px-6 py-4">
                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                              <AlertTriangle className="w-5 h-5" />
                              {analyseDossierData.points_retard.length} Point(s) de retard identifié(s)
                            </h3>
                          </div>
                          <div className="p-6">
                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                              {analyseDossierData.points_retard.map((retard, idx) => (
                                <div 
                                  key={idx}
                                  className={`relative group rounded-xl p-5 transition-all duration-300 hover:shadow-lg hover:-translate-y-1 ${
                                    retard.statut === 'RETARD_CRITIQUE' 
                                      ? 'bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-200' 
                                      : retard.statut === 'RETARD_MODERE' 
                                        ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-2 border-orange-200' 
                                        : 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-2 border-yellow-200'
                                  }`}
                                >
                                  {/* Severity Badge */}
                                  <div className={`absolute -top-3 -right-3 px-3 py-1 rounded-full text-xs font-bold shadow-md ${
                                    retard.statut === 'RETARD_CRITIQUE' 
                                      ? 'bg-red-500 text-white' 
                                      : retard.statut === 'RETARD_MODERE' 
                                        ? 'bg-orange-500 text-white' 
                                        : 'bg-yellow-500 text-white'
                                  }`}>
                                    #{idx + 1}
                                  </div>
                                  
                                  <div className="mb-3">
                                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${
                                      retard.statut === 'RETARD_CRITIQUE' ? 'bg-red-200 text-red-800' :
                                      retard.statut === 'RETARD_MODERE' ? 'bg-orange-200 text-orange-800' :
                                      'bg-yellow-200 text-yellow-800'
                                    }`}>
                                      {retard.statut?.replace('RETARD_', '')}
                                    </span>
                                  </div>
                                  
                                  <h4 className="font-bold text-gray-800 mb-3 line-clamp-2">{retard.etape}</h4>
                                  
                                  <div className="space-y-2 text-sm">
                                    <div className="flex justify-between items-center">
                                      <span className="text-gray-500">Durée réelle</span>
                                      <span className="font-semibold text-gray-700">{formatDuration(retard.duree_reelle_min)}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-gray-500">Benchmark</span>
                                      <span className="font-semibold text-gray-700">{formatDuration(retard.benchmark_min)}</span>
                                    </div>
                                    {retard.agent && (
                                      <div className="flex justify-between items-center">
                                        <span className="text-gray-500">Agent</span>
                                        <span className="font-semibold text-gray-700 text-right truncate max-w-[120px]">{retard.agent}</span>
                                      </div>
                                    )}
                                  </div>
                                  
                                  <div className="mt-4 pt-3 border-t border-gray-200">
                                    <div className="flex justify-between items-center">
                                      <span className="text-gray-600 font-medium">Écart</span>
                                      <div className="text-right">
                                        <p className={`text-xl font-bold ${
                                          retard.statut === 'RETARD_CRITIQUE' ? 'text-red-600' :
                                          retard.statut === 'RETARD_MODERE' ? 'text-orange-600' :
                                          'text-yellow-600'
                                        }`}>
                                          +{formatDuration(retard.ecart_min)}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                          {retard.ecart_pct > 0 ? `+${Math.round(retard.ecart_pct)}%` : ''}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Visual Timeline - Modern Design */}
                      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
                          <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <Activity className="w-5 h-5" />
                            Parcours du dossier
                          </h3>
                        </div>
                        <div className="p-6">
                          {/* Comparison Bar Chart */}
                          <div className="mb-8">
                            <p className="text-sm text-gray-500 mb-4">Comparaison durée réelle vs benchmark par étape</p>
                            <ResponsiveContainer width="100%" height={Math.max(300, analyseDossierData.parcours?.length * 45 || 300)}>
                              <BarChart 
                                layout="vertical" 
                                data={analyseDossierData.parcours?.map(e => ({
                                  name: (e.action_libelle || e.action || '').substring(0, 25) + ((e.action_libelle || e.action || '').length > 25 ? '...' : ''),
                                  fullName: e.action_libelle || e.action,
                                  duree_reelle: Math.round(e.duree_reelle_min || 0),
                                  benchmark: Math.round(e.benchmark_min || 0),
                                  statut: e.statut_temps
                                })) || []}
                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                              >
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis type="number" tick={{ fontSize: 11 }} />
                                <YAxis dataKey="name" type="category" width={180} tick={{ fontSize: 11 }} />
                                <Tooltip 
                                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: 'white' }}
                                  formatter={(value, name) => [
                                    `${value} min`, 
                                    name === 'duree_reelle' ? 'Durée réelle' : 'Benchmark'
                                  ]}
                                  labelFormatter={(label, payload) => payload[0]?.payload?.fullName || label}
                                />
                                <Legend 
                                  formatter={(value) => value === 'duree_reelle' ? 'Durée réelle' : 'Benchmark'}
                                />
                                <Bar dataKey="benchmark" fill="#94a3b8" radius={[0, 4, 4, 0]} name="benchmark" />
                                <Bar 
                                  dataKey="duree_reelle" 
                                  radius={[0, 4, 4, 0]} 
                                  name="duree_reelle"
                                  fill="#3b82f6"
                                >
                                  {analyseDossierData.parcours?.map((entry, index) => (
                                    <Cell 
                                      key={`cell-${index}`} 
                                      fill={
                                        entry.statut_temps?.includes('RETARD_CRITIQUE') ? '#ef4444' :
                                        entry.statut_temps?.includes('RETARD') ? '#f97316' :
                                        entry.statut_temps === 'RAPIDE' ? '#22c55e' : '#3b82f6'
                                      } 
                                    />
                                  ))}
                                </Bar>
                              </BarChart>
                            </ResponsiveContainer>
                          </div>

                          {/* Modern Timeline */}
                          <div className="border-t border-gray-100 pt-6">
                            <p className="text-sm text-gray-500 mb-4">Timeline détaillée</p>
                            <div className="relative">
                              {/* Timeline line */}
                              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-purple-500 to-indigo-500"></div>
                              
                              {analyseDossierData.parcours?.map((etape, idx) => {
                                const isDelayed = etape.statut_temps?.includes('RETARD')
                                const isFast = etape.statut_temps === 'RAPIDE'
                                
                                return (
                                  <div key={idx} className="relative pl-16 pb-8 last:pb-0">
                                    {/* Timeline node */}
                                    <div className={`absolute left-4 w-5 h-5 rounded-full border-4 ${
                                      isDelayed ? 'bg-red-500 border-red-200' :
                                      isFast ? 'bg-green-500 border-green-200' :
                                      'bg-blue-500 border-blue-200'
                                    } shadow-lg`}>
                                      <span className="absolute -left-1 -top-1 w-7 h-7 rounded-full animate-ping opacity-20" style={{
                                        backgroundColor: isDelayed ? '#ef4444' : isFast ? '#22c55e' : '#3b82f6'
                                      }}></span>
                                    </div>
                                    
                                    {/* Step number */}
                                    <div className="absolute left-0 top-0 w-3 h-5 flex items-center justify-center">
                                      <span className="text-xs font-bold text-gray-400">{etape.ordre_etape}</span>
                                    </div>
                                    
                                    {/* Content card */}
                                    <div className={`rounded-xl p-4 transition-all duration-300 hover:shadow-md ${
                                      isDelayed ? 'bg-red-50 border border-red-200' :
                                      isFast ? 'bg-green-50 border border-green-200' :
                                      'bg-gray-50 border border-gray-200'
                                    }`}>
                                      <div className="flex flex-wrap items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                          <h4 className="font-semibold text-gray-800 mb-1">
                                            {etape.action_libelle || etape.action}
                                          </h4>
                                          <div className="flex flex-wrap items-center gap-2 text-xs">
                                            {etape.nom_agent && (
                                              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-white rounded-full text-gray-600">
                                                <Users className="w-3 h-3" />
                                                {etape.nom_agent}
                                              </span>
                                            )}
                                            {etape.categorie_etape && (
                                              <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full">
                                                {etape.categorie_etape}
                                              </span>
                                            )}
                                          </div>
                                        </div>
                                        
                                        <div className="flex items-center gap-3">
                                          <div className="text-right">
                                            <p className={`text-lg font-bold ${
                                              isDelayed ? 'text-red-600' :
                                              isFast ? 'text-green-600' : 'text-gray-700'
                                            }`}>
                                              {formatDuration(etape.duree_reelle_min)}
                                            </p>
                                            {etape.benchmark_min && (
                                              <p className="text-xs text-gray-500">
                                                vs {formatDuration(etape.benchmark_min)}
                                              </p>
                                            )}
                                          </div>
                                          <span className={`px-2 py-1 rounded-lg text-xs font-semibold ${
                                            etape.statut_temps === 'RETARD_CRITIQUE' ? 'bg-red-500 text-white' :
                                            etape.statut_temps === 'RETARD_MODERE' ? 'bg-orange-500 text-white' :
                                            etape.statut_temps === 'RETARD_LEGER' ? 'bg-yellow-500 text-white' :
                                            etape.statut_temps === 'RAPIDE' ? 'bg-green-500 text-white' :
                                            'bg-gray-400 text-white'
                                          }`}>
                                            {etape.statut_temps === 'RETARD_CRITIQUE' ? '🔴 Critique' :
                                             etape.statut_temps === 'RETARD_MODERE' ? '🟠 Modéré' :
                                             etape.statut_temps === 'RETARD_LEGER' ? '🟡 Léger' :
                                             etape.statut_temps === 'RAPIDE' ? '🟢 Rapide' :
                                             '⚪ Normal'}
                                          </span>
                                        </div>
                                      </div>
                                      
                                      {/* Progress bar */}
                                      {etape.benchmark_min > 0 && (
                                        <div className="mt-3">
                                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                            <div 
                                              className={`h-full rounded-full transition-all ${
                                                isDelayed ? 'bg-gradient-to-r from-red-400 to-red-500' :
                                                isFast ? 'bg-gradient-to-r from-green-400 to-green-500' :
                                                'bg-gradient-to-r from-blue-400 to-blue-500'
                                              }`}
                                              style={{ 
                                                width: `${Math.min(100, ((etape.duree_reelle_min || 0) / etape.benchmark_min) * 100)}%` 
                                              }}
                                            />
                                          </div>
                                          <div className="flex justify-between mt-1 text-xs text-gray-500">
                                            <span>0</span>
                                            <span className="font-medium">
                                              {etape.ecart_min > 0 ? `+${formatDuration(etape.ecart_min)}` : 
                                               etape.ecart_min < 0 ? `-${formatDuration(Math.abs(etape.ecart_min))}` : 'Dans les temps'}
                                            </span>
                                            <span>{formatDuration(etape.benchmark_min)}</span>
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )
                              })}
                            </div>
                          </div>

                          {/* Legend */}
                          <div className="mt-6 pt-4 border-t border-gray-100 flex flex-wrap justify-center gap-4 text-xs">
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 rounded-full bg-red-500"></span>
                              <span className="text-gray-600">Retard critique</span>
                            </span>
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 rounded-full bg-orange-500"></span>
                              <span className="text-gray-600">Retard modéré</span>
                            </span>
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                              <span className="text-gray-600">Retard léger</span>
                            </span>
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 rounded-full bg-green-500"></span>
                              <span className="text-gray-600">Rapide</span>
                            </span>
                            <span className="flex items-center gap-1.5">
                              <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                              <span className="text-gray-600">Normal</span>
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Detailed Table - Collapsible */}
                      <details className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                        <summary className="bg-gradient-to-r from-gray-600 to-gray-700 px-6 py-4 cursor-pointer hover:from-gray-700 hover:to-gray-800 transition-colors">
                          <h3 className="text-lg font-bold text-white inline-flex items-center gap-2">
                            <ChevronDown className="w-5 h-5" />
                            Tableau détaillé du parcours
                          </h3>
                        </summary>
                        <div className="p-6 overflow-x-auto">
                          <table className="min-w-full">
                            <thead>
                              <tr className="bg-gray-50">
                                <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider rounded-l-lg">
                                  #
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                                  Étape
                                </th>
                                <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                                  Agent
                                </th>
                                <th className="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">
                                  Durée
                                </th>
                                <th className="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">
                                  Benchmark
                                </th>
                                <th className="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider">
                                  Écart
                                </th>
                                <th className="px-4 py-3 text-center text-xs font-bold text-gray-600 uppercase tracking-wider rounded-r-lg">
                                  Statut
                                </th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                              {analyseDossierData.parcours?.map((etape, idx) => (
                                <tr 
                                  key={idx}
                                  className={`transition-colors hover:bg-gray-50 ${
                                    etape.statut_temps?.includes('RETARD') ? 'bg-red-50/50' :
                                    etape.statut_temps === 'RAPIDE' ? 'bg-green-50/50' : ''
                                  }`}
                                >
                                  <td className="px-4 py-4">
                                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-gray-600 font-bold text-sm">
                                      {etape.ordre_etape}
                                    </span>
                                  </td>
                                  <td className="px-4 py-4">
                                    <p className="font-medium text-gray-800">{etape.action_libelle || etape.action}</p>
                                    {etape.categorie_etape && (
                                      <p className="text-xs text-gray-500 mt-0.5">{etape.categorie_etape}</p>
                                    )}
                                  </td>
                                  <td className="px-4 py-4 text-sm text-gray-600">
                                    {etape.nom_agent || '-'}
                                  </td>
                                  <td className="px-4 py-4 text-center">
                                    <span className="font-semibold text-gray-800">
                                      {formatDuration(etape.duree_reelle_min)}
                                    </span>
                                  </td>
                                  <td className="px-4 py-4 text-center text-sm text-gray-500">
                                    {etape.benchmark_min ? formatDuration(etape.benchmark_min) : '-'}
                                  </td>
                                  <td className={`px-4 py-4 text-center font-semibold ${
                                    etape.ecart_min > 0 ? 'text-red-600' :
                                    etape.ecart_min < 0 ? 'text-green-600' : 'text-gray-500'
                                  }`}>
                                    {etape.ecart_min !== null && etape.ecart_min !== undefined ? (
                                      <>
                                        {etape.ecart_min > 0 ? '+' : ''}
                                        {formatDuration(etape.ecart_min)}
                                      </>
                                    ) : '-'}
                                  </td>
                                  <td className="px-4 py-4 text-center">
                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                                      etape.statut_temps === 'RETARD_CRITIQUE' ? 'bg-red-100 text-red-700' :
                                      etape.statut_temps === 'RETARD_MODERE' ? 'bg-orange-100 text-orange-700' :
                                      etape.statut_temps === 'RETARD_LEGER' ? 'bg-yellow-100 text-yellow-700' :
                                      etape.statut_temps === 'RAPIDE' ? 'bg-green-100 text-green-700' :
                                      'bg-gray-100 text-gray-700'
                                    }`}>
                                      {etape.statut_temps?.replace('RETARD_', '').replace('_', ' ') || 'Normal'}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </details>
                    </>
                  ) : (
                    <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-12 text-center">
                      <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                        <Search className="w-8 h-8 text-gray-400" />
                      </div>
                      <p className="text-gray-500 font-medium">Aucune donnée trouvée pour ce dossier</p>
                    </div>
                  )}
                </div>
              )}

              {/* Help Section */}
              {!selectedDossierRef && !searchDossier && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-blue-800 mb-3">
                    Comment utiliser l'analyse de dossier ?
                  </h3>
                  <ul className="space-y-2 text-blue-700">
                    <li className="flex items-start gap-2">
                      <span className="font-bold">1.</span>
                      <span>Entrez la référence du dossier que vous souhaitez analyser (ex: DAZI-2025-0018)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold">2.</span>
                      <span>Sélectionnez le dossier dans les résultats de recherche</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold">3.</span>
                      <span>Visualisez le parcours complet avec les points de retard identifiés</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-bold">4.</span>
                      <span>Comparez la durée réelle de chaque étape avec le benchmark pour identifier les anomalies</span>
                    </li>
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
