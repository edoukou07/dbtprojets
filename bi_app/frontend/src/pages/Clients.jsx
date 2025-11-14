import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { clientsAPI } from '../services/api'
import { ExternalLink, TrendingUp, Users, AlertCircle, Search, X, ChevronLeft, ChevronRight, Download } from 'lucide-react'
import { CardSkeleton, TableSkeleton } from '../components/skeletons'
import { exportClientsToExcel } from '../utils/excelExport'

export default function Clients() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSegment, setSelectedSegment] = useState('')
  const [selectedRisque, setSelectedRisque] = useState('')
  const [minTauxPaiement, setMinTauxPaiement] = useState('')
  const [maxFacturesRetard, setMaxFacturesRetard] = useState('')
  const [minDemandes, setMinDemandes] = useState('')
  const [minLotsAttribues, setMinLotsAttribues] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)
  
  const { data: clientsResponse, isLoading } = useQuery({
    queryKey: ['clients-list'],
    queryFn: () => clientsAPI.getAll().then(res => res.data),
    staleTime: 30000,
  })

  // Extraire le tableau de clients de la réponse paginée
  const allClients = clientsResponse?.results || []
  
  // Extraire les valeurs uniques pour les filtres
  const segments = useMemo(() => {
    const unique = [...new Set(allClients.map(c => c.segment_client).filter(Boolean))]
    return unique.sort()
  }, [allClients])
  
  const niveauxRisque = useMemo(() => {
    const unique = [...new Set(allClients.map(c => c.niveau_risque).filter(Boolean))]
    return unique.sort()
  }, [allClients])
  
  // Filtrer les clients selon tous les critères
  const filteredClients = allClients.filter(client => {
    // Filtre par recherche textuelle
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      const matchSearch = 
        client.raison_sociale?.toLowerCase().includes(term) ||
        client.entreprise_id?.toString().includes(term)
      if (!matchSearch) return false
    }
    
    // Filtre par segment
    if (selectedSegment && client.segment_client !== selectedSegment) {
      return false
    }
    
    // Filtre par niveau de risque
    if (selectedRisque && client.niveau_risque !== selectedRisque) {
      return false
    }
    
    // Filtre par taux de paiement minimum
    if (minTauxPaiement) {
      const taux = parseFloat(client.taux_paiement_pct) || 0
      if (taux < parseFloat(minTauxPaiement)) return false
    }
    
    // Filtre par nombre max de factures en retard
    if (maxFacturesRetard) {
      const nbRetard = parseInt(client.nombre_factures_retard) || 0
      if (nbRetard > parseInt(maxFacturesRetard)) return false
    }
    
    // Filtre par nombre minimum de demandes
    if (minDemandes) {
      const nbDemandes = parseInt(client.nombre_demandes) || 0
      if (nbDemandes < parseInt(minDemandes)) return false
    }
    
    // Filtre par nombre minimum de lots attribués
    if (minLotsAttribues) {
      const nbLots = parseInt(client.nombre_lots_attribues) || 0
      if (nbLots < parseInt(minLotsAttribues)) return false
    }
    
    return true
  })
  
  // Calculs de pagination
  const totalPages = Math.ceil(filteredClients.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const clients = filteredClients.slice(startIndex, endIndex)
  
  // Réinitialiser à la page 1 quand les filtres changent
  useMemo(() => {
    setCurrentPage(1)
  }, [searchTerm, selectedSegment, selectedRisque, minTauxPaiement, maxFacturesRetard, minDemandes, minLotsAttribues])
  
  const resetFilters = () => {
    setSearchTerm('')
    setSelectedSegment('')
    setSelectedRisque('')
    setMinTauxPaiement('')
    setMaxFacturesRetard('')
    setMinDemandes('')
    setMinLotsAttribues('')
    setCurrentPage(1)
  }
  
  const hasActiveFilters = searchTerm || selectedSegment || selectedRisque || 
    minTauxPaiement || maxFacturesRetard || minDemandes || minLotsAttribues

  const { data: summary } = useQuery({
    queryKey: ['clients-summary'],
    queryFn: () => clientsAPI.getSummary().then(res => res.data),
    staleTime: 30000,
  })

  const formatCurrency = (value) => {
    if (!value && value !== 0) return '0 FCFA'
    return new Intl.NumberFormat('fr-FR').format(value) + ' FCFA'
  }

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0%'
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0%'
    return numValue.toFixed(1) + '%'
  }

  const getRisqueColor = (niveau) => {
    switch (niveau?.toLowerCase()) {
      case 'faible': return 'bg-green-100 text-green-800'
      case 'moyen': return 'bg-yellow-100 text-yellow-800'
      case 'eleve': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* En-tête avec bouton Export */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Portefeuille Clients</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Gestion et analyse du portefeuille clients</p>
        </div>
        <button
          onClick={() => exportClientsToExcel(summary, allClients)}
          disabled={!summary || !allClients || allClients.length === 0}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg flex items-center gap-2 transition-colors shadow-sm disabled:cursor-not-allowed"
          title="Exporter vers Excel"
        >
          <Download className="w-5 h-5" />
          Exporter Excel
        </button>
      </div>

      {/* KPIs Summary */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Clients</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{summary.total_clients || 0}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">CA Total</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{formatCurrency(summary.ca_total)}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Taux Paiement Moyen</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{formatPercent(summary.taux_paiement_moyen)}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">CA Impayé</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{formatCurrency(summary.ca_impaye)}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
          </div>
        </div>
      )}

      {/* Table des clients */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Liste des Clients</h3>
        
        {/* Filtres */}
        <div className="mb-4 space-y-3">
          {/* Barre de recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher par raison sociale ou ID entreprise..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          {/* Filtres principaux */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Filtre Segment */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Segment Client
              </label>
              <select
                value={selectedSegment}
                onChange={(e) => setSelectedSegment(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Tous les segments</option>
                {segments.map(segment => (
                  <option key={segment} value={segment}>{segment}</option>
                ))}
              </select>
            </div>
            
            {/* Filtre Niveau de Risque */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Niveau de Risque
              </label>
              <select
                value={selectedRisque}
                onChange={(e) => setSelectedRisque(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Tous les niveaux</option>
                {niveauxRisque.map(niveau => (
                  <option key={niveau} value={niveau}>{niveau}</option>
                ))}
              </select>
            </div>
            
            {/* Filtre Taux Paiement Min */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Taux Paiement Min (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="5"
                placeholder="Ex: 80"
                value={minTauxPaiement}
                onChange={(e) => setMinTauxPaiement(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Filtre Factures Retard Max */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Factures Retard Max
              </label>
              <input
                type="number"
                min="0"
                step="1"
                placeholder="Ex: 5"
                value={maxFacturesRetard}
                onChange={(e) => setMaxFacturesRetard(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Filtres avancés */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {/* Filtre Demandes Min */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nombre Demandes Min
              </label>
              <input
                type="number"
                min="0"
                step="1"
                placeholder="Ex: 1"
                value={minDemandes}
                onChange={(e) => setMinDemandes(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Filtre Lots Attribués Min */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Lots Attribués Min
              </label>
              <input
                type="number"
                min="0"
                step="1"
                placeholder="Ex: 1"
                value={minLotsAttribues}
                onChange={(e) => setMinLotsAttribues(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Bouton Réinitialiser */}
            <div className="flex items-end">
              {hasActiveFilters && (
                <button
                  onClick={resetFilters}
                  className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center justify-center gap-2"
                >
                  <X className="w-4 h-4" />
                  Réinitialiser les filtres
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Nombre de résultats */}
        {!isLoading && (
          <div className="flex items-center justify-between py-4 border-y border-gray-200 bg-gray-50">
            <div className="flex items-center gap-2 px-4">
              <label className="text-sm text-gray-600">Afficher:</label>
              <select
                value={itemsPerPage}
                onChange={(e) => {
                  setItemsPerPage(Number(e.target.value))
                  setCurrentPage(1)
                }}
                className="px-2 py-1 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span className="text-sm text-gray-600 dark:text-gray-400">par page</span>
            </div>
            
            <p className="text-lg font-semibold text-gray-900 dark:text-white">
              {filteredClients.length} {filteredClients.length > 1 ? 'entreprises trouvées' : 'entreprise trouvée'}
              {hasActiveFilters && (
                <span className="text-sm font-normal text-gray-600 dark:text-gray-400 ml-2">
                  (sur {allClients.length} au total)
                </span>
              )}
            </p>
            
            <div className="text-sm text-gray-600 dark:text-gray-400 px-4">
              {filteredClients.length > 0 && (
                <>Affichage {startIndex + 1}-{Math.min(endIndex, filteredClients.length)} sur {filteredClients.length}</>
              )}
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <TableSkeleton rows={itemsPerPage} columns={7} />
          </div>
        ) : clients && clients.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Secteur
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    CA Total
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Taux Paiement
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Niveau Risque
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Segment
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-white uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {clients.map((client) => (
                  <tr key={client.entreprise_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{client.raison_sociale}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">ID: {client.entreprise_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {client.secteur_activite || 'Non défini'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {formatCurrency(client.chiffre_affaires_total)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${
                        (client.taux_paiement_pct || 0) >= 80 ? 'text-green-600 dark:text-green-400' : 
                        (client.taux_paiement_pct || 0) >= 50 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'
                      }`}>
                        {formatPercent(client.taux_paiement_pct)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        client.niveau_risque?.toLowerCase() === 'faible' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' :
                        client.niveau_risque?.toLowerCase() === 'moyen' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' :
                        client.niveau_risque?.toLowerCase() === 'eleve' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' :
                        'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                      }`}>
                        {client.niveau_risque || 'Non défini'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {client.segment_client || 'Non segmenté'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <Link
                        to={`/clients/${client.entreprise_id}`}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 inline-flex items-center gap-1"
                      >
                        Détails
                        <ExternalLink className="w-4 h-4" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              {hasActiveFilters 
                ? 'Aucun client ne correspond aux filtres sélectionnés' 
                : 'Aucun client trouvé'}
            </p>
            {hasActiveFilters && (
              <button
                onClick={resetFilters}
                className="mt-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm inline-flex items-center gap-1"
              >
                <X className="w-4 h-4" />
                Réinitialiser les filtres
              </button>
            )}
          </div>
        )}
        
        {/* Pagination */}
        {!isLoading && filteredClients.length > 0 && totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6">
            <div className="flex justify-between items-center w-full">
              <div className="text-sm text-gray-700 dark:text-gray-300">
                Page <span className="font-medium">{currentPage}</span> sur{' '}
                <span className="font-medium">{totalPages}</span>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className={`px-3 py-1 rounded-lg flex items-center gap-1 ${
                    currentPage === 1
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Précédent
                </button>
                
                {/* Numéros de page */}
                <div className="flex gap-1">
                  {[...Array(totalPages)].map((_, idx) => {
                    const pageNum = idx + 1
                    // Afficher les 3 premières, les 3 dernières, et celles autour de la page actuelle
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
                              ? 'bg-blue-600 dark:bg-blue-700 text-white'
                              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    } else if (pageNum === currentPage - 2 || pageNum === currentPage + 2) {
                      return <span key={pageNum} className="px-2 py-1 text-gray-500 dark:text-gray-400">...</span>
                    }
                    return null
                  })}
                </div>
                
                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className={`px-3 py-1 rounded-lg flex items-center gap-1 ${
                    currentPage === totalPages
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
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
    </div>
  )
}

