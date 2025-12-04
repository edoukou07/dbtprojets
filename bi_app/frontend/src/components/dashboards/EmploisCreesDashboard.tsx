/**
 * EmploisCreesDashboard Component
 * Displays employment creation metrics by type and status
 */

import React, { useMemo } from 'react';
import {
  EmploisCrees,
  EmploisCreesSummary,
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

interface EmploisCreesDashboardProps {
  title?: string;
}

const EmploisCreesDashboard: React.FC<EmploisCreesDashboardProps> = ({
  title = 'Emplois Créés',
}) => {
  const { currentPage, pageSize, goToPage } = usePagination({ pageSize: 10 });
  const { sortColumn, sortDirection, toggleSorting } = useSorting();
  const { filters, updateFilters, clearFilters } = useFilters();

  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.zone_id) params.append('zone_id', String(filters.zone_id));
    if (filters.annea) params.append('annea', String(filters.annea));
    if (filters.mois) params.append('mois', String(filters.mois));
    if (filters.type_demande) params.append('type_demande', String(filters.type_demande));
    if (filters.statut) params.append('statut', String(filters.statut));
    if (sortColumn) {
      params.append('ordering', `${sortDirection === 'desc' ? '-' : ''}${sortColumn}`);
    }
    params.append('limit', String(pageSize));
    params.append('offset', String((currentPage - 1) * pageSize));
    return `?${params.toString()}`;
  }, [filters, sortColumn, sortDirection, currentPage, pageSize]);

  const { data, loading, error, refetch } = useApi<any>(
    `/emplois-crees/${queryParams}`,
    { cache: true, cacheTime: 5 * 60 * 1000 }
  );

  const { data: summary, loading: summaryLoading } = useApi<EmploisCreesSummary>(
    '/emplois-crees/summary/',
    { cache: true, cacheTime: 5 * 60 * 1000 }
  );

  const rows = data?.results || [];
  const totalCount = data?.count || 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  const columns: TableColumn<EmploisCrees>[] = [
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
      key: 'type_demande',
      label: 'Type Demande',
      sortable: true,
      width: '12%',
    },
    {
      key: 'statut',
      label: 'Statut',
      sortable: true,
      width: '11%',
    },
    {
      key: 'nombre_demandes',
      label: 'Demandes',
      type: 'number',
      sortable: true,
      width: '10%',
    },
    {
      key: 'total_emplois',
      label: 'Emplois',
      type: 'number',
      sortable: true,
      width: '10%',
    },
    {
      key: 'pct_nationaux',
      label: 'Nationaux %',
      type: 'percentage',
      sortable: true,
      width: '12%',
      render: (value) => `${value?.toFixed(1)}%`,
    },
    {
      key: 'pct_expatries',
      label: 'Expatriés %',
      type: 'percentage',
      sortable: true,
      width: '12%',
      render: (value) => `${value?.toFixed(1)}%`,
    },
  ];

  const summaryCards = [
    {
      title: 'Demandes',
      value: summary?.total_demandes || 0,
      format: 'number' as const,
    },
    {
      title: 'Emplois Créés',
      value: summary?.total_emplois || 0,
      format: 'number' as const,
    },
    {
      title: 'Zones',
      value: summary?.total_zones || 0,
      format: 'number' as const,
    },
    {
      title: 'Taux Nationaux',
      value: summary?.avg_pct_nationaux?.toFixed(1) || '0',
      unit: '%',
      format: 'percentage' as const,
    },
  ];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>{title}</h1>
        <p>Analyse des emplois créés par type et statut</p>
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
            type_demande: {
              type: 'select',
              label: 'Type Demande',
              options: [
                { value: 'CREATION', label: 'Création' },
                { value: 'EXTENSION', label: 'Extension' },
                { value: 'REHABILITATION', label: 'Réhabilitation' },
              ],
            },
            statut: {
              type: 'select',
              label: 'Statut',
              options: [
                { value: 'EN_COURS', label: 'En cours' },
                { value: 'VALIDEE', label: 'Validée' },
                { value: 'REJETEE', label: 'Rejetée' },
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

export default EmploisCreesDashboard;
