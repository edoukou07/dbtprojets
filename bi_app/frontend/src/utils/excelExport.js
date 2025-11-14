import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

/**
 * Utilitaire d'export Excel avancé avec support multi-feuilles et formatage
 */

/**
 * Convertit une valeur en format approprié pour Excel
 */
const formatCellValue = (value, type = 'auto') => {
  if (value === null || value === undefined) return ''
  
  switch (type) {
    case 'currency':
      return typeof value === 'number' ? value : parseFloat(value) || 0
    case 'percent':
      return typeof value === 'number' ? value / 100 : parseFloat(value) / 100 || 0
    case 'number':
      return typeof value === 'number' ? value : parseFloat(value) || 0
    case 'date':
      return value instanceof Date ? value : new Date(value)
    default:
      return value
  }
}

/**
 * Applique un style de cellule
 */
const applyCellStyle = (cell, style = {}) => {
  if (!cell) return
  
  cell.s = {
    font: {
      name: 'Calibri',
      sz: 11,
      bold: style.bold || false,
      color: style.fontColor ? { rgb: style.fontColor } : undefined
    },
    fill: style.bgColor ? {
      fgColor: { rgb: style.bgColor }
    } : undefined,
    alignment: {
      horizontal: style.align || 'left',
      vertical: 'center',
      wrapText: style.wrapText || false
    },
    border: style.border ? {
      top: { style: 'thin', color: { rgb: '000000' } },
      bottom: { style: 'thin', color: { rgb: '000000' } },
      left: { style: 'thin', color: { rgb: '000000' } },
      right: { style: 'thin', color: { rgb: '000000' } }
    } : undefined,
    numFmt: style.numFmt || undefined
  }
}

/**
 * Calcule la largeur optimale des colonnes
 */
const calculateColumnWidths = (data, headers) => {
  const colWidths = []
  
  headers.forEach((header, colIndex) => {
    let maxWidth = header.label.length
    
    data.forEach(row => {
      const cellValue = String(row[header.key] || '')
      maxWidth = Math.max(maxWidth, cellValue.length)
    })
    
    // Limiter entre 10 et 50 caractères
    colWidths.push({ wch: Math.min(Math.max(maxWidth + 2, 10), 50) })
  })
  
  return colWidths
}

/**
 * Exporte des données vers Excel avec une seule feuille
 * 
 * @param {Array} data - Tableau d'objets à exporter
 * @param {Array} headers - Configuration des colonnes [{key, label, type, format}]
 * @param {String} fileName - Nom du fichier (sans extension)
 * @param {String} sheetName - Nom de la feuille
 */
export const exportToExcel = (data, headers, fileName = 'export', sheetName = 'Données') => {
  // Créer le workbook
  const wb = XLSX.utils.book_new()
  
  // Préparer les données avec en-têtes
  const wsData = []
  
  // Ligne d'en-tête
  wsData.push(headers.map(h => h.label))
  
  // Lignes de données
  data.forEach(row => {
    const rowData = headers.map(header => {
      const value = row[header.key]
      return formatCellValue(value, header.type)
    })
    wsData.push(rowData)
  })
  
  // Créer la feuille
  const ws = XLSX.utils.aoa_to_sheet(wsData)
  
  // Appliquer les styles aux en-têtes
  headers.forEach((_, colIndex) => {
    const cellAddress = XLSX.utils.encode_cell({ r: 0, c: colIndex })
    const cell = ws[cellAddress]
    applyCellStyle(cell, {
      bold: true,
      bgColor: '4472C4',
      fontColor: 'FFFFFF',
      align: 'center',
      border: true
    })
  })
  
  // Appliquer les formats de nombre
  data.forEach((row, rowIndex) => {
    headers.forEach((header, colIndex) => {
      const cellAddress = XLSX.utils.encode_cell({ r: rowIndex + 1, c: colIndex })
      const cell = ws[cellAddress]
      
      if (cell) {
        let style = { border: true }
        
        switch (header.type) {
          case 'currency':
            style.numFmt = '#,##0 "FCFA"'
            style.align = 'right'
            break
          case 'percent':
            style.numFmt = '0.0%'
            style.align = 'right'
            break
          case 'number':
            style.numFmt = '#,##0'
            style.align = 'right'
            break
          case 'date':
            style.numFmt = 'dd/mm/yyyy'
            style.align = 'center'
            break
        }
        
        applyCellStyle(cell, style)
      }
    })
  })
  
  // Définir les largeurs de colonnes
  ws['!cols'] = calculateColumnWidths(data, headers)
  
  // Ajouter la feuille au workbook
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  
  // Générer le fichier
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array', cellStyles: true })
  const blob = new Blob([wbout], { type: 'application/octet-stream' })
  saveAs(blob, `${fileName}.xlsx`)
}

/**
 * Exporte des données vers Excel avec plusieurs feuilles
 * 
 * @param {Array} sheets - Tableau de configurations [{name, data, headers, summary}]
 * @param {String} fileName - Nom du fichier (sans extension)
 */
