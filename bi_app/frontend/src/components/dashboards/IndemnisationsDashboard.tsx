/**
 * IndemnisationsDashboard Component
 * Displays indemnisations metrics by zone and status
 */

import React, { useMemo } from 'react';
import {
  Indemnisations,
  IndemnisationsSummary,
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

interface IndemnisationsDashboardProps {
  title?: string;
}

const IndemnisationsDashboard: React.FC<IndemnisationsDashboardProps> = ({
  title = 'Gestion des Indemnisations',
}) => {
  const { currentPage, pageSize, goToPage } = usePagination({ pageSize: 10 });
  const { sortColumn, sortDirection, toggleSorting } = useSorting();
  const { filters, updateFilters, clearFilters } = useFilters();

  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.zone_id) params.append('zone_id', String(filters.zone_id));
    if (filters.annea) params.append('annea', String(filters.annea));
    if (filters.mois) params.append('mois', String(filters.mois));
    if (filters.statut) params.append('statut', String(filters.statut));
    if (sortColumn) {
      params.append('ordering', `${sortDirection === 'desc' ? '-' : ''}${sortColumn}`);
    }
    params.append('limit', String(pageSize));
    params.append('offset', String((currentPage - 1) * pageSize));
    return `?${params.toString()}`;
  }, [filters, sortColumn, sortDirection, currentPage, pageSize]);

  const { data, loading, error, refetch } = useApi<any>(
    `/indemnisations/${queryParams}`,
    { cache: true, cacheTime: 5 * 60 * 1000 }
  );

  const { data: summary, loading: summaryLoading } = useApi<IndemnisationsSummary>(
    '/indemnisations/summary/',
    { cache: true, cacheTime: 5 * 60 * 1000 }
  );

  const rows = data?.results || [];
  const totalCount = data?.count || 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  const columns: TableColumn<Indemnisations>[] = [
    {
      key: 'zone_name',
      label: 'Zone',
      sortable: true,
      width: '12%',
    },
    {
      key: 'annea',
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
      key: 'statut',
      label: 'Statut',
      sortable: true,
      width: '12%',
    },
    {
      key: 'nombre_indemnisations',
      label: 'Indemnisations',
      type: 'number',
      sortable: true,
      width: '13%',
    },
    {
      key: 'nombre_beneficiaires',
      label: 'Bénéficiaires',
      type: 'number',
      sortable: true,
      width: '13%',
    },
    {
      key: 'montant_total_restant',
      label: 'Montant Restant',
      type: 'currency',
      sortable: true,
      width: '15%',
      render: (value) => `${value?.toLocaleString('fr-FR', { style: 'currency', currency: 'XOF' })}`,
    },
  ];

  const summaryCards = [
    {
      title: 'Indemnisations',
      value: summary?.total_indemnisations || 0,
      format: 'number' as const,
    },
    {
      title: 'Bénéficiaires',
      value: summary?.total_beneficiaires || 0,
      format: 'number' as const,
    },
    {
      title: 'Montant Total Restant',
      value: summary?.total_montant_restant || 0,
      format: 'currency' as const,
    },
    {
      title: 'Montant Moyen',
      value: summary?.avg_montant_par_indemnisation?.toFixed(0) || '0',
      format: 'currency' as const,
    },
  ];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>{title}</h1>
        <p>Analyse des indemnisations par zone et statut</p>
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
            annea: {
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
            statut: {
              type: 'select',
              label: 'Statut',
              options: [
                { value: 'ACCEPTEE', label: 'Acceptée' },
                { value: 'PAYEE', label: 'Payée' },
                { value: 'REJETEE', label: 'Rejetée' },
                { value: 'EN_ATTENTE', label: 'En attente' },
              ],
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

export default IndemnisationsDashboard;
