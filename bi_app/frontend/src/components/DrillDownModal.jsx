import { X, ChevronRight, ExternalLink } from 'lucide-react'
import { useState } from 'react'

export default function DrillDownModal({ isOpen, onClose, title, data, columns, breadcrumb = [] }) {
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  if (!isOpen) return null

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = data?.slice(indexOfFirstItem, indexOfLastItem) || []
  const totalPages = Math.ceil((data?.length || 0) / itemsPerPage)

  const formatValue = (value) => {
    if (value === null || value === undefined) return '-'
    if (typeof value === 'number') {
      if (value > 1000000) return `${(value / 1000000).toFixed(2)} M`
      if (value > 1000) return `${(value / 1000).toFixed(2)} K`
      return value.toLocaleString('fr-FR')
    }
    return value
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      ></div>

      {/* Modal */}
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4">
          <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[90vh] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{title}</h2>
                {breadcrumb.length > 0 && (
                  <div className="flex items-center mt-1 text-sm text-gray-500">
                    {breadcrumb.map((crumb, index) => (
                      <span key={index} className="flex items-center">
                        {index > 0 && <ChevronRight className="w-4 h-4 mx-1" />}
                        <span className={index === breadcrumb.length - 1 ? 'font-medium text-blue-600' : ''}>
                          {crumb}
                        </span>
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto px-6 py-4">
              {data && data.length > 0 ? (
                <>
                  {/* Stats summary */}
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-sm text-blue-600 font-medium">Total Lignes</p>
                      <p className="text-2xl font-bold text-blue-900">{data.length}</p>
                    </div>
                    {columns.find(col => col.type === 'currency') && (
                      <div className="bg-green-50 rounded-lg p-4">
                        <p className="text-sm text-green-600 font-medium">
                          Total {columns.find(col => col.type === 'currency').label}
                        </p>
                        <p className="text-2xl font-bold text-green-900">
                          {data.reduce((sum, row) => sum + (parseFloat(row[columns.find(col => col.type === 'currency').key]) || 0), 0).toLocaleString('fr-FR', { minimumFractionDigits: 0 })} F
                        </p>
                      </div>
                    )}
                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm text-purple-600 font-medium">Page</p>
                      <p className="text-2xl font-bold text-purple-900">{currentPage} / {totalPages}</p>
                    </div>
                  </div>

                  {/* Table */}
                  <div className="overflow-x-auto border border-gray-200 rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {columns.map((col) => (
                            <th
                              key={col.key}
                              className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
                            >
                              {col.label}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {currentItems.map((row, idx) => (
                          <tr key={idx} className="hover:bg-gray-50 transition-colors">
                            {columns.map((col) => (
                              <td key={col.key} className="px-4 py-3 text-sm text-gray-900">
                                {col.type === 'currency' ? (
                                  <span className="font-medium text-green-600">
                                    {parseFloat(row[col.key])?.toLocaleString('fr-FR', { minimumFractionDigits: 0 })} F
                                  </span>
                                ) : col.type === 'date' ? (
                                  <span className="text-gray-600">
                                    {row[col.key] ? new Date(row[col.key]).toLocaleDateString('fr-FR') : '-'}
                                  </span>
                                ) : col.type === 'status' ? (
                                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                    row[col.key] === 'Payé' || row[col.key] === 'Clôturé' || row[col.key] === 'Approuvé'
                                      ? 'bg-green-100 text-green-800'
                                      : row[col.key] === 'En attente' || row[col.key] === 'En cours'
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}>
                                    {row[col.key]}
                                  </span>
                                ) : col.type === 'link' ? (
                                  <a href={col.href?.(row)} className="text-blue-600 hover:text-blue-800 flex items-center">
                                    {formatValue(row[col.key])}
                                    <ExternalLink className="w-3 h-3 ml-1" />
                                  </a>
                                ) : (
                                  formatValue(row[col.key])
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">Aucune donnée disponible</p>
                </div>
              )}
            </div>

            {/* Footer with Pagination */}
            {data && data.length > 0 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  Affichage de {indexOfFirstItem + 1} à {Math.min(indexOfLastItem, data.length)} sur {data.length} lignes
                </p>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Précédent
                  </button>
                  
                  <div className="flex items-center space-x-1">
                    {[...Array(totalPages)].map((_, idx) => {
                      const page = idx + 1
                      // Afficher seulement quelques pages autour de la page actuelle
                      if (page === 1 || page === totalPages || (page >= currentPage - 1 && page <= currentPage + 1)) {
                        return (
                          <button
                            key={page}
                            onClick={() => setCurrentPage(page)}
                            className={`px-3 py-1 rounded-lg text-sm font-medium ${
                              currentPage === page
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-700 hover:bg-gray-100'
                            }`}
                          >
                            {page}
                          </button>
                        )
                      } else if (page === currentPage - 2 || page === currentPage + 2) {
                        return <span key={page} className="px-2 text-gray-400">...</span>
                      }
                      return null
                    })}
                  </div>

                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Suivant
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
