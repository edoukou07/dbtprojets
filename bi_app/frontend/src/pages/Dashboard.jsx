import { useQuery } from '@tanstack/react-query'
import { DollarSign, Building2, Users, Activity, TrendingUp, TrendingDown } from 'lucide-react'
import { financierAPI, occupationAPI, clientsAPI, operationnelAPI } from '../services/api'
import StatsCard from '../components/StatsCard'

export default function Dashboard() {
  const { data: financierData } = useQuery({
    queryKey: ['financier-summary'],
    queryFn: () => financierAPI.getSummary().then(res => res.data),
  })

  const { data: occupationData } = useQuery({
    queryKey: ['occupation-summary'],
    queryFn: () => occupationAPI.getSummary().then(res => res.data),
  })

  const { data: clientsData } = useQuery({
    queryKey: ['clients-summary'],
    queryFn: () => clientsAPI.getSummary().then(res => res.data),
  })

  const { data: operationnelData } = useQuery({
    queryKey: ['operationnel-summary'],
    queryFn: () => operationnelAPI.getSummary().then(res => res.data),
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

  return (
    <div className="space-y-8">
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

      {/* Clients KPIs */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Users className="w-6 h-6 mr-2 text-blue-600" />
          Portefeuille Clients
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Clients"
            value={clientsData?.total_clients?.toLocaleString('fr-FR') || '0'}
            subtitle="Entreprises actives"
            icon={Users}
            color="blue"
          />
          <StatsCard
            title="CA Total"
            value={formatCurrency(clientsData?.ca_total)}
            subtitle="Revenus clients"
            icon={DollarSign}
            color="green"
          />
          <StatsCard
            title="CA Impayé"
            value={formatCurrency(clientsData?.ca_impaye)}
            subtitle="Créances clients"
            icon={TrendingDown}
            color="orange"
          />
          <StatsCard
            title="Taux de Paiement"
            value={formatPercent(clientsData?.taux_paiement_moyen)}
            subtitle="Fiabilité clients"
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
