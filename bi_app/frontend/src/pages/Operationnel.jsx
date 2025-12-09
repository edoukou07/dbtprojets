import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { operationnelAPI } from '../services/api'
import StatsCard from '../components/StatsCard'
import { Activity, TrendingUp, CheckCircle, Clock, FileText, Users, AlertCircle, DollarSign } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Operationnel() {
  // Chargement des données
  const { data: summary } = useQuery({
    queryKey: ['operationnel-summary'],
    queryFn: async () => {
      const response = await operationnelAPI.getSummary()
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })

  const { data: performanceCollectes } = useQuery({
    queryKey: ['performance-collectes'],
    queryFn: async () => {
      const response = await operationnelAPI.getPerformanceCollectes()
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })

  const { data: performanceAttributions } = useQuery({
    queryKey: ['performance-attributions'],
    queryFn: async () => {
      const response = await operationnelAPI.getPerformanceAttributions()
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })

  const { data: performanceFacturation } = useQuery({
    queryKey: ['performance-facturation'],
    queryFn: async () => {
      const response = await operationnelAPI.getPerformanceFacturation()
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })

  const { data: indicateursCles } = useQuery({
    queryKey: ['indicateurs-cles'],
    queryFn: async () => {
      const response = await operationnelAPI.getIndicateursCles()
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })

  // Helpers de formatage
  const formatCurrency = (value) => {
    if (!value && value !== 0) return '0 FCFA'
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XOF',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatCurrencyShort = (value) => {
    if (!value && value !== 0) return '0'
    if (value >= 1000000000) {
      return (value / 1000000000).toFixed(1) + 'Md'
    } else if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M'
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K'
    }
    return value.toString()
  }

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0%'
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0%'
    return numValue.toFixed(1) + '%'
  }

  const formatNumber = (value) => {
    if (!value && value !== 0) return '0'
    return new Intl.NumberFormat('fr-FR').format(value)
  }


  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Performance Opérationnelle</h2>
      </div>

      {/* KPIs Principaux */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Activity className="w-6 h-6 mr-2 text-blue-600" />
          Indicateurs Clés de Performance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Collectes"
            value={formatNumber(summary?.total_collectes || 0)}
            icon={FileText}
            trend={null}
            color="blue"
            loading={!summary}
          />
          <StatsCard
            title="Taux de Clôture"
            value={formatPercent(summary?.taux_cloture_moyen || 0)}
            icon={CheckCircle}
            trend={null}
            color="green"
            loading={!summary}
          />
          <StatsCard
            title="Taux de Recouvrement"
            value={formatPercent(summary?.taux_recouvrement_moyen || 0)}
            icon={DollarSign}
            trend={null}
            color="purple"
            loading={!summary}
          />
          <StatsCard
            title="Total Demandes"
            value={formatNumber(summary?.total_demandes || 0)}
            icon={Users}
            trend={null}
            color="orange"
            loading={!summary}
          />
        </div>
      </section>

      {/* Indicateurs Détaillés du Trimestre */}
      {indicateursCles?.indicateurs && (
        <section>
          <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-6 h-6 mr-2 text-green-600" />
            Performance du Trimestre {indicateursCles.periode?.trimestre} - {indicateursCles.periode?.annee}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <StatsCard
              title="Collectes - Taux Clôture"
              value={formatPercent(indicateursCles.indicateurs.taux_cloture || 0)}
              icon={CheckCircle}
              trend={indicateursCles.evolution?.taux_recouvrement ? {
                value: Math.abs(indicateursCles.evolution.taux_recouvrement).toFixed(1),
                isPositive: indicateursCles.evolution.taux_recouvrement > 0
              } : null}
              color="green"
            />
            <StatsCard
              title="Collectes - Taux Recouvrement"
              value={formatPercent(indicateursCles.indicateurs.taux_recouvrement || 0)}
              icon={DollarSign}
              trend={indicateursCles.evolution?.taux_recouvrement ? {
                value: Math.abs(indicateursCles.evolution.taux_recouvrement).toFixed(1),
                isPositive: indicateursCles.evolution.taux_recouvrement > 0
              } : null}
              color="purple"
            />
            <StatsCard
              title="Collectes - Durée Moyenne"
              value={`${formatNumber(indicateursCles.indicateurs.duree_moyenne_collecte?.toFixed(0) || 0)} jours`}
              icon={Clock}
              trend={null}
              color="blue"
            />
            <StatsCard
              title="Attributions - Taux Approbation"
              value={formatPercent(indicateursCles.indicateurs.taux_approbation || 0)}
              icon={CheckCircle}
              trend={indicateursCles.evolution?.taux_approbation ? {
                value: Math.abs(indicateursCles.evolution.taux_approbation).toFixed(1),
                isPositive: indicateursCles.evolution.taux_approbation > 0
              } : null}
              color="green"
            />
            <StatsCard
              title="Attributions - Délai Moyen"
              value={`${formatNumber(indicateursCles.indicateurs.delai_moyen_attribution?.toFixed(0) || 0)} jours`}
              icon={Clock}
              trend={null}
              color="orange"
            />
            <StatsCard
              title="Facturation - Délai Paiement"
              value={`${formatNumber(indicateursCles.indicateurs.delai_moyen_paiement?.toFixed(0) || 0)} jours`}
              icon={Clock}
              trend={null}
              color="red"
            />
          </div>
        </section>
      )}

      {/* Performance Collectes */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <FileText className="w-6 h-6 mr-2 text-blue-600" />
          Performance des Collectes
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Statistiques Globales */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Vue d'Ensemble</h4>
            {performanceCollectes?.global ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Total Collectes</span>
                  <span className="text-lg font-bold text-blue-600">
                    {formatNumber(performanceCollectes.global.total_collectes || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Collectes Clôturées</span>
                  <span className="text-lg font-bold text-green-600">
                    {formatNumber(performanceCollectes.global.total_cloturees || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Collectes Ouvertes</span>
                  <span className="text-lg font-bold text-orange-600">
                    {formatNumber(performanceCollectes.global.total_ouvertes || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Taux de Clôture Moyen</span>
                  <span className="text-lg font-bold text-purple-600">
                    {formatPercent(performanceCollectes.global.taux_cloture_moyen || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-indigo-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Taux de Recouvrement</span>
                  <span className="text-lg font-bold text-indigo-600">
                    {formatPercent(performanceCollectes.global.taux_recouvrement_moyen || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Durée Moyenne</span>
                  <span className="text-lg font-bold text-gray-700">
                    {formatNumber(performanceCollectes.global.duree_moyenne_jours?.toFixed(0) || 0)} jours
                  </span>
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                Chargement...
              </div>
            )}
          </div>

          {/* Évolution Trimestrielle */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Évolution Trimestrielle</h4>
            {performanceCollectes?.par_trimestre && performanceCollectes.par_trimestre.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceCollectes.par_trimestre}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="trimestre" tickFormatter={(value) => `T${value}`} />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'total_collectes') return [formatNumber(value), 'Collectes']
                      if (name === 'taux_recouvrement') return [formatPercent(value), 'Taux Recouvrement']
                      return [value, name]
                    }}
                    labelFormatter={(value) => `Trimestre ${value}`}
                  />
                  <Legend />
                  <Line 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="total_collectes" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="Collectes"
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="taux_recouvrement" 
                    stroke="#8b5cf6" 
                    strokeWidth={2}
                    name="Taux (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-300 flex items-center justify-center text-gray-500">
                Aucune donnée disponible
              </div>
            )}
          </div>
        </div>

        {/* Montants Collectes */}
        {performanceCollectes?.global && (
          <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Montants des Collectes</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Montant à Recouvrer</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrencyShort(performanceCollectes.global.montant_total_a_recouvrer || 0)} FCFA
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Montant Recouvré</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrencyShort(performanceCollectes.global.montant_total_recouvre || 0)} FCFA
                </p>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Reste à Recouvrer</p>
                <p className="text-2xl font-bold text-orange-600">
                  {formatCurrencyShort(
                    (performanceCollectes.global.montant_total_a_recouvrer || 0) - 
                    (performanceCollectes.global.montant_total_recouvre || 0)
                  )} FCFA
                </p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Performance Attributions */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Users className="w-6 h-6 mr-2 text-green-600" />
          Performance des Attributions
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Statistiques Globales */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Vue d'Ensemble</h4>
            {performanceAttributions?.global ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Total Demandes</span>
                  <span className="text-lg font-bold text-blue-600">
                    {formatNumber(performanceAttributions.global.total_demandes || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Demandes Approuvées</span>
                  <span className="text-lg font-bold text-green-600">
                    {formatNumber(performanceAttributions.global.total_approuvees || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Demandes Rejetées</span>
                  <span className="text-lg font-bold text-red-600">
                    {formatNumber(performanceAttributions.global.total_rejetees || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">En Attente</span>
                  <span className="text-lg font-bold text-orange-600">
                    {formatNumber(performanceAttributions.global.total_en_attente || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Taux d'Approbation</span>
                  <span className="text-lg font-bold text-purple-600">
                    {formatPercent(performanceAttributions.global.taux_approbation_moyen || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Délai Moyen</span>
                  <span className="text-lg font-bold text-gray-700">
                    {formatNumber(performanceAttributions.global.delai_moyen_jours?.toFixed(0) || 0)} jours
                  </span>
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                Chargement...
              </div>
            )}
          </div>

          {/* Graphique Évolution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Évolution des Demandes</h4>
            {performanceAttributions?.par_trimestre && performanceAttributions.par_trimestre.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceAttributions.par_trimestre}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="trimestre" tickFormatter={(value) => `T${value}`} />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'Approuvées') return [formatNumber(value), name]
                      if (name === 'Rejetées') return [formatNumber(value), name]
                      if (name === 'En Attente') return [formatNumber(value), name]
                      return [value, name]
                    }}
                    labelFormatter={(value) => `Trimestre ${value}`}
                  />
                  <Legend />
                  <Bar dataKey="demandes_approuvees" fill="#10b981" name="Approuvées" />
                  <Bar dataKey="demandes_rejetees" fill="#ef4444" name="Rejetées" />
                  <Bar dataKey="demandes_en_attente" fill="#f59e0b" name="En Attente" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-300 flex items-center justify-center text-gray-500">
                Aucune donnée disponible
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Performance Facturation */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <DollarSign className="w-6 h-6 mr-2 text-purple-600" />
          Performance de la Facturation
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Statistiques Globales */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Vue d'Ensemble</h4>
            {performanceFacturation?.global ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Factures Émises</span>
                  <span className="text-lg font-bold text-blue-600">
                    {formatNumber(performanceFacturation.global.total_factures_emises || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Factures Payées</span>
                  <span className="text-lg font-bold text-green-600">
                    {formatNumber(performanceFacturation.global.total_factures_payees || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Taux de Paiement</span>
                  <span className="text-lg font-bold text-purple-600">
                    {formatPercent(performanceFacturation.global.taux_paiement_pct || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-indigo-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Taux de Recouvrement</span>
                  <span className="text-lg font-bold text-indigo-600">
                    {formatPercent(performanceFacturation.global.taux_recouvrement_pct || 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Délai Moyen de Paiement</span>
                  <span className="text-lg font-bold text-gray-700">
                    {formatNumber(performanceFacturation.global.delai_moyen_paiement?.toFixed(0) || 0)} jours
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-emerald-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Montant Total Facturé</span>
                  <span className="text-lg font-bold text-emerald-600">
                    {formatCurrencyShort(performanceFacturation.global.montant_total_facture || 0)} FCFA
                  </span>
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                Chargement...
              </div>
            )}
          </div>

          {/* Graphique Montants */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Évolution des Montants</h4>
            {performanceFacturation?.par_trimestre && performanceFacturation.par_trimestre.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={performanceFacturation.par_trimestre}>
                  <defs>
                    <linearGradient id="colorFacture" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorPaye" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="trimestre" tickFormatter={(value) => `T${value}`} />
                  <YAxis tickFormatter={(value) => formatCurrencyShort(value)} />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'Facturé') return [formatCurrencyShort(value) + ' FCFA', name]
                      if (name === 'Payé') return [formatCurrencyShort(value) + ' FCFA', name]
                      return [value, name]
                    }}
                    labelFormatter={(value) => `Trimestre ${value}`}
                  />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey="montant_facture" 
                    stroke="#3b82f6" 
                    fillOpacity={1} 
                    fill="url(#colorFacture)"
                    name="Facturé"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="montant_paye" 
                    stroke="#10b981" 
                    fillOpacity={1} 
                    fill="url(#colorPaye)"
                    name="Payé"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-300 flex items-center justify-center text-gray-500">
                Aucune donnée disponible
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
