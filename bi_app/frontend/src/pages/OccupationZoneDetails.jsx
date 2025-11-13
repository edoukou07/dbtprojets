import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { Building2, MapPin, TrendingUp, DollarSign, ArrowLeft, Percent, Download } from 'lucide-react'
import { occupationAPI } from '../services/api'
import StatsCard from '../components/StatsCard'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { useState } from 'react'

export default function OccupationZoneDetails() {
  const { zoneName } = useParams()
  const [isExporting, setIsExporting] = useState(false)
  
  const { data: zoneData, isLoading, error } = useQuery({
    queryKey: ['zone-details', zoneName],
    queryFn: () => occupationAPI.getZoneDetails(zoneName).then(res => res.data),
    enabled: !!zoneName,
  })

  const formatNumber = (value) => {
    if (!value && value !== 0) return '0'
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0'
    return new Intl.NumberFormat('fr-FR').format(numValue)
  }

  const formatCurrency = (value) => {
    if (!value && value !== 0) return '0 FCFA'
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0 FCFA'
    return new Intl.NumberFormat('fr-FR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numValue) + ' FCFA'
  }

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0%'
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0%'
    return numValue.toFixed(1) + '%'
  }

  const formatSuperficie = (value) => {
    if (!value && value !== 0) return '0 m²'
    const numValue = typeof value === 'string' ? parseFloat(value) : value
    if (isNaN(numValue)) return '0 m²'
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(numValue) + ' m²'
  }

  // Fonction pour nettoyer les caractères spéciaux pour le PDF
  const cleanForPDF = (text) => {
    if (!text) return text
    return String(text)
      .replace(/é/g, 'e')
      .replace(/è/g, 'e')
      .replace(/ê/g, 'e')
      .replace(/à/g, 'a')
      .replace(/â/g, 'a')
      .replace(/ù/g, 'u')
      .replace(/û/g, 'u')
      .replace(/ô/g, 'o')
      .replace(/î/g, 'i')
      .replace(/ï/g, 'i')
      .replace(/ç/g, 'c')
      .replace(/'/g, ' ')
      .replace(/'/g, ' ')
      .replace(/"/g, ' ')
      .replace(/"/g, ' ')
      .replace(/–/g, '-')
      .replace(/—/g, '-')
      .replace(/\u00A0/g, ' ')  // Espace insécable
      .replace(/\u202F/g, ' ')  // Espace fine insécable
      .replace(/\s+/g, ' ')     // Normaliser tous les espaces
  }

  const exportToPDF = () => {
    if (!zoneData) return
    
    setIsExporting(true)
    
    setTimeout(() => {
      try {
        const doc = new jsPDF({
          orientation: 'portrait',
          unit: 'mm',
          format: 'a4',
          putOnlyUsedFonts: true,
          compress: true
        })
        
        const pageWidth = doc.internal.pageSize.getWidth()
        const pageHeight = doc.internal.pageSize.getHeight()
        let yPosition = 20

        // En-tête
        doc.setFillColor(37, 99, 235) // blue-600
        doc.rect(0, 0, pageWidth, 35, 'F')
        doc.setTextColor(255, 255, 255)
        doc.setFontSize(22)
        doc.setFont('helvetica', 'bold')
        doc.text(cleanForPDF('SIGETI - Details Zone Industrielle'), pageWidth / 2, 15, { align: 'center' })
        doc.setFontSize(14)
        doc.text(cleanForPDF(zoneData.nom_zone || 'N/A'), pageWidth / 2, 25, { align: 'center' })

        // Réinitialiser la couleur du texte
        doc.setTextColor(0, 0, 0)
        yPosition = 45

        // Section 1: KPIs Principaux
        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Vue d ensemble'), 14, yPosition)
        yPosition += 10

        const kpis = [
          [cleanForPDF('Indicateur'), cleanForPDF('Valeur')],
          [cleanForPDF('Taux d Occupation'), cleanForPDF(formatPercent(zoneData.taux_occupation_pct))],
          [cleanForPDF('Total Lots'), cleanForPDF(formatNumber(zoneData.nombre_total_lots))],
          [cleanForPDF('Superficie Totale'), cleanForPDF(formatSuperficie(zoneData.superficie_totale))],
          [cleanForPDF('Valeur Totale'), cleanForPDF(formatCurrency(zoneData.valeur_totale_lots))],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [kpis[0]],
          body: kpis.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        yPosition = doc.lastAutoTable.finalY + 15

        // Section 2: Distribution des Lots
        if (yPosition > pageHeight - 60) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Distribution des Lots'), 14, yPosition)
        yPosition += 10

        const distributionLots = [
          [cleanForPDF('Type de Lot'), cleanForPDF('Nombre'), cleanForPDF('Pourcentage')],
          [cleanForPDF('Lots Disponibles'), cleanForPDF(formatNumber(zoneData.lots_disponibles)), cleanForPDF(formatPercent(zoneData.pct_disponible))],
          [cleanForPDF('Lots Attribues'), cleanForPDF(formatNumber(zoneData.lots_attribues)), cleanForPDF(formatPercent(zoneData.pct_attribues))],
          [cleanForPDF('Lots Reserves'), cleanForPDF(formatNumber(zoneData.lots_reserves)), cleanForPDF(formatPercent(zoneData.pct_reserves))],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [distributionLots[0]],
          body: distributionLots.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        yPosition = doc.lastAutoTable.finalY + 15

        // Section 3: Distribution des Superficies
        if (yPosition > pageHeight - 60) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Distribution des Superficies'), 14, yPosition)
        yPosition += 10

        const distributionSuperficie = [
          [cleanForPDF('Type'), cleanForPDF('Surface'), cleanForPDF('Pourcentage')],
          [cleanForPDF('Superficie Disponible'), cleanForPDF(formatSuperficie(zoneData.superficie_disponible)), cleanForPDF(formatPercent(zoneData.pct_superficie_disponible))],
          [cleanForPDF('Superficie Attribuee'), cleanForPDF(formatSuperficie(zoneData.superficie_attribuee)), cleanForPDF(formatPercent(zoneData.pct_superficie_attribuee))],
          [cleanForPDF('Superficie Totale'), cleanForPDF(formatSuperficie(zoneData.superficie_totale)), '100%'],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [distributionSuperficie[0]],
          body: distributionSuperficie.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        yPosition = doc.lastAutoTable.finalY + 15

        // Section 4: Indicateurs Avancés
        if (yPosition > pageHeight - 60) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Indicateurs Avances'), 14, yPosition)
        yPosition += 10

        const indicateursAvances = [
          [cleanForPDF('Indicateur'), cleanForPDF('Valeur')],
          [cleanForPDF('Valeur Moyenne par Lot'), cleanForPDF(formatCurrency(zoneData.valeur_moyenne_lot))],
          [cleanForPDF('Taux de Viabilisation'), cleanForPDF(formatPercent(zoneData.taux_viabilisation_pct))],
          [cleanForPDF('Potentiel de Valorisation'), cleanForPDF(formatCurrency((zoneData.lots_disponibles || 0) * (zoneData.valeur_moyenne_lot || 0)))],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [indicateursAvances[0]],
          body: indicateursAvances.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        yPosition = doc.lastAutoTable.finalY + 15

        // Section 5: Récapitulatif Complet
        if (yPosition > pageHeight - 120) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Recapitulatif Complet'), 14, yPosition)
        yPosition += 10

        const recapitulatif = [
          [cleanForPDF('Indicateur'), cleanForPDF('Valeur')],
          [cleanForPDF('Zone ID'), cleanForPDF(zoneData.zone_id || 'N/A')],
          [cleanForPDF('Nom de la Zone'), cleanForPDF(zoneData.nom_zone || 'N/A')],
          [cleanForPDF('Nombre Total de Lots'), cleanForPDF(formatNumber(zoneData.nombre_total_lots))],
          [cleanForPDF('Lots Disponibles'), cleanForPDF(formatNumber(zoneData.lots_disponibles))],
          [cleanForPDF('Lots Attribues'), cleanForPDF(formatNumber(zoneData.lots_attribues))],
          [cleanForPDF('Lots Reserves'), cleanForPDF(formatNumber(zoneData.lots_reserves))],
          [cleanForPDF('Superficie Totale'), cleanForPDF(formatSuperficie(zoneData.superficie_totale))],
          [cleanForPDF('Superficie Disponible'), cleanForPDF(formatSuperficie(zoneData.superficie_disponible))],
          [cleanForPDF('Superficie Attribuee'), cleanForPDF(formatSuperficie(zoneData.superficie_attribuee))],
          [cleanForPDF('Taux d Occupation'), cleanForPDF(formatPercent(zoneData.taux_occupation_pct))],
          [cleanForPDF('Taux de Viabilisation'), cleanForPDF(formatPercent(zoneData.taux_viabilisation_pct))],
          [cleanForPDF('Valeur Totale des Lots'), cleanForPDF(formatCurrency(zoneData.valeur_totale_lots))],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [recapitulatif[0]],
          body: recapitulatif.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        // Pied de page sur toutes les pages
        const totalPages = doc.internal.getNumberOfPages()
        for (let i = 1; i <= totalPages; i++) {
          doc.setPage(i)
          doc.setFontSize(8)
          doc.setTextColor(128, 128, 128)
          doc.text(
            `SIGETI - ${new Date().toLocaleDateString('fr-FR')} - Page ${i}/${totalPages}`,
            pageWidth / 2,
            pageHeight - 10,
            { align: 'center' }
          )
        }

        // Sauvegarder le PDF
        const fileName = `Zone_${(zoneData.nom_zone || 'Unknown').replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`
        doc.save(fileName)

        setIsExporting(false)
      } catch (error) {
        console.error('Erreur lors de l\'export PDF:', error)
        alert(`Une erreur est survenue lors de l\'export PDF: ${error.message}`)
        setIsExporting(false)
      }
    }, 100)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des données de la zone...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">❌ Erreur</div>
          <p className="text-gray-600">{error.message || 'Impossible de charger les données'}</p>
          <Link to="/occupation" className="mt-4 inline-block text-blue-600 hover:underline">
            ← Retour à Occupation
          </Link>
        </div>
      </div>
    )
  }

  if (!zoneData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600">Aucune donnée disponible pour cette zone</p>
          <Link to="/occupation" className="mt-4 inline-block text-blue-600 hover:underline">
            ← Retour à Occupation
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb et Titre */}
      <div className="flex items-center justify-between">
        <div>
          <Link 
            to="/occupation" 
            className="text-blue-600 hover:text-blue-800 flex items-center mb-2"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Retour à Occupation des Zones
          </Link>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <MapPin className="w-8 h-8 mr-3 text-blue-600" />
            {zoneData.nom_zone}
          </h2>
          <p className="text-gray-600 mt-1">Détails complets de la zone industrielle</p>
        </div>
        
        {/* Bouton Export PDF */}
        <button
          onClick={exportToPDF}
          disabled={isExporting}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            isExporting
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          <Download className="w-5 h-5" />
          {isExporting ? 'Export en cours...' : 'Exporter en PDF'}
        </button>
      </div>

      {/* KPIs Principaux */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Vue d'ensemble</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Taux d'Occupation"
            value={formatPercent(zoneData.taux_occupation_pct)}
            subtitle="Occupation globale"
            icon={Percent}
            color={zoneData.taux_occupation_pct > 80 ? "green" : zoneData.taux_occupation_pct > 50 ? "orange" : "red"}
          />
          <StatsCard
            title="Total Lots"
            value={formatNumber(zoneData.nombre_total_lots)}
            subtitle="Capacité totale"
            icon={Building2}
            color="indigo"
          />
          <StatsCard
            title="Superficie Totale"
            value={formatSuperficie(zoneData.superficie_totale)}
            subtitle="Surface totale"
            icon={MapPin}
            color="blue"
          />
          <StatsCard
            title="Valeur Totale"
            value={formatCurrency(zoneData.valeur_totale_lots)}
            subtitle="Valeur des lots"
            icon={DollarSign}
            color="green"
          />
        </div>
      </section>

      {/* Distribution des Lots */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Building2 className="w-6 h-6 mr-2 text-blue-600" />
          Distribution des Lots
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-600">Lots Disponibles</h4>
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <Building2 className="w-5 h-5 text-green-600" />
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{formatNumber(zoneData.lots_disponibles)}</p>
            <p className="text-sm text-gray-500 mt-1">{formatPercent(zoneData.pct_disponible)} du total</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-600">Lots Attribués</h4>
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                <Building2 className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{formatNumber(zoneData.lots_attribues)}</p>
            <p className="text-sm text-gray-500 mt-1">{formatPercent(zoneData.pct_attribues)} du total</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-600">Lots Réservés</h4>
              <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                <Building2 className="w-5 h-5 text-orange-600" />
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{formatNumber(zoneData.lots_reserves)}</p>
            <p className="text-sm text-gray-500 mt-1">{formatPercent(zoneData.pct_reserves)} du total</p>
          </div>
        </div>
      </section>

      {/* Distribution des Superficies */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <MapPin className="w-6 h-6 mr-2 text-blue-600" />
          Distribution des Superficies
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-sm font-medium text-gray-600 mb-4">Superficie Disponible</h4>
            <p className="text-3xl font-bold text-green-600 mb-2">{formatSuperficie(zoneData.superficie_disponible)}</p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ width: `${zoneData.pct_superficie_disponible}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500 mt-2">{formatPercent(zoneData.pct_superficie_disponible)} de la surface totale</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-sm font-medium text-gray-600 mb-4">Superficie Attribuée</h4>
            <p className="text-3xl font-bold text-blue-600 mb-2">{formatSuperficie(zoneData.superficie_attribuee)}</p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${zoneData.pct_superficie_attribuee}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500 mt-2">{formatPercent(zoneData.pct_superficie_attribuee)} de la surface totale</p>
          </div>
        </div>
      </section>

      {/* Indicateurs Avancés */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="w-6 h-6 mr-2 text-blue-600" />
          Indicateurs Avancés
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Valeur Moyenne par Lot</h4>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(zoneData.valeur_moyenne_lot)}</p>
            <p className="text-sm text-gray-500 mt-1">Prix moyen unitaire</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Taux de Viabilisation</h4>
            <p className="text-2xl font-bold text-gray-900">{formatPercent(zoneData.taux_viabilisation_pct)}</p>
            <p className="text-sm text-gray-500 mt-1">Infrastructure disponible</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Potentiel de Valorisation</h4>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency((zoneData.lots_disponibles || 0) * (zoneData.valeur_moyenne_lot || 0))}
            </p>
            <p className="text-sm text-gray-500 mt-1">Valeur lots disponibles</p>
          </div>
        </div>
      </section>

      {/* Tableau Récapitulatif */}
      <section>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Récapitulatif Complet</h3>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Indicateur
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Valeur
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Zone ID</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{zoneData.zone_id}</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Nom de la Zone</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{zoneData.nom_zone}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Nombre Total de Lots</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{formatNumber(zoneData.nombre_total_lots)}</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Lots Disponibles</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 text-right font-semibold">{formatNumber(zoneData.lots_disponibles)}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Lots Attribués</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 text-right font-semibold">{formatNumber(zoneData.lots_attribues)}</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Lots Réservés</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600 text-right font-semibold">{formatNumber(zoneData.lots_reserves)}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Superficie Totale</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{formatSuperficie(zoneData.superficie_totale)}</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Superficie Disponible</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{formatSuperficie(zoneData.superficie_disponible)}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Superficie Attribuée</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{formatSuperficie(zoneData.superficie_attribuee)}</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Taux d'Occupation</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{formatPercent(zoneData.taux_occupation_pct)}</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Taux de Viabilisation</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{formatPercent(zoneData.taux_viabilisation_pct)}</td>
              </tr>
              <tr className="bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Valeur Totale des Lots</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{formatCurrency(zoneData.valeur_totale_lots)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
