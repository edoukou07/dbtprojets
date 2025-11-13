import { useState } from 'react'
import { Calendar, MapPin, Briefcase, X, TrendingUp } from 'lucide-react'

export default function FilterBar({ onFilterChange, showZoneFilter = true, showDomaineFilter = true, showComparison = false }) {
  const [filters, setFilters] = useState({
    dateDebut: '',
    dateFin: '',
    zone: '',
    domaine: '',
    periode: 'mois',
    compareWithPrevious: false
  })

  // Options de périodes prédéfinies
  const periodePresets = [
    { value: 'today', label: "Aujourd'hui" },
    { value: '7days', label: '7 derniers jours' },
    { value: '30days', label: '30 derniers jours' },
    { value: 'mois', label: 'Ce mois' },
    { value: 'trimestre', label: 'Ce trimestre' },
    { value: 'annee', label: 'Cette année' },
    { value: 'custom', label: 'Période personnalisée' }
  ]

  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value }
    setFilters(newFilters)
    
    // Auto-calculer les dates selon le preset
    if (field === 'periode' && value !== 'custom') {
      const dates = calculateDates(value)
      newFilters.dateDebut = dates.debut
      newFilters.dateFin = dates.fin
      setFilters(newFilters)
    }
    
    onFilterChange && onFilterChange(newFilters)
  }

  const calculateDates = (preset) => {
    const today = new Date()
    let debut, fin = today.toISOString().split('T')[0]

    switch (preset) {
      case 'today':
        debut = fin
        break
      case '7days':
        debut = new Date(today.setDate(today.getDate() - 7)).toISOString().split('T')[0]
        break
      case '30days':
        debut = new Date(today.setDate(today.getDate() - 30)).toISOString().split('T')[0]
        break
      case 'mois':
        debut = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0]
        break
      case 'trimestre':
        const currentQuarter = Math.floor(today.getMonth() / 3)
        debut = new Date(today.getFullYear(), currentQuarter * 3, 1).toISOString().split('T')[0]
        break
      case 'annee':
        debut = new Date(today.getFullYear(), 0, 1).toISOString().split('T')[0]
        break
      default:
        debut = ''
    }

    return { debut, fin }
  }

  const resetFilters = () => {
    const defaultFilters = {
      dateDebut: '',
      dateFin: '',
      zone: '',
      domaine: '',
      periode: 'mois',
      compareWithPrevious: false
    }
    setFilters(defaultFilters)
    onFilterChange && onFilterChange(defaultFilters)
  }

  const hasActiveFilters = filters.dateDebut || filters.dateFin || filters.zone || filters.domaine

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700 flex items-center">
          <Calendar className="w-4 h-4 mr-2 text-blue-600" />
          Filtres & Période
        </h3>
        {hasActiveFilters && (
          <button
            onClick={resetFilters}
            className="flex items-center text-sm text-red-600 hover:text-red-700 font-medium"
          >
            <X className="w-4 h-4 mr-1" />
            Réinitialiser
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Sélecteur de période prédéfinie */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Période
          </label>
          <select
            value={filters.periode}
            onChange={(e) => handleFilterChange('periode', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {periodePresets.map(preset => (
              <option key={preset.value} value={preset.value}>{preset.label}</option>
            ))}
          </select>
        </div>

        {/* Date de début (visible si custom) */}
        {filters.periode === 'custom' && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Date de début
            </label>
            <input
              type="date"
              value={filters.dateDebut}
              onChange={(e) => handleFilterChange('dateDebut', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        )}

        {/* Date de fin (visible si custom) */}
        {filters.periode === 'custom' && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Date de fin
            </label>
            <input
              type="date"
              value={filters.dateFin}
              onChange={(e) => handleFilterChange('dateFin', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        )}

        {/* Filtre Zone */}
        {showZoneFilter && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1 flex items-center">
              <MapPin className="w-3 h-3 mr-1" />
              Zone Industrielle
            </label>
            <select
              value={filters.zone}
              onChange={(e) => handleFilterChange('zone', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Toutes les zones</option>
              <option value="1">Zone Industrielle de Yopougon</option>
              <option value="2">Zone Industrielle de Koumassi</option>
              <option value="3">Zone Industrielle de Treichville</option>
              <option value="4">Zone Industrielle de Vridi</option>
            </select>
          </div>
        )}

        {/* Filtre Domaine */}
        {showDomaineFilter && (
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1 flex items-center">
              <Briefcase className="w-3 h-3 mr-1" />
              Domaine d'Activité
            </label>
            <select
              value={filters.domaine}
              onChange={(e) => handleFilterChange('domaine', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous les domaines</option>
              <option value="1">Industrie Manufacturière</option>
              <option value="2">Agroalimentaire</option>
              <option value="3">Textile</option>
              <option value="4">Chimie & Pétrochimie</option>
              <option value="5">Logistique & Transport</option>
              <option value="6">Services</option>
            </select>
          </div>
        )}
      </div>

      {/* Option de comparaison */}
      {showComparison && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={filters.compareWithPrevious}
              onChange={(e) => handleFilterChange('compareWithPrevious', e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1 text-green-600" />
              Comparer avec la période précédente
            </span>
          </label>
        </div>
      )}

      {/* Affichage des filtres actifs */}
      {hasActiveFilters && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            <span className="text-xs font-medium text-gray-600">Filtres actifs:</span>
            {filters.dateDebut && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {filters.dateDebut} → {filters.dateFin || 'aujourd\'hui'}
              </span>
            )}
            {filters.zone && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Zone sélectionnée
              </span>
            )}
            {filters.domaine && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Domaine sélectionné
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
