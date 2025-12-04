/**
 * ImplantationSuiviDashboard Component
 * Displays suivi implantation metrics by zone
 */

import React, { useMemo } from 'react';
import {
  ImplantationSuivi,
  ImplantationSuiviSummary,
  FilterParams,
  TableColumn,
} from '../../types/dashboards.types';
import {
  useApi,
  usePagination,
  useSorting,
  useFilters,
} from '../../hooks/useDashboard';
import DashboardTable from '../common/DashboardTable';
import SummaryCards from '../common/SummaryCards';
import FilterPanel from '../common/FilterPanel';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';

interface ImplantationSuiviDashboardProps {
  title?: string;
}

const ImplantationSuiviDashboard: React.FC<ImplantationSuiviDashboardProps> = ({
  title = 'Suivi des Implantations',
}) => {
  const { currentPage, pageSize, goToPage } = usePagination({ pageSize: 10 });
  const { sortColumn, sortDirection, toggleSorting } = useSorting();
  const { filters, updateFilters, clearFilters } = useFilters();

  // Build query parameters
  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.zone_id) params.append('zone_id', String(filters.zone_id));
    if (filters.annee) params.append('annee', String(filters.annee));
    if (filters.mois) params.append('mois', String(filters.mois));
    if (sortColumn) {
      params.append('ordering', `${sortDirection === 'desc' ? '-' : ''}${sortColumn}`);
    }
    params.append('limit', String(pageSize));
    params.append('offset', String((currentPage - 1) * pageSize));
    return `?${params.toString()}`;
  }, [filters, sortColumn, sortDirection, currentPage, pageSize]);

  // Fetch data
  const { data, loading, error, refetch } = useApi<any>(
    `/implantation-suivi/${queryParams}`,
    {
      cache: true,
      cacheTime: 5 * 60 * 1000,
    }
  );

  const { data: summary, loading: summaryLoading } = useApi<ImplantationSuiviSummary>(
    '/implantation-suivi/summary/',
    { cache: true, cacheTime: 5 * 60 * 1000 }
  );

  // Parse data
  const rows = data?.results || [];
  const totalCount = data?.count || 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  // Table columns
  const columns: TableColumn<ImplantationSuivi>[] = [
    {
      key: 'nom_zone',
      label: 'Zone',
      sortable: true,
      width: '15%',
    },
    {
      key: 'annee',
      label: 'Année',
      type: 'number',
      sortable: true,
      width: '10%',
    },
    {
      key: 'mois',
      label: 'Mois',
      type: 'number',
      sortable: true,
      width: '10%',
    },
    {
      key: 'nombre_implantations',
      label: 'Implantations',
      type: 'number',
      sortable: true,
      width: '12%',
    },
    {
      key: 'nombre_etapes',
      label: 'Étapes',
      type: 'number',
      sortable: true,
      width: '10%',
    },
    {
      key: 'taux_completude_pct',
      label: 'Complétude',
      type: 'percentage',
      sortable: true,
      width: '12%',
      render: (value) => `${value?.toFixed(1)}%`,
    },
    {
      key: 'pct_en_retard',
      label: 'En Retard',
      type: 'percentage',
      sortable: true,
      width: '12%',
      render: (value) => `${value?.toFixed(1)}%`,
    },
  ];

  const summaryCards = [
    {
      title: 'Implantations',
      value: summary?.total_implantations || 0,
      format: 'number' as const,
    },
    {
      title: 'Étapes',
      value: summary?.total_etapes || 0,
      format: 'number' as const,
    },
    {
      title: 'Zones',
      value: summary?.total_zones || 0,
      format: 'number' as const,
    },
    {
      title: 'Complétude Moyenne',
      value: summary?.avg_completude_pct?.toFixed(1) || '0',
      unit: '%',
      format: 'percentage' as const,
    },
  ];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>{title}</h1>
        <p>Suivi des étapes d'implantation par zone</p>
      </header>

      {error && <ErrorAlert error={error} onRetry={refetch} />}

      <div className="summary-section">
        <SummaryCards cards={summaryCards} loading={summaryLoading} />
      </div>

      <div className="filter-section">
        <FilterPanel
          filters={filters}
          onFilterChange={updateFilters}
          onClearFilters={clearFilters}
          filterConfig={{
            zone_id: {
              type: 'select',
              label: 'Zone',
              options: [
                { value: 1, label: 'Zone 1' },
                { value: 2, label: 'Zone 2' },
                { value: 3, label: 'Zone 3' },
                { value: 4, label: 'Zone 4' },
              ],
            },
            annee: {
              type: 'range',
              label: 'Année',
            },
            mois: {
              type: 'select',
              label: 'Mois',
              options: Array.from({ length: 12 }, (_, i) => ({
                value: i + 1,
                label: new Date(2024, i).toLocaleString('fr-FR', { month: 'long' }),
              })),
            },
          }}
        />
      </div>

      <div className="table-section">
        {loading ? (
          <LoadingSpinner />
        ) : (
          <DashboardTable
            columns={columns}
            data={rows}
            pagination={{
              current_page: currentPage,
              total_pages: totalPages,
              total_count: totalCount,
              page_size: pageSize,
            }}
            onPageChange={goToPage}
            onSortChange={(column, direction) => toggleSorting(column)}
          />
        )}
      </div>
    </div>
  );
};

export default ImplantationSuiviDashboard;
