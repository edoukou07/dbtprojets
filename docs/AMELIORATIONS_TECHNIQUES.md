# Plan d'Amélioration Technique - SIGETI BI

## Table des Matières
1. [Performance & Optimisation](#1-performance--optimisation)
2. [Visualisations de Données](#2-visualisations-de-données)
3. [Fonctionnalités Métier](#3-fonctionnalités-métier)
4. [UX/UI](#4-uxui)
5. [Sécurité & Gouvernance](#5-sécurité--gouvernance)
6. [Architecture Technique](#6-architecture-technique)
7. [Nouvelles Fonctionnalités](#7-nouvelles-fonctionnalités)
8. [Data Quality](#8-data-quality)
9. [Documentation & Formation](#9-documentation--formation)
10. [Plan de Mise en Œuvre](#10-plan-de-mise-en-œuvre)

---

## 1. Performance & Optimisation

### 1.1 Cache Redis - Backend

#### Installation
```bash
pip install redis django-redis
```

#### Configuration Django (`settings.py`)
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'sigeti_bi',
        'TIMEOUT': 900,  # 15 minutes par défaut
    }
}

# Cache pour sessions (optionnel)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

#### Implémentation dans les vues
```python
# bi_app/backend/analytics/views.py
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
import hashlib
import json

# Méthode 1 : Décorateur simple (15 minutes)
@cache_page(60 * 15)
@api_view(['GET'])
def occupation_summary(request):
    # Cette vue est mise en cache automatiquement
    data = calculate_occupation_summary()
    return Response(data)

# Méthode 2 : Cache manuel avec clé personnalisée
@api_view(['GET'])
def occupation_by_zone(request):
    # Générer une clé unique basée sur les paramètres
    zone_filter = request.GET.get('zone', 'all')
    cache_key = f'occupation_by_zone_{zone_filter}'
    
    # Essayer de récupérer du cache
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return Response({
            'data': cached_data,
            'cached': True,
            'timestamp': cache.get(f'{cache_key}_timestamp')
        })
    
    # Calculer si pas en cache
    data = calculate_occupation_by_zone(zone_filter)
    
    # Mettre en cache pour 15 minutes
    cache.set(cache_key, data, 60 * 15)
    cache.set(f'{cache_key}_timestamp', timezone.now().isoformat(), 60 * 15)
    
    return Response({
        'data': data,
        'cached': False,
        'timestamp': timezone.now().isoformat()
    })

# Méthode 3 : Cache avec invalidation intelligente
def invalidate_occupation_cache():
    """Invalider le cache quand les données changent"""
    cache.delete_pattern('occupation_*')
    cache.delete_pattern('zone_details_*')

# Signal pour invalider le cache automatiquement
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=MartOccupationZones)
def invalidate_cache_on_data_change(sender, **kwargs):
    invalidate_occupation_cache()
```

#### Utilitaire de cache réutilisable
```python
# bi_app/backend/analytics/cache_utils.py
from django.core.cache import cache
from functools import wraps
import hashlib
import json
from datetime import datetime

def cached_query(timeout=900, key_prefix=''):
    """
    Décorateur pour mettre en cache le résultat d'une fonction
    
    Usage:
        @cached_query(timeout=1800, key_prefix='stats')
        def get_complex_stats(param1, param2):
            # Calculs lourds
            return data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer une clé unique basée sur les arguments
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            key_hash = hashlib.md5(
                json.dumps(key_data, sort_keys=True, default=str).encode()
            ).hexdigest()
            cache_key = f'{key_prefix}:{func.__name__}:{key_hash}'
            
            # Vérifier le cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Calculer et mettre en cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator

# Exemple d'utilisation
@cached_query(timeout=1800, key_prefix='occupation')
def calculate_top_zones(limit=5):
    # Requête lourde
    zones = MartOccupationZones.objects.all().order_by('-taux_occupation_pct')[:limit]
    return list(zones.values())
```

### 1.2 Pagination Côté Serveur

#### Backend - ViewSet paginé
```python
# bi_app/backend/analytics/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'results': data
        })

# bi_app/backend/analytics/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

class OccupationZoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MartOccupationZones.objects.all()
    serializer_class = OccupationZoneSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtres disponibles
    filterset_fields = ['statut', 'taux_occupation_pct']
    
    # Champs recherchables
    search_fields = ['nom_zone', 'code_zone']
    
    # Champs triables
    ordering_fields = ['nom_zone', 'taux_occupation_pct', 'superficie_totale']
    ordering = ['nom_zone']  # Tri par défaut
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres personnalisés
        min_occupation = self.request.query_params.get('min_occupation')
        max_occupation = self.request.query_params.get('max_occupation')
        
        if min_occupation:
            queryset = queryset.filter(taux_occupation_pct__gte=min_occupation)
        if max_occupation:
            queryset = queryset.filter(taux_occupation_pct__lte=max_occupation)
        
        return queryset

# URLs
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'zones', OccupationZoneViewSet, basename='zones')
urlpatterns = router.urls
```

#### Frontend - Hook personnalisé pour pagination
```jsx
// bi_app/frontend/src/hooks/usePaginatedQuery.js
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

export function usePaginatedQuery(
  queryKey,
  fetchFn,
  { pageSize = 10, initialFilters = {}, enabled = true } = {}
) {
  const [currentPage, setCurrentPage] = useState(1)
  const [filters, setFilters] = useState(initialFilters)
  const [sortField, setSortField] = useState(null)
  const [sortDirection, setSortDirection] = useState('asc')

  const queryParams = {
    page: currentPage,
    page_size: pageSize,
    ...filters,
    ...(sortField && { ordering: sortDirection === 'desc' ? `-${sortField}` : sortField })
  }

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: [...queryKey, queryParams],
    queryFn: () => fetchFn(queryParams),
    enabled,
    keepPreviousData: true, // Garde les données précédentes pendant le chargement
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
    setCurrentPage(1)
  }

  const handleFilter = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
    setCurrentPage(1)
  }

  const resetFilters = () => {
    setFilters(initialFilters)
    setCurrentPage(1)
  }

  return {
    data: data?.results || [],
    pagination: {
      count: data?.count || 0,
      totalPages: data?.total_pages || 1,
      currentPage: data?.current_page || currentPage,
      pageSize: data?.page_size || pageSize,
      hasNext: !!data?.next,
      hasPrevious: !!data?.previous,
    },
    isLoading,
    error,
    refetch,
    // Actions
    setCurrentPage,
    handleSort,
    handleFilter,
    resetFilters,
    // États
    filters,
    sortField,
    sortDirection,
  }
}
```

#### Utilisation dans un composant
```jsx
// bi_app/frontend/src/pages/Occupation.jsx
import { usePaginatedQuery } from '../hooks/usePaginatedQuery'
import { occupationAPI } from '../services/api'

export default function Occupation() {
  const {
    data: zones,
    pagination,
    isLoading,
    setCurrentPage,
    handleSort,
    handleFilter,
    resetFilters,
    filters,
    sortField,
    sortDirection
  } = usePaginatedQuery(
    ['occupation-zones'],
    occupationAPI.getZonesPaginated,
    { pageSize: 10 }
  )

  return (
    <div>
      {/* Filtres */}
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Rechercher..."
          onChange={(e) => handleFilter({ search: e.target.value })}
          className="px-3 py-2 border rounded"
        />
        <select
          onChange={(e) => handleFilter({ min_occupation: e.target.value })}
          className="px-3 py-2 border rounded"
        >
          <option value="">Taux minimum</option>
          <option value="50">≥ 50%</option>
          <option value="70">≥ 70%</option>
          <option value="90">≥ 90%</option>
        </select>
        <button onClick={resetFilters} className="px-4 py-2 bg-gray-200 rounded">
          Réinitialiser
        </button>
      </div>

      {/* Tableau */}
      <table>
        <thead>
          <tr>
            <th onClick={() => handleSort('nom_zone')} className="cursor-pointer">
              Zone {sortField === 'nom_zone' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
            <th onClick={() => handleSort('taux_occupation_pct')} className="cursor-pointer">
              Taux {sortField === 'taux_occupation_pct' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
          </tr>
        </thead>
        <tbody>
          {zones.map(zone => (
            <tr key={zone.id}>
              <td>{zone.nom_zone}</td>
              <td>{zone.taux_occupation_pct}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <span>
          Affichage {(pagination.currentPage - 1) * pagination.pageSize + 1} - 
          {Math.min(pagination.currentPage * pagination.pageSize, pagination.count)} sur {pagination.count}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={!pagination.hasPrevious}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Précédent
          </button>
          <span className="px-3 py-1">
            Page {pagination.currentPage} / {pagination.totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(prev => prev + 1)}
            disabled={!pagination.hasNext}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            Suivant
          </button>
        </div>
      </div>

      {isLoading && <div>Chargement...</div>}
    </div>
  )
}
```

### 1.3 Index Database

```sql
-- scripts/create_performance_indexes.sql

-- Index pour les zones industrielles
CREATE INDEX IF NOT EXISTS idx_zones_taux_occupation 
ON dwh_marts_occupation.mart_occupation_zones(taux_occupation_pct DESC);

CREATE INDEX IF NOT EXISTS idx_zones_nom 
ON dwh_marts_occupation.mart_occupation_zones(nom_zone);

CREATE INDEX IF NOT EXISTS idx_zones_superficie 
ON dwh_marts_occupation.mart_occupation_zones(superficie_totale DESC);

CREATE INDEX IF NOT EXISTS idx_zones_lots_disponibles 
ON dwh_marts_occupation.mart_occupation_zones(lots_disponibles DESC);

-- Index composite pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_zones_taux_lots 
ON dwh_marts_occupation.mart_occupation_zones(taux_occupation_pct DESC, lots_disponibles DESC);

-- Index pour les clients
CREATE INDEX IF NOT EXISTS idx_clients_raison_sociale 
ON dwh_marts_clients.mart_portefeuille_clients(raison_sociale);

CREATE INDEX IF NOT EXISTS idx_clients_segment 
ON dwh_marts_clients.mart_portefeuille_clients(segment_client);

CREATE INDEX IF NOT EXISTS idx_clients_taux_paiement 
ON dwh_marts_clients.mart_portefeuille_clients(taux_paiement_pct DESC);

CREATE INDEX IF NOT EXISTS idx_clients_factures_retard 
ON dwh_marts_clients.mart_portefeuille_clients(nombre_factures_en_retard DESC);

-- Index GIN pour recherche full-text (optionnel)
CREATE INDEX IF NOT EXISTS idx_zones_nom_fulltext 
ON dwh_marts_occupation.mart_occupation_zones 
USING GIN(to_tsvector('french', nom_zone));

CREATE INDEX IF NOT EXISTS idx_clients_raison_sociale_fulltext 
ON dwh_marts_clients.mart_portefeuille_clients 
USING GIN(to_tsvector('french', raison_sociale));

-- Analyser les tables pour optimiser les plans de requête
ANALYZE dwh_marts_occupation.mart_occupation_zones;
ANALYZE dwh_marts_clients.mart_portefeuille_clients;

-- Vérifier les index existants
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname IN ('dwh_marts_occupation', 'dwh_marts_clients')
ORDER BY tablename, indexname;
```

### 1.4 Lazy Loading avec Intersection Observer

```jsx
// bi_app/frontend/src/hooks/useIntersectionObserver.js
import { useEffect, useRef, useState } from 'react'

export function useIntersectionObserver(options = {}) {
  const ref = useRef(null)
  const [isIntersecting, setIsIntersecting] = useState(false)
  const [hasIntersected, setHasIntersected] = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting)
        if (entry.isIntersecting && !hasIntersected) {
          setHasIntersected(true)
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options
      }
    )

    observer.observe(element)

    return () => {
      if (element) {
        observer.unobserve(element)
      }
    }
  }, [hasIntersected, options])

  return { ref, isIntersecting, hasIntersected }
}

// Composant LazySection
export function LazySection({ children, fallback = null, once = true }) {
  const { ref, hasIntersected, isIntersecting } = useIntersectionObserver()

  const shouldRender = once ? hasIntersected : isIntersecting

  return (
    <div ref={ref}>
      {shouldRender ? children : (fallback || <div className="h-64 bg-gray-100 animate-pulse" />)}
    </div>
  )
}
```

```jsx
// Utilisation dans Occupation.jsx
import { LazySection } from '../hooks/useIntersectionObserver'

export default function Occupation() {
  return (
    <div className="space-y-8">
      {/* KPIs - Chargés immédiatement */}
      <section>
        <KPICards />
      </section>

      {/* Graphiques - Chargés au scroll */}
      <LazySection>
        <section>
          <h3>Alertes d'Occupation</h3>
          <GaugeChart />
        </section>
      </LazySection>

      <LazySection>
        <section>
          <h3>Zones les Moins Occupées</h3>
          <HistogramChart />
        </section>
      </LazySection>

      {/* Tableau - Chargé au scroll */}
      <LazySection>
        <section>
          <ZonesTable />
        </section>
      </LazySection>
    </div>
  )
}
```

### 1.5 React.memo et optimisations

```jsx
// bi_app/frontend/src/components/StatsCard.jsx
import { memo } from 'react'

const StatsCard = memo(function StatsCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  color = 'blue',
  loading = false 
}) {
  // Le composant ne se re-render que si les props changent
  if (loading) {
    return <StatsCardSkeleton />
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        </div>
        <div className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  )
})

export default StatsCard
```

```jsx
// Utilisation de useMemo et useCallback
import { useMemo, useCallback } from 'react'

export default function Occupation() {
  // Mémoriser les calculs lourds
  const topZonesData = useMemo(() => {
    if (!topZones) return null
    return topZones.plus_occupees?.slice(0, 5).map(zone => ({
      ...zone,
      percentage: parseFloat(zone.taux_occupation_pct) || 0
    }))
  }, [topZones])

  // Mémoriser les callbacks pour éviter re-renders enfants
  const handleSort = useCallback((field) => {
    setSortField(prev => prev === field ? field : field)
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
  }, [])

  const handlePageChange = useCallback((newPage) => {
    setCurrentPage(newPage)
  }, [])

  return (
    <ZonesTable 
      data={zonesData}
      onSort={handleSort}
      onPageChange={handlePageChange}
    />
  )
}
```

### 1.6 Code Splitting

```jsx
// bi_app/frontend/src/App.jsx
import { lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import LoadingSpinner from './components/LoadingSpinner'

// Chargement immédiat (pages fréquemment visitées)
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

// Chargement lazy (pages moins fréquentes)
const Occupation = lazy(() => import('./pages/Occupation'))
const OccupationZoneDetails = lazy(() => import('./pages/OccupationZoneDetails'))
const Clients = lazy(() => import('./pages/Clients'))
const ClientDetails = lazy(() => import('./pages/ClientDetails'))
const Financier = lazy(() => import('./pages/Financier'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner fullScreen />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="occupation" element={<Occupation />} />
            <Route path="occupation/zone/:zoneName" element={<OccupationZoneDetails />} />
            <Route path="clients" element={<Clients />} />
            <Route path="clients/:clientId" element={<ClientDetails />} />
            <Route path="financier" element={<Financier />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </Suspense>
    </Router>
  )
}

export default App
```

```jsx
// Composant LoadingSpinner
export default function LoadingSpinner({ fullScreen = false }) {
  if (fullScreen) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  )
}
```

---

**Suite dans le prochain fichier: AMELIORATIONS_VISUALISATIONS.md**
