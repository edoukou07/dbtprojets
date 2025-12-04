/**
 * DashboardTable Component
 * Reusable sortable and paginated table for dashboards
 */

import React from 'react';
import { TableColumn, PaginationInfo } from '../../types/dashboards.types';

interface DashboardTableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  pagination?: PaginationInfo;
  onPageChange?: (page: number) => void;
  onSortChange?: (column: string, direction: 'asc' | 'desc') => void;
  rowKey?: (row: T, index: number) => string | number;
  loading?: boolean;
  emptyMessage?: string;
}

const DashboardTable = React.forwardRef<HTMLTableElement, DashboardTableProps<any>>(
  (
    {
      columns,
      data,
      pagination,
      onPageChange,
      onSortChange,
      rowKey = (_, index) => index,
      loading = false,
      emptyMessage = 'Aucune donnée disponible',
    },
    ref
  ) => {
    const handleColumnClick = (column: TableColumn<any>) => {
      if (column.sortable && onSortChange) {
        const newDirection = column.key === (column as any).currentSort?.column
          ? (column as any).currentSort?.direction === 'asc'
            ? 'desc'
            : 'asc'
          : 'asc';
        onSortChange(column.key, newDirection);
      }
    };

    const renderCellValue = (column: TableColumn<any>, row: any) => {
      const value = row[column.key];

      if (column.render) {
        return column.render(value, row);
      }

      switch (column.type) {
        case 'currency':
          return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'XOF',
            minimumFractionDigits: 0,
          }).format(value || 0);

        case 'percentage':
          return `${(value || 0).toFixed(1)}%`;

        case 'date':
          return new Date(value).toLocaleDateString('fr-FR');

        case 'number':
          return new Intl.NumberFormat('fr-FR').format(value || 0);

        default:
          return value ?? '-';
      }
    };

    return (
      <div className="dashboard-table-wrapper">
        <table ref={ref} className="dashboard-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  style={{ width: column.width }}
                  className={column.sortable ? 'sortable' : ''}
                  onClick={() => handleColumnClick(column)}
                >
                  <div className="table-header-content">
                    <span>{column.label}</span>
                    {column.sortable && (
                      <span className="sort-indicator" aria-label="Sortable">
                        ⇅
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="loading-cell">
                  <span className="spinner" />
                  Chargement...
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="empty-cell">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, index) => (
                <tr key={rowKey(row, index)} className="table-row">
                  {columns.map((column) => (
                    <td
                      key={`${rowKey(row, index)}-${column.key}`}
                      className={`cell cell-${column.type || 'text'}`}
                    >
                      {renderCellValue(column, row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>

        {pagination && (
          <div className="table-pagination">
            <div className="pagination-info">
              Affichage {((pagination.current_page - 1) * pagination.page_size) + 1} à{' '}
              {Math.min(pagination.current_page * pagination.page_size, pagination.total_count)} sur{' '}
              {pagination.total_count} résultats
            </div>

            <div className="pagination-controls">
              <button
                className="pagination-button"
                onClick={() => onPageChange?.(pagination.current_page - 1)}
                disabled={pagination.current_page === 1}
              >
                ← Précédent
              </button>

              <div className="page-numbers">
                {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                  const pageNum = Math.max(1, pagination.current_page - 2) + i;
                  if (pageNum <= pagination.total_pages) {
                    return (
                      <button
                        key={pageNum}
                        className={`page-number ${
                          pageNum === pagination.current_page ? 'active' : ''
                        }`}
                        onClick={() => onPageChange?.(pageNum)}
                      >
                        {pageNum}
                      </button>
                    );
                  }
                  return null;
                })}
              </div>

              <button
                className="pagination-button"
                onClick={() => onPageChange?.(pagination.current_page + 1)}
                disabled={pagination.current_page >= pagination.total_pages}
              >
                Suivant →
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }
);

DashboardTable.displayName = 'DashboardTable';

export default DashboardTable;
