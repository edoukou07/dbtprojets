/**
 * CreancesAgeesDashboard Component
 * Displays aged receivables metrics by age and risk level
 */

import React, { useMemo } from 'react';
import {
  CreancesAgees,
  CreancesAgeesSummary,
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

interface CreancesAgeesDashboardProps {
  title?: string;
}

const CreancesAgeesDashboard: React.FC<CreancesAgeesDashboardProps> = ({
  title = 'Créances Âgées',
}) => {
  const { currentPage, pageSize, goToPage } = usePagination({ pageSize: 10 });
  const { sortColumn, sortDirection, toggleSorting } = useSorting();
  const { filters, updateFilters, clearFilters } = useFilters();

  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.tranche_anciennete) {
      params.append('tranche_anciennete', String(filters.tranche_anciennete));
    }
    if (filters.niveau_risque) {
      params.append('niveau_risque', String(filters.niveau_risque));
    }
    if (sortColumn) {
      params.append('ordering', `${sortDirection === 'desc' ? '-' : ''}${sortColumn}`);
    }
    params.append('limit', String(pageSize));
    params.append('offset', String((currentPage - 1) * pageSize));
    return `?${params.toString()}`;
  }, [filters, sortColumn, sortDirection, currentPage, pageSize]);

  const { data, loading, error, refetch } = useApi<any>(
    `/creances-agees/${queryParams}`,
    { cache: true, cacheTime: 5 * 60 * 1000 }
  );

  const { data: summary, loading: summaryLoading } = useApi<CreancesAgeesSummary>(
    '/creances-agees/summary/',
    { cache: true, cacheTime: 5 * 60 * 1000 }
  );

  const rows = data?.results || [];
  const totalCount = data?.count || 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  const columns: TableColumn<CreancesAgees>[] = [
    {
      key: 'tranche_anciennete',
      label: 'Tranche Ancienneté',
      sortable: true,
      width: '16%',
    },
    {
      key: 'niveau_risque',
      label: 'Niveau Risque',
      sortable: true,
      width: '14%',
    },
    {
      key: 'nombre_factures',
      label: 'Factures',
      type: 'number',
      sortable: true,
      width: '12%',
    },
    {
      key: 'nombre_entreprises',
      label: 'Entreprises',
      type: 'number',
      sortable: true,
      width: '12%',
    },
    {
      key: 'montant_total_factures',
      label: 'Montant Total (XOF)',
      type: 'currency',
      sortable: true,
      width: '23%',
      render: (value) =>
        new Intl.NumberFormat('fr-FR', {
          style: 'currency',
          currency: 'XOF',
          minimumFractionDigits: 0,
        }).format(value || 0),
    },
    {
      key: 'delai_moyen_jours',
      label: 'Délai Moyen (jours)',
      type: 'number',
      sortable: true,
      width: '16%',
    },
  ];

  const summaryCards = [
    {
      title: 'Factures Âgées',
      value: summary?.total_factures || 0,
      format: 'number' as const,
    },
    {
      title: 'Entreprises',
      value: summary?.total_entreprises || 0,
      format: 'number' as const,
    },
    {
      title: 'Montant Total (XOF)',
      value: summary?.montant_total || 0,
      format: 'currency' as const,
    },
    {
      title: 'Montant Moyen (XOF)',
      value: summary?.montant_moyen || 0,
      format: 'currency' as const,
    },
    {
      title: 'Délai Moyen',
      value: summary?.delai_moyen_jours?.toFixed(0) || '0',
      unit: 'jours',
      format: 'number' as const,
    },
  ];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>{title}</h1>
        <p>Analyse des créances âgées par ancienneté et niveau de risque</p>
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
            tranche_anciennete: {
              type: 'select',
              label: 'Tranche Ancienneté',
              options: [
                { value: '0_30', label: '0-30 jours' },
                { value: '31_60', label: '31-60 jours' },
                { value: '61_90', label: '61-90 jours' },
                { value: '91_180', label: '91-180 jours' },
                { value: '180_plus', label: '+180 jours' },
              ],
            },
            niveau_risque: {
              type: 'select',
              label: 'Niveau Risque',
              options: [
                { value: 'BAS', label: 'Bas' },
                { value: 'MOYEN', label: 'Moyen' },
                { value: 'ELEVE', label: 'Élevé' },
                { value: 'CRITIQUE', label: 'Critique' },
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

export default CreancesAgeesDashboard;
