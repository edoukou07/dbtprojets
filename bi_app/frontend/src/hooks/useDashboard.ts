/**
 * Custom React hooks for API communication and state management
 * Handles caching, error handling, loading states, and retry logic
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { FilterParams, UseApiOptions, UseApiResult, UseFetchResult, ApiError } from '../types/dashboards.types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const DEFAULT_CACHE_TIME = 5 * 60 * 1000; // 5 minutes

// ============================================================================
// Cache Management
// ============================================================================

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const apiCache = new Map<string, CacheEntry<any>>();

const getCacheKey = (endpoint: string, params?: FilterParams): string => {
  const paramString = params ? JSON.stringify(params) : '';
  return `${endpoint}:${paramString}`;
};

const getFromCache = <T,>(key: string, maxAge: number): T | null => {
  const entry = apiCache.get(key);
  if (!entry) return null;

  const age = Date.now() - entry.timestamp;
  if (age > maxAge) {
    apiCache.delete(key);
    return null;
  }

  return entry.data as T;
};

const setInCache = <T,>(key: string, data: T): void => {
  apiCache.set(key, {
    data,
    timestamp: Date.now(),
  });
};

export const clearCache = (): void => {
  apiCache.clear();
};

export const invalidateCacheByEndpoint = (endpoint: string): void => {
  const keysToDelete: string[] = [];
  apiCache.forEach((_, key) => {
    if (key.startsWith(endpoint)) {
      keysToDelete.push(key);
    }
  });
  keysToDelete.forEach(key => apiCache.delete(key));
};

// ============================================================================
// useApi Hook - Generic API fetching with caching
// ============================================================================

export const useApi = <T,>(
  endpoint: string,
  options: UseApiOptions = {}
): UseApiResult<T> => {
  const {
    method = 'GET',
    headers = {},
    cache = true,
    cacheTime = DEFAULT_CACHE_TIME,
    retries = 3,
    timeout = 30000,
    dependencies = [],
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const retryCountRef = useRef(0);

  const fetchData = useCallback(async () => {
    const cacheKey = getCacheKey(endpoint);

    // Check cache first
    if (cache && method === 'GET') {
      const cachedData = getFromCache<T>(cacheKey, cacheTime);
      if (cachedData) {
        setData(cachedData);
        setLoading(false);
        setError(null);
        return;
      }
    }

    try {
      setLoading(true);
      setError(null);
      retryCountRef.current = 0;

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw {
          detail: `HTTP ${response.status}: ${response.statusText}`,
          status: response.status,
        };
      }

      const responseData = await response.json();
      setData(responseData);

      // Cache successful response
      if (cache && method === 'GET') {
        setInCache(cacheKey, responseData);
      }

      setError(null);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setError({ detail: 'Request timeout' });
      } else {
        setError(err);
      }

      // Retry logic
      if (retryCountRef.current < retries) {
        retryCountRef.current += 1;
        const backoffDelay = Math.pow(2, retryCountRef.current) * 1000;
        setTimeout(fetchData, backoffDelay);
      }
    } finally {
      setLoading(false);
    }
  }, [endpoint, method, headers, cache, cacheTime, retries, timeout]);

  useEffect(() => {
    fetchData();
  }, [fetchData, ...dependencies]);

  const refetch = useCallback(async () => {
    const cacheKey = getCacheKey(endpoint);
    if (cache) {
      apiCache.delete(cacheKey);
    }
    await fetchData();
  }, [endpoint, fetchData, cache]);

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  return { data, loading, error, refetch, resetError };
};

// ============================================================================
// useFetch Hook - Simplified API hook with data setter
// ============================================================================

export const useFetch = <T,>(
  endpoint: string,
  options: UseApiOptions = {}
): UseFetchResult<T> => {
  const [data, setDataState] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const apiResult = useApi<T>(endpoint, options);

  useEffect(() => {
    if (apiResult.data) {
      setDataState(apiResult.data);
    }
  }, [apiResult.data]);

  useEffect(() => {
    setLoading(apiResult.loading);
  }, [apiResult.loading]);

  useEffect(() => {
    setError(apiResult.error);
  }, [apiResult.error]);

  return {
    data: data || apiResult.data,
    loading,
    error,
    refetch: apiResult.refetch,
    resetError: apiResult.resetError,
    setData: setDataState,
  };
};

// ============================================================================
// usePagination Hook - Manage pagination state
// ============================================================================

export interface UsePaginationOptions {
  initialPage?: number;
  pageSize?: number;
}

export interface UsePaginationResult {
  currentPage: number;
  pageSize: number;
  goToPage: (page: number) => void;
  nextPage: () => void;
  previousPage: () => void;
  setPageSize: (size: number) => void;
}

export const usePagination = (options: UsePaginationOptions = {}): UsePaginationResult => {
  const { initialPage = 1, pageSize: initialPageSize = 10 } = options;

  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.max(1, page));
  }, []);

  const nextPage = useCallback(() => {
    setCurrentPage(prev => prev + 1);
  }, []);

  const previousPage = useCallback(() => {
    setCurrentPage(prev => Math.max(1, prev - 1));
  }, []);

  const setPageSizeHandler = useCallback((size: number) => {
    setPageSize(Math.max(1, size));
    setCurrentPage(1); // Reset to first page
  }, []);

  return {
    currentPage,
    pageSize,
    goToPage,
    nextPage,
    previousPage,
    setPageSize: setPageSizeHandler,
  };
};

// ============================================================================
// useSorting Hook - Manage sorting state
// ============================================================================

export interface UseSortingOptions {
  initialColumn?: string;
  initialDirection?: 'asc' | 'desc';
}

export interface UseSortingResult {
  sortColumn: string | null;
  sortDirection: 'asc' | 'desc';
  setSorting: (column: string, direction?: 'asc' | 'desc') => void;
  toggleSorting: (column: string) => void;
}

export const useSorting = (options: UseSortingOptions = {}): UseSortingResult => {
  const { initialColumn, initialDirection = 'asc' } = options;

  const [sortColumn, setSortColumn] = useState<string | null>(initialColumn || null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>(initialDirection);

  const setSorting = useCallback((column: string, direction: 'asc' | 'desc' = 'asc') => {
    setSortColumn(column);
    setSortDirection(direction);
  }, []);

  const toggleSorting = useCallback((column: string) => {
    if (sortColumn === column) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  }, [sortColumn]);

  return {
    sortColumn,
    sortDirection,
    setSorting,
    toggleSorting,
  };
};

// ============================================================================
// useFilters Hook - Manage filter state
// ============================================================================

export const useFilters = (initialFilters: FilterParams = {}) => {
  const [filters, setFilters] = useState<FilterParams>(initialFilters);

  const updateFilter = useCallback((key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  }, []);

  const updateFilters = useCallback((newFilters: FilterParams) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
    }));
  }, []);

  const removeFilter = useCallback((key: string) => {
    setFilters(prev => {
      const { [key]: _, ...rest } = prev;
      return rest;
    });
  }, []);

  const clearFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  return {
    filters,
    updateFilter,
    updateFilters,
    removeFilter,
    clearFilters,
  };
};

// ============================================================================
// useDebounce Hook - Debounce values for API calls
// ============================================================================

export const useDebounce = <T,>(value: T, delay: number = 500): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

// ============================================================================
// useLocalStorage Hook - Persist state to localStorage
// ============================================================================

export const useLocalStorage = <T,>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
};
