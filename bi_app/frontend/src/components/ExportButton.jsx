import { useState } from 'react'
import { Download, FileSpreadsheet, FileText, File, Check } from 'lucide-react'
import * as XLSX from 'xlsx'
import jsPDF from 'jspdf'
import 'jspdf-autotable'

export default function ExportButton({ data, filename = 'export', title = 'Rapport', showPDF = true, showExcel = true, showCSV = true }) {
  const [isOpen, setIsOpen] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [exportSuccess, setExportSuccess] = useState(false)

  // Export Excel
  const exportToExcel = () => {
    setExporting(true)
    try {
      const ws = XLSX.utils.json_to_sheet(data)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Données')
      
      // Ajuster la largeur des colonnes
      const maxWidth = data.reduce((w, r) => Math.max(w, ...Object.values(r).map(v => String(v).length)), 10)
      ws['!cols'] = Object.keys(data[0] || {}).map(() => ({ wch: Math.min(maxWidth, 30) }))
      
      XLSX.writeFile(wb, `${filename}_${new Date().toISOString().split('T')[0]}.xlsx`)
      
      showSuccess()
    } catch (error) {
      console.error('Erreur export Excel:', error)
      alert('Erreur lors de l\'export Excel')
    } finally {
      setExporting(false)
    }
  }

  // Export CSV
  const exportToCSV = () => {
    setExporting(true)
    try {
      const ws = XLSX.utils.json_to_sheet(data)
      const csv = XLSX.utils.sheet_to_csv(ws)
      
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      
      showSuccess()
    } catch (error) {
      console.error('Erreur export CSV:', error)
      alert('Erreur lors de l\'export CSV')
    } finally {
      setExporting(false)
    }
  }

  // Export PDF
  const exportToPDF = () => {
    setExporting(true)
    try {
      const doc = new jsPDF()
      
      // Header
      doc.setFontSize(18)
      doc.setTextColor(31, 41, 55) // gray-800
      doc.text(title, 14, 20)
      
      doc.setFontSize(10)
      doc.setTextColor(107, 114, 128) // gray-500
      doc.text(`Généré le ${new Date().toLocaleDateString('fr-FR')}`, 14, 28)
      
      // Ligne de séparation
      doc.setDrawColor(229, 231, 235) // gray-200
      doc.line(14, 32, 196, 32)
      
      // Tableau
      if (data && data.length > 0) {
        const headers = Object.keys(data[0])
        const rows = data.map(row => Object.values(row))
        
        doc.autoTable({
          head: [headers],
          body: rows,
          startY: 38,
          theme: 'grid',
          styles: {
            fontSize: 8,
            cellPadding: 3,
          },
          headStyles: {
            fillColor: [59, 130, 246], // blue-500
            textColor: 255,
            fontStyle: 'bold',
          },
          alternateRowStyles: {
            fillColor: [249, 250, 251], // gray-50
          },
        })
      }
      
      // Footer avec pagination
      const pageCount = doc.internal.getNumberOfPages()
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i)
        doc.setFontSize(8)
        doc.setTextColor(156, 163, 175) // gray-400
        doc.text(
          `Page ${i} / ${pageCount}`,
          doc.internal.pageSize.width / 2,
          doc.internal.pageSize.height - 10,
          { align: 'center' }
        )
      }
      
      doc.save(`${filename}_${new Date().toISOString().split('T')[0]}.pdf`)
      
      showSuccess()
    } catch (error) {
      console.error('Erreur export PDF:', error)
      alert('Erreur lors de l\'export PDF')
    } finally {
      setExporting(false)
    }
  }

  const showSuccess = () => {
    setExportSuccess(true)
    setTimeout(() => {
      setExportSuccess(false)
      setIsOpen(false)
    }, 2000)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={!data || data.length === 0 || exporting}
        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {exportSuccess ? (
          <>
            <Check className="w-4 h-4 mr-2" />
            Exporté
          </>
        ) : exporting ? (
          <>
            <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Export...
          </>
        ) : (
          <>
            <Download className="w-4 h-4 mr-2" />
            Exporter
          </>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && !exporting && !exportSuccess && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          ></div>

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-20 overflow-hidden">
            <div className="py-1">
              {showExcel && (
                <button
                  onClick={exportToExcel}
                  className="w-full flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <FileSpreadsheet className="w-5 h-5 mr-3 text-green-600" />
                  <div className="text-left">
                    <div className="font-medium">Excel (.xlsx)</div>
                    <div className="text-xs text-gray-500">Format tableur</div>
                  </div>
                </button>
              )}

              {showCSV && (
                <button
                  onClick={exportToCSV}
                  className="w-full flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors border-t border-gray-100"
                >
                  <File className="w-5 h-5 mr-3 text-blue-600" />
                  <div className="text-left">
                    <div className="font-medium">CSV (.csv)</div>
                    <div className="text-xs text-gray-500">Données brutes</div>
                  </div>
                </button>
              )}

              {showPDF && (
                <button
                  onClick={exportToPDF}
                  className="w-full flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors border-t border-gray-100"
                >
                  <FileText className="w-5 h-5 mr-3 text-red-600" />
                  <div className="text-left">
                    <div className="font-medium">PDF (.pdf)</div>
                    <div className="text-xs text-gray-500">Rapport imprimable</div>
                  </div>
                </button>
              )}
            </div>

            {/* Info */}
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
              <p className="text-xs text-gray-600">
                {data?.length || 0} ligne{data?.length > 1 ? 's' : ''} de données
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