export const exportToExcelMultiSheet = (sheets, fileName = 'export') => {
  const wb = XLSX.utils.book_new()
  
  sheets.forEach(({ name, data, headers, summary }) => {
    const wsData = []
    
    // Ajouter un résumé si fourni
    if (summary) {
      wsData.push([summary.title || 'Résumé'])
      wsData.push([]) // Ligne vide
      
      Object.entries(summary.data || {}).forEach(([key, value]) => {
        wsData.push([key, value])
      })
      
      wsData.push([]) // Ligne vide avant les données
      wsData.push([]) // Double ligne vide
    }
    
    // Ligne d'en-tête
    const headerRow = headers.map(h => h.label)
    wsData.push(headerRow)
    
    // Lignes de données
    data.forEach(row => {
      const rowData = headers.map(header => {
        const value = row[header.key]
        return formatCellValue(value, header.type)
      })
      wsData.push(rowData)
    })
    
    // Créer la feuille
    const ws = XLSX.utils.aoa_to_sheet(wsData)
    
    // Définir la ligne d'en-tête (en tenant compte du résumé)
    const headerRowIndex = summary ? wsData.length - data.length - 1 : 0
    
    // Appliquer les styles aux en-têtes
    headers.forEach((_, colIndex) => {
      const cellAddress = XLSX.utils.encode_cell({ r: headerRowIndex, c: colIndex })
      const cell = ws[cellAddress]
      applyCellStyle(cell, {
        bold: true,
        bgColor: '4472C4',
        fontColor: 'FFFFFF',
        align: 'center',
        border: true
      })
    })
    
    // Appliquer les styles au résumé
    if (summary) {
      const titleCell = ws['A1']
      applyCellStyle(titleCell, {
        bold: true,
        bgColor: '70AD47',
        fontColor: 'FFFFFF',
        align: 'center'
      })
      
      // Fusionner les cellules du titre
      ws['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: headers.length - 1 } }]
    }
    
    // Appliquer les formats de nombre aux données
    data.forEach((row, dataRowIndex) => {
      const actualRowIndex = headerRowIndex + 1 + dataRowIndex
      
      headers.forEach((header, colIndex) => {
        const cellAddress = XLSX.utils.encode_cell({ r: actualRowIndex, c: colIndex })
        const cell = ws[cellAddress]
        
        if (cell) {
          let style = { border: true }
          
          switch (header.type) {
            case 'currency':
              style.numFmt = '#,##0 "FCFA"'
              style.align = 'right'
              break
            case 'percent':
              style.numFmt = '0.0%'
              style.align = 'right'
              break
            case 'number':
              style.numFmt = '#,##0'
              style.align = 'right'
              break
            case 'date':
              style.numFmt = 'dd/mm/yyyy'
              style.align = 'center'
              break
          }
          
          applyCellStyle(cell, style)
        }
      })
    })
    
    // Définir les largeurs de colonnes
    ws['!cols'] = calculateColumnWidths(data, headers)
    
    // Ajouter la feuille au workbook
    XLSX.utils.book_append_sheet(wb, ws, name)
  })
  
  // Générer le fichier
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array', cellStyles: true })
  const blob = new Blob([wbout], { type: 'application/octet-stream' })
  saveAs(blob, `${fileName}.xlsx`)
}

/**
 * Exporte les données d'occupation avec résumé et détails
 */
export const exportOccupationToExcel = (summary, zones, topZones) => {
  const sheets = []
  
  // Feuille 1: Résumé
  if (summary) {
    sheets.push({
      name: 'Résumé',
      data: [
        { indicateur: 'Total Zones', valeur: summary.total_zones || 0 },
        { indicateur: 'Lots Totaux', valeur: summary.nombre_total_lots || 0 },
        { indicateur: 'Lots Attribués', valeur: summary.lots_attribues || 0 },
        { indicateur: 'Lots Disponibles', valeur: summary.lots_disponibles || 0 },
        { indicateur: 'Taux d\'Occupation Moyen (%)', valeur: summary.taux_occupation_moyen || 0 },
        { indicateur: 'Superficie Totale (m²)', valeur: summary.superficie_totale || 0 },
        { indicateur: 'Superficie Occupée (m²)', valeur: summary.superficie_occupee || 0 },
        { indicateur: 'Superficie Disponible (m²)', valeur: summary.superficie_disponible || 0 },
        { indicateur: 'Zones Saturées', valeur: summary.zones_saturees || 0 },
        { indicateur: 'Zones Faible Occupation', valeur: summary.zones_faible_occupation || 0 }
      ],
      headers: [
        { key: 'indicateur', label: 'Indicateur', type: 'text' },
        { key: 'valeur', label: 'Valeur', type: 'number' }
      ]
    })
  }
  
  // Feuille 2: Zones les Plus Occupées
  if (topZones?.plus_occupees && topZones.plus_occupees.length > 0) {
    sheets.push({
      name: 'Top Zones Occupées',
      data: topZones.plus_occupees,
      headers: [
        { key: 'nom_zone', label: 'Zone', type: 'text' },
        { key: 'taux_occupation_pct', label: 'Taux Occupation (%)', type: 'percent' },
        { key: 'nombre_total_lots', label: 'Total Lots', type: 'number' },
        { key: 'lots_attribues', label: 'Lots Attribués', type: 'number' },
        { key: 'lots_disponibles', label: 'Lots Disponibles', type: 'number' },
        { key: 'superficie_totale', label: 'Superficie (m²)', type: 'number' }
      ]
    })
  }
  
  // Feuille 3: Zones les Moins Occupées
  if (topZones?.moins_occupees && topZones.moins_occupees.length > 0) {
    sheets.push({
      name: 'Zones Sous-Occupées',
      data: topZones.moins_occupees,
      headers: [
        { key: 'nom_zone', label: 'Zone', type: 'text' },
        { key: 'taux_occupation_pct', label: 'Taux Occupation (%)', type: 'percent' },
        { key: 'nombre_total_lots', label: 'Total Lots', type: 'number' },
        { key: 'lots_attribues', label: 'Lots Attribués', type: 'number' },
        { key: 'lots_disponibles', label: 'Lots Disponibles', type: 'number' },
        { key: 'superficie_totale', label: 'Superficie (m²)', type: 'number' }
      ]
    })
  }
  
  // Feuille 4: Toutes les Zones
  if (zones && zones.length > 0) {
    sheets.push({
      name: 'Détails Zones',
      data: zones,
      headers: [
        { key: 'nom_zone', label: 'Zone', type: 'text' },
        { key: 'taux_occupation_pct', label: 'Taux Occupation (%)', type: 'percent' },
        { key: 'nombre_total_lots', label: 'Total Lots', type: 'number' },
        { key: 'lots_attribues', label: 'Lots Attribués', type: 'number' },
        { key: 'lots_disponibles', label: 'Lots Disponibles', type: 'number' },
        { key: 'superficie_totale', label: 'Superficie Totale (m²)', type: 'number' },
        { key: 'superficie_occupee', label: 'Superficie Occupée (m²)', type: 'number' },
        { key: 'superficie_disponible', label: 'Superficie Disponible (m²)', type: 'number' }
      ]
    })
  }
  
  exportToExcelMultiSheet(sheets, `Rapport_Occupation_${new Date().toISOString().split('T')[0]}`)
}

/**
 * Exporte les données clients avec résumé
 */
export const exportClientsToExcel = (summary, clients) => {
  const sheets = []
  
  // Feuille 1: Résumé
  if (summary) {
    sheets.push({
      name: 'Résumé',
      data: [
        { indicateur: 'Total Clients', valeur: summary.total_clients || 0 },
        { indicateur: 'CA Total (FCFA)', valeur: summary.ca_total || 0 },
        { indicateur: 'CA Payé (FCFA)', valeur: summary.ca_paye || 0 },
        { indicateur: 'CA Impayé (FCFA)', valeur: summary.ca_impaye || 0 },
        { indicateur: 'Taux Paiement Moyen (%)', valeur: summary.taux_paiement_moyen || 0 }
      ],
      headers: [
        { key: 'indicateur', label: 'Indicateur', type: 'text' },
        { key: 'valeur', label: 'Valeur', type: 'number' }
      ]
    })
  }
  
  // Feuille 2: Liste des Clients
  if (clients && clients.length > 0) {
    sheets.push({
      name: 'Clients',
      data: clients,
      headers: [
        { key: 'entreprise_id', label: 'ID Entreprise', type: 'text' },
        { key: 'raison_sociale', label: 'Raison Sociale', type: 'text' },
        { key: 'secteur_activite', label: 'Secteur', type: 'text' },
        { key: 'segment_client', label: 'Segment', type: 'text' },
        { key: 'chiffre_affaires_total', label: 'CA Total (FCFA)', type: 'currency' },
        { key: 'montant_paye', label: 'Montant Payé (FCFA)', type: 'currency' },
        { key: 'montant_impaye', label: 'Montant Impayé (FCFA)', type: 'currency' },
        { key: 'taux_paiement_pct', label: 'Taux Paiement (%)', type: 'percent' },
        { key: 'nombre_factures', label: 'Nb Factures', type: 'number' },
        { key: 'factures_en_retard', label: 'Factures en Retard', type: 'number' },
        { key: 'niveau_risque', label: 'Niveau Risque', type: 'text' },
        { key: 'nombre_demandes', label: 'Nb Demandes', type: 'number' },
        { key: 'lots_attribues', label: 'Lots Attribués', type: 'number' }
      ]
    })
  }
  
  exportToExcelMultiSheet(sheets, `Rapport_Clients_${new Date().toISOString().split('T')[0]}`)
}
