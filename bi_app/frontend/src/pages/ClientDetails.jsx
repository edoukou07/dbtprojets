import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { clientsAPI } from '../services/api'
import { ArrowLeft, Download, Building2, Mail, Phone, FileText, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react'
import { useState } from 'react'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { CardSkeleton, TableSkeleton } from '../components/skeletons'

export default function ClientDetails() {
  const { entrepriseId } = useParams()
  const [isExporting, setIsExporting] = useState(false)

  const { data: clientData, isLoading, error } = useQuery({
    queryKey: ['client-details', entrepriseId],
    queryFn: () => clientsAPI.getClientDetails(entrepriseId).then(res => res.data),
    enabled: !!entrepriseId,
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
    if (!clientData) return
    
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
        doc.text(cleanForPDF('SIGETI - Fiche Client Detaillee'), pageWidth / 2, 15, { align: 'center' })
        doc.setFontSize(14)
        doc.text(cleanForPDF(clientData.raison_sociale || 'N/A'), pageWidth / 2, 25, { align: 'center' })

        // Réinitialiser la couleur du texte
        doc.setTextColor(0, 0, 0)
        yPosition = 45

        // Section 1: Informations Générales
        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Informations Generales'), 14, yPosition)
        yPosition += 10

        const infosGenerales = [
          [cleanForPDF('Champ'), cleanForPDF('Valeur')],
          [cleanForPDF('ID Entreprise'), cleanForPDF(clientData.entreprise_id || 'N/A')],
          [cleanForPDF('Raison Sociale'), cleanForPDF(clientData.raison_sociale || 'N/A')],
          [cleanForPDF('Forme Juridique'), cleanForPDF(clientData.forme_juridique || 'N/A')],
          [cleanForPDF('Registre Commerce'), cleanForPDF(clientData.registre_commerce || 'N/A')],
          [cleanForPDF('Secteur d Activite'), cleanForPDF(clientData.secteur_activite || 'N/A')],
          [cleanForPDF('Telephone'), cleanForPDF(clientData.telephone || 'N/A')],
          [cleanForPDF('Email'), cleanForPDF(clientData.email || 'N/A')],
          [cleanForPDF('Segment Client'), cleanForPDF(clientData.segment_client || 'N/A')],
          [cleanForPDF('Niveau de Risque'), cleanForPDF(clientData.niveau_risque || 'N/A')],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [infosGenerales[0]],
          body: infosGenerales.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        yPosition = doc.lastAutoTable.finalY + 15

        // Section 2: Performance Financière
        if (yPosition > pageHeight - 80) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Performance Financiere'), 14, yPosition)
        yPosition += 10

        const performanceFinanciere = [
          [cleanForPDF('Indicateur'), cleanForPDF('Valeur')],
          [cleanForPDF('Chiffre d Affaires Total'), cleanForPDF(formatCurrency(clientData.chiffre_affaires_total))],
          [cleanForPDF('CA Paye'), cleanForPDF(formatCurrency(clientData.ca_paye))],
          [cleanForPDF('CA Impaye'), cleanForPDF(formatCurrency(clientData.ca_impaye))],
          [cleanForPDF('Taux de Recouvrement'), cleanForPDF(formatPercent(clientData.taux_recouvrement))],
          [cleanForPDF('Taux de Paiement'), cleanForPDF(formatPercent(clientData.taux_paiement_pct))],
          [cleanForPDF('Nombre de Factures'), cleanForPDF(formatNumber(clientData.nombre_factures))],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [performanceFinanciere[0]],
          body: performanceFinanciere.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        yPosition = doc.lastAutoTable.finalY + 15

        // Section 3: Comportement de Paiement
        if (yPosition > pageHeight - 60) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Comportement de Paiement'), 14, yPosition)
        yPosition += 10

        const comportementPaiement = [
          [cleanForPDF('Indicateur'), cleanForPDF('Valeur')],
          [cleanForPDF('Delai Moyen de Paiement'), cleanForPDF(formatNumber(clientData.delai_moyen_paiement_jours)) + ' jours'],
          [cleanForPDF('Factures en Retard'), cleanForPDF(formatNumber(clientData.nombre_factures_retard))],
          [cleanForPDF('Taux Factures en Retard'), cleanForPDF(formatPercent(clientData.taux_factures_retard))],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [comportementPaiement[0]],
          body: comportementPaiement.slice(1),
          theme: 'grid',
          headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
          alternateRowStyles: { fillColor: [249, 250, 251] },
          margin: { left: 14, right: 14 },
          styles: { font: 'helvetica', fontSize: 10 },
        })

        yPosition = doc.lastAutoTable.finalY + 15

        // Section 4: Attributions et Occupation
        if (yPosition > pageHeight - 70) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(37, 99, 235)
        doc.text(cleanForPDF('Attributions et Occupation'), 14, yPosition)
        yPosition += 10

        const attributions = [
          [cleanForPDF('Indicateur'), cleanForPDF('Valeur')],
          [cleanForPDF('Nombre de Demandes'), cleanForPDF(formatNumber(clientData.nombre_demandes))],
          [cleanForPDF('Demandes Approuvees'), cleanForPDF(formatNumber(clientData.demandes_approuvees))],
          [cleanForPDF('Taux d Approbation'), cleanForPDF(formatPercent(clientData.taux_approbation))],
          [cleanForPDF('Lots Attribues'), cleanForPDF(formatNumber(clientData.nombre_lots_attribues))],
          [cleanForPDF('Superficie Totale Attribuee'), cleanForPDF(formatSuperficie(clientData.superficie_totale_attribuee))],
          [cleanForPDF('Superficie Moyenne par Lot'), cleanForPDF(formatSuperficie(clientData.superficie_moyenne_lot))],
        ]

        autoTable(doc, {
          startY: yPosition,
          head: [attributions[0]],
          body: attributions.slice(1),
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
        const fileName = `Client_${(clientData.raison_sociale || 'Unknown').replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`
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
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <CardSkeleton />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <TableSkeleton rows={5} columns={4} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Erreur de chargement</h2>
          <p className="text-gray-600 mb-4">{error.message}</p>
          <Link to="/clients" className="text-blue-600 hover:underline">
            Retour aux clients
          </Link>
        </div>
      </div>
    )
  }

  if (!clientData) {
    return null
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
      {/* Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          to="/clients"
          className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Retour aux clients
        </Link>
        <button
          onClick={exportToPDF}
          disabled={isExporting}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {isExporting ? 'Export en cours...' : 'Exporter en PDF'}
        </button>
      </div>

      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Building2 className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{clientData.raison_sociale}</h1>
              <p className="text-gray-500 mt-1">ID: {clientData.entreprise_id}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRisqueColor(clientData.niveau_risque)}`}>
              {clientData.niveau_risque || 'Non défini'}
            </span>
            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
              {clientData.segment_client || 'Non segmenté'}
            </span>
          </div>
        </div>
      </div>

      {/* KPIs Principaux */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">CA Total</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{formatCurrency(clientData.chiffre_affaires_total)}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Taux de Recouvrement</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{formatPercent(clientData.taux_recouvrement)}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Nombre Factures</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{formatNumber(clientData.nombre_factures)}</p>
            </div>
            <FileText className="w-8 h-8 text-purple-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Lots Attribués</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{formatNumber(clientData.nombre_lots_attribues)}</p>
            </div>
            <Building2 className="w-8 h-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Informations Générales */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Informations Générales</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="text-sm font-medium text-gray-600">Forme Juridique</label>
            <p className="text-gray-900 mt-1">{clientData.forme_juridique || 'Non renseigné'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Registre de Commerce</label>
            <p className="text-gray-900 mt-1">{clientData.registre_commerce || 'Non renseigné'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Secteur d'Activité</label>
            <p className="text-gray-900 mt-1">{clientData.secteur_activite || 'Non renseigné'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Téléphone</label>
            <p className="text-gray-900 mt-1 flex items-center gap-2">
              <Phone className="w-4 h-4 text-gray-400" />
              {clientData.telephone || 'Non renseigné'}
            </p>
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium text-gray-600">Email</label>
            <p className="text-gray-900 mt-1 flex items-center gap-2">
              <Mail className="w-4 h-4 text-gray-400" />
              {clientData.email || 'Non renseigné'}
            </p>
          </div>
        </div>
      </div>

      {/* Performance Financière */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Performance Financière</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-green-700 font-medium">CA Payé</p>
            <p className="text-2xl font-bold text-green-900 mt-1">{formatCurrency(clientData.ca_paye)}</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg">
            <p className="text-sm text-red-700 font-medium">CA Impayé</p>
            <p className="text-2xl font-bold text-red-900 mt-1">{formatCurrency(clientData.ca_impaye)}</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700 font-medium">Taux de Paiement</p>
            <p className="text-2xl font-bold text-blue-900 mt-1">{formatPercent(clientData.taux_paiement_pct)}</p>
          </div>
        </div>
      </div>

      {/* Comportement de Paiement */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Comportement de Paiement</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="text-sm font-medium text-gray-600">Délai Moyen de Paiement</label>
            <p className="text-2xl font-bold text-gray-900 mt-1">{formatNumber(clientData.delai_moyen_paiement_jours)} jours</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Factures en Retard</label>
            <p className="text-2xl font-bold text-orange-600 mt-1">{formatNumber(clientData.nombre_factures_retard)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Taux Factures en Retard</label>
            <p className="text-2xl font-bold text-orange-600 mt-1">{formatPercent(clientData.taux_factures_retard)}</p>
          </div>
        </div>
      </div>

      {/* Attributions et Occupation */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Attributions et Occupation</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="text-sm font-medium text-gray-600">Nombre de Demandes</label>
            <p className="text-2xl font-bold text-gray-900 mt-1">{formatNumber(clientData.nombre_demandes)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Demandes Approuvées</label>
            <p className="text-2xl font-bold text-green-600 mt-1">{formatNumber(clientData.demandes_approuvees)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Taux d'Approbation</label>
            <p className="text-2xl font-bold text-blue-600 mt-1">{formatPercent(clientData.taux_approbation)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Lots Attribués</label>
            <p className="text-2xl font-bold text-gray-900 mt-1">{formatNumber(clientData.nombre_lots_attribues)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Superficie Totale Attribuée</label>
            <p className="text-2xl font-bold text-gray-900 mt-1">{formatSuperficie(clientData.superficie_totale_attribuee)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Superficie Moyenne/Lot</label>
            <p className="text-2xl font-bold text-purple-600 mt-1">{formatSuperficie(clientData.superficie_moyenne_lot)}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
