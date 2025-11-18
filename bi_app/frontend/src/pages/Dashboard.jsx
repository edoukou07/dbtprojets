import { useQuery } from '@tanstack/react-query'
import { DollarSign, Building2, Users, Activity, TrendingUp, TrendingDown } from 'lucide-react'
import { financierAPI, occupationAPI, clientsAPI, operationnelAPI } from '../services/api'
import StatsCard from '../components/StatsCard'
import ExportButton from '../components/ExportButton'
import AlertsPanel from '../components/AlertsPanel'

export default function Dashboard() {
  const { data: financierData, isLoading: financierLoading } = useQuery({
    queryKey: ['financier-summary'],
    queryFn: () => financierAPI.getSummary().then(res => res.data),
    staleTime: 30000,
  })

  const { data: occupationData, isLoading: occupationLoading } = useQuery({
    queryKey: ['occupation-summary'],
    queryFn: () => occupationAPI.getSummary().then(res => res.data),
    staleTime: 30000,
  })

  const { data: clientsData, isLoading: clientsLoading } = useQuery({
    queryKey: ['clients-summary'],
    queryFn: () => clientsAPI.getSummary().then(res => res.data),
    staleTime: 30000,
  })

  const { data: operationnelData, isLoading: operationnelLoading } = useQuery({
    queryKey: ['operationnel-summary'],
    queryFn: () => operationnelAPI.getSummary().then(res => res.data),
    staleTime: 30000,
  })

  const formatCurrency = (value) => {
    if (!value) return '0 FCFA'
    return new Intl.NumberFormat('fr-FR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value) + ' FCFA'
  }

  const formatPercent = (value) => {
    if (!value) return '0%'
    return value.toFixed(1) + '%'
  }

  // Préparer les données pour l'export
  const exportData = [
    { Indicateur: 'CA Facturé', Valeur: financierData?.ca_total || 0, Unité: 'FCFA' },
    { Indicateur: 'CA Payé', Valeur: financierData?.ca_paye || 0, Unité: 'FCFA' },
    { Indicateur: 'Taux Paiement', Valeur: financierData?.taux_paiement_moyen || 0, Unité: '%' },
    { Indicateur: 'Taux Recouvrement', Valeur: financierData?.taux_recouvrement_moyen || 0, Unité: '%' },
    { Indicateur: 'Taux Occupation', Valeur: occupationData?.taux_occupation_moyen || 0, Unité: '%' },
    { Indicateur: 'Lots Disponibles', Valeur: occupationData?.total_lots_disponibles || 0, Unité: 'lots' },
    { Indicateur: 'Total Clients', Valeur: clientsData?.total_clients || 0, Unité: 'clients' },
    { Indicateur: 'CA Moyen par Client', Valeur: clientsData?.ca_moyen_par_client || 0, Unité: 'FCFA' },
    { Indicateur: 'Total Collectes', Valeur: operationnelData?.total_collectes || 0, Unité: 'collectes' },
    { Indicateur: 'Taux Clôture', Valeur: operationnelData?.taux_cloture_moyen || 0, Unité: '%' },
  ]

  const isLoading = financierLoading || occupationLoading || clientsLoading || operationnelLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Export Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Tableau de Bord Général</h2>
        <ExportButton 
          data={exportData}
          filename="dashboard_sigeti"
          title="Tableau de Bord SIGETI - Synthèse Générale"
        />
      </div>

      {/* Alerts Panel */}
      <AlertsPanel showOnlyActive={true} maxAlerts={3} />

      {/* Financial KPIs */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <DollarSign className="w-6 h-6 mr-2 text-blue-600" />
          Performance Financière
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="CA Facturé"
            value={formatCurrency(financierData?.ca_total)}
            subtitle="Chiffre d'affaires total"
            icon={DollarSign}
            color="blue"
          />
          <StatsCard
            title="CA Payé"
            value={formatCurrency(financierData?.ca_paye)}
            subtitle="Encaissements"
            icon={TrendingUp}
            color="green"
          />
          <StatsCard
            title="Créances"
            value={formatCurrency(financierData?.ca_impaye)}
            subtitle="Montant impayé"
            icon={TrendingDown}
            color="orange"
          />
          <StatsCard
            title="Taux de Paiement"
            value={formatPercent(financierData?.taux_paiement_moyen)}
            subtitle="Performance recouvrement"
            icon={Activity}
            color="purple"
          />
        </div>
      </section>

      {/* Occupation KPIs */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Building2 className="w-6 h-6 mr-2 text-blue-600" />
          Occupation des Zones
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Lots"
            value={occupationData?.total_lots?.toLocaleString('fr-FR') || '0'}
            subtitle="Capacité totale"
            icon={Building2}
            color="indigo"
          />
          <StatsCard
            title="Lots Disponibles"
            value={occupationData?.lots_disponibles?.toLocaleString('fr-FR') || '0'}
            subtitle="Offre disponible"
            icon={Building2}
            color="green"
          />
          <StatsCard
            title="Lots Attribués"
            value={occupationData?.lots_attribues?.toLocaleString('fr-FR') || '0'}
            subtitle="Lots occupés"
            icon={Building2}
            color="blue"
          />
          <StatsCard
            title="Taux d'Occupation"
            value={formatPercent(occupationData?.taux_occupation_moyen)}
            subtitle="Performance occupation"
            icon={Activity}
            color="purple"
          />
        </div>
      </section>

      {/* Operational KPIs */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Activity className="w-6 h-6 mr-2 text-blue-600" />
          Performance Opérationnelle
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Collectes"
            value={operationnelData?.total_collectes?.toLocaleString('fr-FR') || '0'}
            subtitle="Campagnes de recouvrement"
            icon={Activity}
            color="indigo"
          />
          <StatsCard
            title="Demandes"
            value={operationnelData?.total_demandes?.toLocaleString('fr-FR') || '0'}
            subtitle="Attributions"
            icon={Building2}
            color="blue"
          />
          <StatsCard
            title="Taux Approbation"
            value={formatPercent(operationnelData?.taux_approbation_moyen)}
            subtitle="Qualité des dossiers"
            icon={TrendingUp}
            color="green"
          />
          <StatsCard
            title="Taux Recouvrement"
            value={formatPercent(operationnelData?.taux_recouvrement_moyen)}
            subtitle="Efficacité collecte"
            icon={Activity}
            color="purple"
          />
        </div>
      </section>
    </div>
  )
}
