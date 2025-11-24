import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts'
import { 
  DollarSign, TrendingUp, TrendingDown, Calendar, 
  AlertTriangle, CheckCircle, Target, BarChart3,
  PieChart as PieChartIcon, TrendingDown as ArrowDown,
  TrendingUp as ArrowUp
} from 'lucide-react'
import { financierAPI } from '../services/api'
import StatsCard from '../components/StatsCard'
import ExportButton from '../components/ExportButton'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']

export default function Financier() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  
  // Requêtes API
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['financier-summary', selectedYear],
    queryFn: () => financierAPI.getSummary({ annee: selectedYear }).then(res => res.data),
  })

  const { data: tendancesMensuelles } = useQuery({
    queryKey: ['financier-tendances-mensuelles', selectedYear],
    queryFn: () => financierAPI.getTendancesMensuelles(selectedYear).then(res => res.data),
  })

  const { data: tendancesTrimestrielles } = useQuery({
    queryKey: ['financier-tendances-trimestrielles', selectedYear],
    queryFn: () => financierAPI.getTendancesTrimestrielles(selectedYear).then(res => res.data),
  })

  const { data: topZones } = useQuery({
    queryKey: ['financier-top-zones', selectedYear],
    queryFn: () => financierAPI.getTopZonesPerformance(selectedYear, 5).then(res => res.data),
  })

  const { data: comparaison } = useQuery({
    queryKey: ['financier-comparaison', selectedYear],
    queryFn: () => financierAPI.getComparaisonAnnuelle(selectedYear).then(res => res.data),
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

  // Préparer données pour export
  const prepareExportData = () => {
    const data = [];
    
    if (summary) {
      data.push({
        'Métrique': 'CA Facturé',
        'Valeur': summary.ca_total,
        'Format': formatCurrency(summary.ca_total)
      });
      data.push({
        'Métrique': 'CA Payé',
        'Valeur': summary.ca_paye,
        'Format': formatCurrency(summary.ca_paye)
      });
      data.push({
        'Métrique': 'Créances',
        'Valeur': summary.ca_impaye,
        'Format': formatCurrency(summary.ca_impaye)
      });
      data.push({
        'Métrique': 'Taux de Paiement',
        'Valeur': summary.taux_paiement_moyen,
        'Format': formatPercent(summary.taux_paiement_moyen)
      });
    }

    if (topZones?.top_chiffre_affaires) {
      data.push({ 'Métrique': '', 'Valeur': '', 'Format': '' });
      data.push({ 'Métrique': 'TOP ZONES PAR CA', 'Valeur': '', 'Format': '' });
      topZones.top_chiffre_affaires.forEach((zone, index) => {
        data.push({
          'Métrique': `${index + 1}. ${zone.nom_zone}`,
          'Valeur': zone.ca_total,
          'Format': formatCurrency(zone.ca_total) + ` - Taux: ${formatPercent(zone.taux_paiement)}`
        });
      });
    }

    return data;
  };

  // Pas besoin de fonctions séparées - ExportButton gère tout

  return (
    <div className="space-y-8">
      {/* Header Principal */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Performance Financière</h2>
        <ExportButton 
          data={prepareExportData()} 
          filename={`financier_${selectedYear}`}
          title={`Dashboard Financier - ${selectedYear}`}
          showPDF={true}
          showExcel={true}
          showCSV={true}
        />
      </div>

      {/* Contrôles et Comparaison */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-gray-400" />
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          >
            <option value={2023}>2023</option>
            <option value={2024}>2024</option>
            <option value={2025}>2025</option>
          </select>
        </div>
        
        {/* Comparaison année vs année */}
        {comparaison && comparaison.variations && (
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-xs text-gray-500">vs {comparaison.annee_precedente}</p>
              <div className="flex items-center space-x-1">
                {comparaison.variations.ca_total >= 0 ? (
                  <ArrowUp className="w-4 h-4 text-green-600" />
                ) : (
                  <ArrowDown className="w-4 h-4 text-red-600" />
                )}
                <span className={`text-sm font-semibold ${
                  comparaison.variations.ca_total >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {Math.abs(comparaison.variations.ca_total || 0).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* KPIs Principaux */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <BarChart3 className="w-6 h-6 mr-2 text-blue-600" />
          Vue d'Ensemble Financière
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="CA Facturé"
            value={formatCurrencyShort(summary?.ca_total) + ' FCFA'}
            subtitle={`${formatCurrency(summary?.ca_total)}`}
            icon={DollarSign}
            color="blue"
            loading={summaryLoading}
          />
          <StatsCard
            title="CA Payé"
            value={formatCurrencyShort(summary?.ca_paye) + ' FCFA'}
            subtitle={formatPercent(summary?.taux_paiement_moyen)}
            icon={CheckCircle}
            color="green"
            loading={summaryLoading}
          />
          <StatsCard
            title="Créances"
            value={formatCurrencyShort(summary?.ca_impaye) + ' FCFA'}
            subtitle={formatPercent(summary?.taux_impaye_pct) + ' du CA'}
            icon={AlertTriangle}
            color="orange"
            loading={summaryLoading}
          />
          <StatsCard
            title="Nombre Factures"
            value={summary?.total_factures?.toLocaleString('fr-FR') || '0'}
            subtitle="Factures émises"
            icon={DollarSign}
            color="purple"
            loading={summaryLoading}
          />
        </div>
      </section>

      {/* Recouvrement */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Target className="w-6 h-6 mr-2 text-blue-600" />
          Analyse du Recouvrement
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard
            title="Montant Recouvré"
            value={formatCurrencyShort(summary?.montant_recouvre) + ' FCFA'}
            subtitle={`${summary?.total_collectes || 0} collectes`}
            icon={TrendingUp}
            color="green"
          />
          <StatsCard
            title="Taux Recouvrement"
            value={formatPercent(summary?.taux_recouvrement_moyen)}
            subtitle="Sur créances totales"
            icon={Target}
            color="blue"
          />
          <StatsCard
            title="Montant À Recouvrer"
            value={formatCurrencyShort(summary?.montant_a_recouvrer) + ' FCFA'}
            subtitle="Objectif collecte"
            icon={AlertTriangle}
            color="red"
          />
        </div>
      </section>

      {/* Graphiques de Tendances */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Évolution Mensuelle */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Évolution Mensuelle {selectedYear}
          </h4>
          {tendancesMensuelles && tendancesMensuelles.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={tendancesMensuelles}>
                <defs>
                  <linearGradient id="colorFacture" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPaye" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nom_mois" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  formatter={(value) => formatCurrency(value)}
                  contentStyle={{ borderRadius: '8px' }}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="ca_facture" 
                  stroke="#0ea5e9" 
                  fillOpacity={1} 
                  fill="url(#colorFacture)" 
                  name="CA Facturé"
                />
                <Area 
                  type="monotone" 
                  dataKey="ca_paye" 
                  stroke="#10b981" 
                  fillOpacity={1} 
                  fill="url(#colorPaye)" 
                  name="CA Payé"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              Aucune donnée disponible
            </div>
          )}
        </div>

        {/* Performance Trimestrielle */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Performance Trimestrielle
          </h4>
          {tendancesTrimestrielles && tendancesTrimestrielles.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={tendancesTrimestrielles} margin={{ top: 20, right: 30, left: 60, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="nom_trimestre"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  label={{ value: 'Montant (FCFA)', angle: -90, position: 'insideLeft' }}
                  tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={(value) => formatCurrency(value)}
                  labelFormatter={(label) => `Montant: ${label}`}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="ca_facture" fill="#0ea5e9" name="CA Facturé" radius={[8, 8, 0, 0]} />
                <Bar dataKey="ca_paye" fill="#10b981" name="CA Payé" radius={[8, 8, 0, 0]} />
                <Bar dataKey="ca_impaye" fill="#f59e0b" name="Créances" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-400 flex items-center justify-center text-gray-500">
              Aucune donnée disponible
            </div>
          )}
        </div>
      </div>

      {/* Top Zones */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top CA */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <DollarSign className="w-5 h-5 mr-2 text-blue-600" />
            Top Zones par CA
          </h4>
          <div className="space-y-3">
            {topZones?.top_chiffre_affaires?.map((zone, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{zone.nom_zone}</p>
                    <p className="text-xs text-gray-500">
                      Taux: {formatPercent(zone.taux_paiement)}
                    </p>
                  </div>
                </div>
                <span className="text-sm font-bold text-blue-600">
                  {formatCurrencyShort(zone.ca_total)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Meilleurs Payeurs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
            Meilleurs Payeurs
          </h4>
          <div className="space-y-3">
            {topZones?.meilleurs_payeurs?.map((zone, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{zone.nom_zone}</p>
                    <p className="text-xs text-gray-500">
                      CA: {formatCurrencyShort(zone.ca_total)}
                    </p>
                  </div>
                </div>
                <span className="text-lg font-bold text-green-600">
                  {formatPercent(zone.taux_paiement)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Zones à Risque */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
            Zones à Risque
          </h4>
          <div className="space-y-3">
            {topZones?.zones_a_risque && topZones.zones_a_risque.length > 0 ? (
              topZones.zones_a_risque.map((zone, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{zone.nom_zone}</p>
                      <p className="text-xs text-red-600">
                        Impayé: {formatCurrencyShort(zone.ca_impaye)}
                      </p>
                    </div>
                  </div>
                  <span className="text-lg font-bold text-red-600">
                    {formatPercent(zone.taux_paiement)}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
                <p className="text-sm">Aucune zone à risque</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recouvrement par Zone */}

    </div>
  )
}
