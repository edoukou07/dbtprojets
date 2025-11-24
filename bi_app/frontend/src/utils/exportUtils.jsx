import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

/**
 * Export données en CSV
 */
export const exportToCSV = (data, filename = 'export.csv') => {
  if (!data || data.length === 0) {
    console.warn('Aucune donnée à exporter');
    return;
  }

  // Obtenir les en-têtes
  const headers = Object.keys(data[0]);
  
  // Créer CSV
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        // Échapper les guillemets et encapsuler si contient virgule
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    )
  ].join('\n');

  // Télécharger
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
};

/**
 * Export données en Excel
 */
export const exportToExcel = (data, filename = 'export', sheetName = 'Données') => {
  if (!data || data.length === 0) {
    console.warn('Aucune donnée à exporter');
    return;
  }

  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, sheetName);
  
  // Style colonne largeur automatique
  const colWidths = Object.keys(data[0]).map(key => ({
    wch: Math.max(key.length, 12)
  }));
  ws['!cols'] = colWidths;

  XLSX.writeFile(wb, `${filename}_${new Date().toISOString().split('T')[0]}.xlsx`);
};

/**
 * Export en PDF avec tableau
 */
export const exportToPDF = (data, filename = 'export', title = 'Export Données') => {
  if (!data || data.length === 0) {
    console.warn('Aucune donnée à exporter');
    return;
  }

  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  // Titre
  doc.setFontSize(16);
  doc.text(title, 14, 15);

  // Date d'export
  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text(`Généré le: ${new Date().toLocaleString('fr-FR')}`, 14, 25);

  // Tableau
  const headers = Object.keys(data[0]);
  const rows = data.map(item =>
    headers.map(header => {
      const value = item[header];
      if (typeof value === 'number') {
        return new Intl.NumberFormat('fr-FR').format(value);
      }
      return value || '-';
    })
  );

  autoTable(doc, {
    head: [headers],
    body: rows,
    startY: 35,
    margin: { top: 35, right: 14, bottom: 14, left: 14 },
    theme: 'grid',
    headerStyles: {
      fillColor: [15, 165, 233],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      halign: 'center'
    },
    bodyStyles: {
      textColor: [50, 50, 50],
    },
    alternateRowStyles: {
      fillColor: [245, 245, 245]
    },
    columnStyles: {
      // Centrer les colonnes numériques
      ...Object.fromEntries(
        headers.map((h, i) => [
          i,
          data.some(d => typeof d[h] === 'number') ? { halign: 'right' } : {}
        ])
      )
    },
    didDrawPage: function(data) {
      // Pied de page
      const pageSize = doc.internal.pageSize;
      const pageHeight = pageSize.getHeight();
      const pageWidth = pageSize.getWidth();
      doc.setFontSize(10);
      doc.setTextColor(150);
      doc.text(
        `Page ${data.pageCount}`,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );
    }
  });

  doc.save(`${filename}_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Export dashboard complet (PDF multi-page)
 */
export const exportDashboardPDF = (sections, title = 'Dashboard Export') => {
  const doc = new jsPDF();
  let isFirstPage = true;

  sections.forEach((section, index) => {
    if (!isFirstPage) {
      doc.addPage();
    }

    const pageWidth = doc.internal.pageSize.getWidth();
    const startY = isFirstPage ? 30 : 20;

    // Titre section
    doc.setFontSize(14);
    doc.setTextColor(30, 41, 59);
    doc.text(section.title, 14, startY);

    // Tableau si présent
    if (section.data && section.data.length > 0) {
      const headers = Object.keys(section.data[0]);
      const rows = section.data.map(item =>
        headers.map(header => item[header] || '-')
      );

      autoTable(doc, {
        head: [headers],
        body: rows,
        startY: startY + 8,
        margin: { top: startY + 8, right: 14, bottom: 14, left: 14 },
        theme: 'striped',
        headerStyles: {
          fillColor: [15, 165, 233],
          textColor: [255, 255, 255],
          fontStyle: 'bold'
        },
        columnStyles: {
          ...Object.fromEntries(
            headers.map((h, i) => [
              i,
              section.data.some(d => typeof d[h] === 'number') ? { halign: 'right' } : {}
            ])
          )
        }
      });
    }

    isFirstPage = false;
  });

  // Page de couverture
  const doc2 = new jsPDF();
  doc2.setFontSize(24);
  doc2.text(title, 14, 50);
  doc2.setFontSize(12);
  doc2.text(`Généré le: ${new Date().toLocaleString('fr-FR')}`, 14, 80);
  doc2.addPage();
  
  // Fusionner
  const pages = doc.internal.pages;
  doc2.internal.pages.push(...pages.slice(1));
  doc2.internal.pages.splice(1, 1);

  doc2.save(`${title}_${new Date().toISOString().split('T')[0]}.pdf`);
};

/**
 * Composant boutons export réutilisable
 */
export const ExportButtons = ({ 
  data, 
  filename = 'export',
  formats = ['csv', 'excel', 'pdf'],
  className = ''
}) => {
  const handleExport = (format) => {
    switch (format) {
      case 'csv':
        exportToCSV(data, filename);
        break;
      case 'excel':
        exportToExcel(data, filename);
        break;
      case 'pdf':
        exportToPDF(data, filename);
        break;
      default:
        break;
    }
  };

  return (
    <div className={`flex gap-2 ${className}`}>
      {formats.includes('csv') && (
        <button
          onClick={() => handleExport('csv')}
          className="px-3 py-1 text-sm bg-green-50 text-green-700 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
          title="Exporter en CSV"
        >
          📊 CSV
        </button>
      )}
      {formats.includes('excel') && (
        <button
          onClick={() => handleExport('excel')}
          className="px-3 py-1 text-sm bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
          title="Exporter en Excel"
        >
          📈 Excel
        </button>
      )}
      {formats.includes('pdf') && (
        <button
          onClick={() => handleExport('pdf')}
          className="px-3 py-1 text-sm bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
          title="Exporter en PDF"
        >
          📄 PDF
        </button>
      )}
    </div>
  );
};
