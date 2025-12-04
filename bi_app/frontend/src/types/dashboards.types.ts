/**
 * TypeScript types and interfaces for Phase 2 dashboards
 * Corresponding to Django serializers from bi_app/backend/api/
 */

// ============================================================================
// API Response Types
// ============================================================================

/**
 * mart_implantation_suivi data
 * Source: dwh_marts_operationnel.mart_implantation_suivi
 */
export interface ImplantationSuivi {
  id?: number;
  zone_id: number;
  nom_zone: string;
  annee: number;
  mois: number;
  nombre_implantations: number;
  nombre_etapes: number;
  taux_completude_pct: number;
  pct_en_retard: number;
}

/**
 * Summary aggregation for implantation_suivi
 */
export interface ImplantationSuiviSummary {
  total_implantations: number;
  total_etapes: number;
  total_zones: number;
  avg_completude_pct: number;
  avg_retard_pct: number;
  zones_count: number;
}

/**
 * mart_indemnisations data
 * Source: dwh_marts_financier.mart_indemnisations
 */
export interface Indemnisations {
  id?: number;
  zone_id: number;
  zone_name: string;
  annea: number;
  mois: number;
  statut: string;
  nombre_indemnisations: number;
  nombre_beneficiaires: number;
  montant_total_restant: number;
}

/**
 * Summary aggregation for indemnisations
 */
export interface IndemnisationsSummary {
  total_indemnisations: number;
  total_beneficiaires: number;
  total_montant_restant: number;
  avg_montant_par_indemnisation: number;
  zones_count: number;
}

/**
 * mart_emplois_crees data
 * Source: dwh_marts_operationnel.mart_emplois_crees
 */
export interface EmploisCrees {
  id?: number;
  zone_id: number;
  zone_name: string;
  annea: number;
  mois: number;
  type_demande: string;
  statut: string;
  nombre_demandes: number;
  total_emplois: number;
  pct_expatries: number;
  pct_nationaux: number;
}

/**
 * Summary aggregation for emplois_crees
 */
export interface EmploisCreesSummary {
  total_demandes: number;
  total_emplois: number;
  total_zones: number;
  avg_emplois_par_demande: number;
  avg_pct_nationaux: number;
  avg_pct_expatries: number;
}

/**
 * mart_creances_agees data
 * Source: dwh_marts_financier.mart_creances_agees
 */
export interface CreancesAgees {
  id?: number;
  tranche_anciennete: string;
  niveau_risque: string;
  nombre_factures: number;
  nombre_entreprises: number;
  montant_total_factures: number;
  delai_moyen_jours: number;
}

/**
 * Summary aggregation for creances_agees
 */
export interface CreancesAgeesSummary {
  total_factures: number;
  total_entreprises: number;
  total_montant_factures: number;
  avg_delai_jours: number;
  max_montant_facture: number;
}

// ============================================================================
// API Request/Response Wrapper Types
// ============================================================================

/**
 * Generic paginated API response
 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Generic API error response
 */
export interface ApiError {
  detail?: string;
  error?: string;
  [key: string]: any;
}

/**
 * Filter parameters for API calls
 */
export interface FilterParams {
  [key: string]: string | number | boolean | undefined;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface DashboardPageProps {
  title: string;
  description?: string;
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  error?: string | null;
  pagination?: PaginationInfo;
  onPageChange?: (page: number) => void;
  onSortChange?: (column: string, direction: 'asc' | 'desc') => void;
  onFilterChange?: (filters: FilterParams) => void;
}

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  type?: 'text' | 'number' | 'date' | 'percentage' | 'currency';
  sortable?: boolean;
  searchable?: boolean;
  width?: string;
  render?: (value: any, row: T) => React.ReactNode;
}

export interface PaginationInfo {
  current_page: number;
  total_pages: number;
  total_count: number;
  page_size: number;
}

export interface FilterCardProps {
  filters: FilterParams;
  onFilterChange: (filters: FilterParams) => void;
  loading?: boolean;
}

export interface SummaryCardProps {
  title: string;
  value: number | string;
  unit?: string;
  format?: 'number' | 'currency' | 'percentage';
  trend?: {
    direction: 'up' | 'down';
    percentage: number;
  };
  icon?: React.ReactNode;
}

// ============================================================================
// State Management Types
// ============================================================================

export interface DashboardState<T> {
  data: T[];
  summary: any;
  filters: FilterParams;
  sorting: {
    column: string;
    direction: 'asc' | 'desc';
  };
  pagination: PaginationInfo;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export interface DashboardAction<T> {
  type: 'SET_DATA' | 'SET_FILTERS' | 'SET_SORTING' | 'SET_PAGINATION' | 
        'SET_LOADING' | 'SET_ERROR' | 'CLEAR_ERROR' | 'RESET';
  payload?: any;
}

// ============================================================================
// API Hook Types
// ============================================================================

export interface UseApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  cache?: boolean;
  cacheTime?: number;
  retries?: number;
  timeout?: number;
  dependencies?: any[];
}

export interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  refetch: () => Promise<void>;
  resetError: () => void;
}

export interface UseFetchResult<T> extends UseApiResult<T> {
  setData: (data: T) => void;
}

// ============================================================================
// Filtering & Sorting Types
// ============================================================================

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  column: string;
  direction: SortDirection;
}

export interface FilterConfig {
  [key: string]: {
    type: 'text' | 'select' | 'date' | 'range' | 'checkbox';
    label: string;
    options?: Array<{ value: string | number; label: string }>;
    defaultValue?: any;
  };
}

// ============================================================================
// Chart/Visualization Types
// ============================================================================

export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
  [key: string]: any;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'donut' | 'area';
  title: string;
  data: ChartDataPoint[];
  options?: {
    legend?: boolean;
    tooltip?: boolean;
    animation?: boolean;
    [key: string]: any;
  };
}

// ============================================================================
// Export Mart-specific types for convenience
// ============================================================================

export type MartsUnion = ImplantationSuivi | Indemnisations | EmploisCrees | CreancesAgees;
export type SummaryUnion = ImplantationSuiviSummary | IndemnisationsSummary | EmploisCreesSummary | CreancesAgeesSummary;
