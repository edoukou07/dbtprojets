# 🏗️ Diagrammes d'Architecture Détaillés - SIGETI BI

## 1. Architecture Globale (Vue d'Ensemble)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          SIGETI BI ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────────┘

LAYER 1: PRESENTATION (Frontend)
┌──────────────────────────────────────────────────────────────────────────┐
│                          React + Vite (Port 5173)                        │
├──────────────────────────────────────────────────────────────────────────┤
│  Pages:                    Components:         Services:                 │
│  ├─ Login                  ├─ Layout           ├─ api.js                │
│  ├─ Dashboard             ├─ KPICard          ├─ auth.js               │
│  ├─ Financier             ├─ DataTable        ├─ caching.js            │
│  ├─ Occupation            ├─ ZonesMap         └─ hooks/                │
│  ├─ Clients               ├─ Charts                                     │
│  ├─ Operationnel          ├─ ErrorBoundary    Middleware:             │
│  ├─ Alertes               └─ ProtectedRoute   ├─ JWT handler           │
│  ├─ ChatBot                                   ├─ CORS handler          │
│  └─ Reports                                   └─ Error handler         │
│                                                                         │
│  State Management: React Query + localStorage                          │
│  HTTP Client: Axios interceptor                                        │
│  Styling: Tailwind CSS + Lucide Icons                                 │
└──────────────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │ REST API
                                     │ JSON
                                     ▼
LAYER 2: APPLICATION (Backend)
┌──────────────────────────────────────────────────────────────────────────┐
│                    Django REST API (Port 8000)                           │
├──────────────────────────────────────────────────────────────────────────┤
│  Core APIs:                Security:           AI Module:               │
│  ├─ /api/financier/*      ├─ JWT Auth         ├─ query_engine.py      │
│  ├─ /api/occupation/*     ├─ Session Auth     ├─ text_normalizer.py   │
│  ├─ /api/clients/*        ├─ CORS             ├─ chat_service.py      │
│  ├─ /api/operationnel/*   ├─ Permissions      └─ trend_analysis.py    │
│  ├─ /api/alerts/*         └─ Rate Limit                                │
│  ├─ /api/ai/chat/*                           Cache Layer:             │
│  └─ /api/auth/*                              ├─ Redis (prod)          │
│                                              ├─ Memory cache (dev)    │
│  Middleware:                                 └─ TTL: 5-30 min        │
│  ├─ Authentication                                                    │
│  ├─ CORS                                     Logging:                 │
│  ├─ Request logging                         ├─ API requests          │
│  ├─ Error handling                          ├─ Database queries      │
│  └─ Rate limiting                           ├─ User actions          │
│                                             └─ Errors/Warnings      │
└──────────────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │ SQL Query
                                     │ Read/Write
                                     ▼
LAYER 3: DATA (Database)
┌──────────────────────────────────────────────────────────────────────────┐
│              PostgreSQL 14+ (SIGETI_NODE_DB)                             │
├──────────────────────────────────────────────────────────────────────────┤
│  Schema: public                Schema: dwh_marts_*                       │
│  ├─ analytics_alert          ├─ dwh_marts_financier/                   │
│  ├─ analytics_alertthreshold │   └─ mart_performance_financiere        │
│  ├─ analytics_user           ├─ dwh_marts_occupation/                  │
│  └─ auth_user                │   └─ mart_occupation_zones              │
│                              ├─ dwh_marts_clients/                     │
│  Schema: source              │   └─ mart_portefeuille_clients          │
│  ├─ entreprises              └─ dwh_marts_operationnel/                │
│  ├─ factures                     └─ mart_kpi_operationnels            │
│  ├─ paiements                                                          │
│  └─ zones                    Indexes on:                               │
│                              ├─ Performance (KPIs)                     │
│  Schema: dwh_staging         ├─ Occupation (zones)                     │
│  ├─ stg_entreprises          ├─ Clients (segments)                     │
│  ├─ stg_factures             └─ Operationnel (dates)                   │
│  ├─ stg_paiements                                                      │
│  └─ stg_zones                Snapshots:                                │
│                              └─ snapshot_entreprises (hist)            │
│                                                                         │
│  Constraints:                                                           │
│  ├─ PK on all core tables                                              │
│  ├─ FK for relationships                                               │
│  ├─ Unique on natural keys                                             │
│  └─ Checks on data validity                                            │
└──────────────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │ dbt run
                                     │ SQL Execute
                                     ▼
LAYER 4: ETL ORCHESTRATION (dbt & Prefect)
┌──────────────────────────────────────────────────────────────────────────┐
│                  dbt + Prefect Pipeline (Scheduler)                      │
├──────────────────────────────────────────────────────────────────────────┤
│  dbt Execution Flow:                                                     │
│  1. Source read (source.yml)                                             │
│  2. Staging layer (stg_*.sql)                                            │
│  3. Dimensions (dim_*.sql)                                               │
│  4. Facts (fact_*.sql)                                                   │
│  5. Marts materialization (mart_*.sql)                                   │
│  6. Tests execution (tests_quality.yml)                                  │
│  7. Documentation generation                                             │
│                                                                          │
│  Prefect Flow (Every 10 min):                                            │
│  ├─ Task 1: Verify DB connection                                         │
│  ├─ Task 2: dbt debug                                                    │
│  ├─ Task 3: dbt run (staging)                                            │
│  ├─ Task 4: dbt run (dimensions)                                         │
│  ├─ Task 5: dbt run (facts)                                              │
│  ├─ Task 6: dbt run (marts)                                              │
│  └─ Task 7: dbt test (quality)                                           │
│                                                                          │
│  Retry Logic: Max 1 retry with backoff                                   │
│  Timeout: 120 seconds per task                                           │
│  Logging: Full stdout + stderr capture                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Frontend Architecture (React Components)

```
App.jsx (Root)
│
├─ Router Setup
│  └─ Routes
│     ├─ PublicRoute: /login → Login.jsx
│     └─ ProtectedRoutes:
│        ├─ /dashboard → Dashboard.jsx
│        ├─ /financier → Financier.jsx
│        ├─ /occupation → Occupation.jsx
│        │              → OccupationZoneDetails.jsx (nested)
│        ├─ /clients → Clients.jsx
│        │          → ClientDetails.jsx (nested)
│        ├─ /operationnel → Operationnel.jsx
│        ├─ /alerts → AlertsAnalytics.jsx
│        ├─ /chatbot → ChatBot.jsx
│        └─ /reports → ReportConfig.jsx
│
Layout.jsx (Wrapper)
├─ Navigation Bar
│  ├─ Logo + Home link
│  ├─ Menu (Financier, Occupation, Clients, Operationnel, Alertes)
│  ├─ User Profile dropdown
│  └─ Logout button
│
└─ Main Content
   │
   Pages (Each page structure):
   │
   ├─ DASHBOARD PAGE
   │  ├─ useQuery: /api/financier/summary/
   │  ├─ useQuery: /api/occupation/summary/
   │  ├─ useQuery: /api/clients/summary/
   │  ├─ useQuery: /api/operationnel/summary/
   │  ├─ useQuery: /api/alerts/active/
   │  │
   │  └─ Render:
   │     ├─ <KPICard> for each summary
   │     ├─ <LineChart> for trends
   │     └─ <AlertsPreview> for active alerts
   │
   ├─ FINANCIER PAGE
   │  ├─ useQuery: /api/financier/summary/
   │  ├─ useQuery: /api/financier/top_zones_performance/
   │  ├─ useQuery: /api/financier/tendances_mensuelles/
   │  ├─ useState: filters (date range, zone, sector)
   │  │
   │  └─ Render:
   │     ├─ <Filters>
   │     ├─ <KPICard> × 6 (CA, Impayés, etc.)
   │     ├─ <BarChart> CA vs Impayés
   │     ├─ <LineChart> Taux paiement evolution
   │     ├─ <BarChart> Top 10 clients
   │     ├─ <PieChart> Distribution secteurs
   │     ├─ <AreaChart> Tendances
   │     └─ <DataTable> Détail clients
   │
   ├─ OCCUPATION PAGE
   │  ├─ useQuery: /api/occupation/summary/
   │  ├─ useQuery: /api/occupation/zones_map/
   │  ├─ useState: selectedZone, filters
   │  │
   │  └─ Render:
   │     ├─ <ZonesMap>
   │     │  └─ Leaflet map with geojson
   │     │     ├─ Zone colors by occupation %
   │     │     ├─ Popup on zone click
   │     │     └─ Legend
   │     ├─ <KPICard> × 5 (Taux, Lots, Surface)
   │     ├─ <Gauge> Occupation globale
   │     ├─ <DataTable> Zones détails
   │     └─ Link to OccupationZoneDetails
   │
   ├─ OCCUPATION ZONE DETAILS PAGE
   │  ├─ useParams: zone_name
   │  ├─ useQuery: /api/occupation/{zone_id}/
   │  │
   │  └─ Render:
   │     ├─ <Breadcrumb>
   │     ├─ Zone name + map
   │     ├─ KPIs détail zone
   │     ├─ Lots breakdown table
   │     ├─ Viabilisation status
   │     └─ Zone history chart
   │
   ├─ CLIENTS PAGE
   │  ├─ useQuery: /api/clients/summary/
   │  ├─ useQuery: /api/clients/by_segment/
   │  ├─ useState: segment, filters
   │  │
   │  └─ Render:
   │     ├─ <KPICard> × 5 (Total, Actifs, Inactifs)
   │     ├─ <DonutChart> Segmentation A/B/C
   │     ├─ <BarChart> Clients par secteur
   │     ├─ <BarChart> Top 20 clients
   │     ├─ <Tabs>
   │     │  ├─ Tab: Clients actifs (table)
   │     │  ├─ Tab: Clients inactifs (table)
   │     │  ├─ Tab: Clients à risque (table)
   │     │  └─ Tab: Par zone (map + table)
   │     └─ Link to ClientDetails
   │
   ├─ CLIENT DETAILS PAGE
   │  ├─ useParams: client_id
   │  ├─ useQuery: /api/clients/{id}/details/
   │  │
   │  └─ Render:
   │     ├─ <Breadcrumb>
   │     ├─ Client info card
   │     ├─ KPIs client (CA, paiement, lots)
   │     ├─ Transactions history (table)
   │     ├─ Lots détails (table)
   │     └─ Contact info
   │
   ├─ OPERATIONNEL PAGE
   │  ├─ useQuery: /api/operationnel/summary/
   │  ├─ useQuery: /api/operationnel/kpi_details/
   │  │
   │  └─ Render:
   │     ├─ Grid KPIs clés × 8
   │     ├─ <LineChart> KPIs tendances mensuelles
   │     ├─ <BarChart> Performance zones
   │     ├─ <Radar> Comparatif zones
   │     └─ <DataTable> Détail KPIs
   │
   ├─ ALERTES PAGE
   │  ├─ useQuery: /api/alerts/
   │  ├─ useQuery: /api/alerts/by_type/
   │  ├─ useState: filters (severity, status)
   │  │
   │  └─ Render:
   │     ├─ <KPICard> × 4 (Actives, Critiques, etc.)
   │     ├─ <PieChart> Alertes par sévérité
   │     ├─ <Timeline> Alertes timeline
   │     ├─ <DataTable> Liste détaillée
   │     │  ├─ Severity badge (colors)
   │     │  ├─ Title + message
   │     │  ├─ Date
   │     │  ├─ Status
   │     │  └─ Actions (Ack/Resolve)
   │     └─ Filters (severity, type, status, zone)
   │
   ├─ CHATBOT PAGE
   │  ├─ useRef: messagesEnd (auto-scroll)
   │  ├─ useState: messages, input, loading
   │  ├─ useMutation: POST /api/ai/chat/
   │  │
   │  └─ Render:
   │     ├─ <ChatHistory>
   │     │  ├─ User messages (blue, right)
   │     │  ├─ Bot messages (gray, left)
   │     │  ├─ Formatted tables/charts
   │     │  └─ Auto-scroll to latest
   │     ├─ <SuggestedQuestions>
   │     ├─ <InputForm>
   │     │  ├─ Text input
   │     │  ├─ Send button
   │     │  └─ Attach data option
   │     └─ <LoadingIndicator> (while processing)
   │
   └─ REPORTS PAGE
      ├─ useQuery: /api/reports/templates/
      ├─ useState: selected filters
      │
      └─ Render:
         ├─ <ReportSelector> (Financier/Occupation/etc.)
         ├─ <DateRangePicker>
         ├─ <RecipientsList>
         ├─ <ScheduleConfig> (Immediate/Recurring)
         ├─ <PreviewButton>
         ├─ <SendButton>
         └─ <SentReportsHistory>

Common Components Used Across Pages:
├─ <KPICard value, label, trend />
├─ <DataTable data, columns, onRowClick />
├─ <LineChart data, categories, title />
├─ <BarChart data, categories, title />
├─ <PieChart data, title, onClick />
├─ <Gauge value, max, thresholds />
├─ <ZonesMap zones, onZoneClick />
├─ <LoadingSpinner />
├─ <ErrorMessage error />
├─ <SuccessAlert message />
├─ <Modal children, isOpen, onClose />
├─ <Tabs tabs, activeTab, onChange />
├─ <Filters filterConfig, onApply />
├─ <Pagination page, total, onChange />
├─ <StatusBadge status, type />
├─ <Breadcrumb path />
└─ <ProtectedRoute component, requiredRole />
```

---

## 3. Backend API Layer

```
Django Project Structure
│
├─ sigeti_bi/ (Config)
│  ├─ settings.py
│  │  ├─ INSTALLED_APPS
│  │  ├─ DATABASES
│  │  ├─ REST_FRAMEWORK config
│  │  ├─ CORS_ALLOWED_ORIGINS
│  │  └─ CACHES config
│  │
│  ├─ urls.py (Root routing)
│  │  ├─ path('admin/', admin.site.urls)
│  │  ├─ path('api/', include('api.urls'))
│  │  ├─ path('api/ai/', include('ai_chat.urls'))
│  │  └─ path('api/auth/', include('auth_views.urls'))
│  │
│  └─ wsgi.py (Production)
│
├─ analytics/ (Data Models)
│  ├─ models.py
│  │  ├─ class MartPerformanceFinanciere
│  │  ├─ class MartOccupationZones
│  │  ├─ class MartPortefeuilleClients
│  │  ├─ class MartKPIOperationnels
│  │  ├─ class Alert
│  │  └─ class AlertThreshold
│  │
│  └─ apps.py
│
├─ api/ (REST Endpoints)
│  ├─ views.py (ViewSets)
│  │  ├─ class MartPerformanceFinanciereViewSet
│  │  │  ├─ list() → GET /api/financier/
│  │  │  ├─ summary() → GET /api/financier/summary/
│  │  │  ├─ by_zone() → GET /api/financier/by_zone/{zone}
│  │  │  ├─ tendances_mensuelles() → GET /api/financier/tendances_mensuelles/
│  │  │  └─ ... (10+ actions)
│  │  │
│  │  ├─ class MartOccupationZonesViewSet
│  │  │  ├─ list() → GET /api/occupation/
│  │  │  ├─ summary() → GET /api/occupation/summary/
│  │  │  ├─ zones_map() → GET /api/occupation/zones_map/
│  │  │  └─ ... (8+ actions)
│  │  │
│  │  ├─ class MartPortefeuilleClientsViewSet
│  │  │  ├─ list() → GET /api/clients/
│  │  │  ├─ summary() → GET /api/clients/summary/
│  │  │  ├─ by_segment() → GET /api/clients/by_segment/
│  │  │  └─ ... (10+ actions)
│  │  │
│  │  ├─ class MartKPIOperationnelsViewSet
│  │  │  ├─ list() → GET /api/operationnel/
│  │  │  ├─ summary() → GET /api/operationnel/summary/
│  │  │  └─ ... (8+ actions)
│  │  │
│  │  ├─ class AlertViewSet
│  │  │  ├─ list() → GET /api/alerts/
│  │  │  ├─ create() → POST /api/alerts/
│  │  │  ├─ retrieve() → GET /api/alerts/{id}/
│  │  │  ├─ update() → PATCH /api/alerts/{id}/
│  │  │  ├─ active() → GET /api/alerts/active/
│  │  │  ├─ acknowledge() → POST /api/alerts/{id}/acknowledge/
│  │  │  └─ resolve() → POST /api/alerts/{id}/resolve/
│  │  │
│  │  └─ class AlertThresholdViewSet
│  │     ├─ list() → GET /api/alert-thresholds/
│  │     ├─ create() → POST /api/alert-thresholds/
│  │     └─ update() → PATCH /api/alert-thresholds/{id}/
│  │
│  ├─ serializers.py (JSON Mapping)
│  │  ├─ class MartPerformanceFinanciereSerializer
│  │  ├─ class MartOccupationZonesSerializer
│  │  ├─ class MartPortefeuilleClientsSerializer
│  │  ├─ class MartKPIOperationnelsSerializer
│  │  ├─ class AlertSerializer
│  │  └─ class AlertThresholdSerializer
│  │
│  ├─ urls.py (Routing)
│  │  ├─ router.register('financier', MartPerformanceFinanciereViewSet)
│  │  ├─ router.register('occupation', MartOccupationZonesViewSet)
│  │  ├─ router.register('clients', MartPortefeuilleClientsViewSet)
│  │  ├─ router.register('operationnel', MartKPIOperationnelsViewSet)
│  │  ├─ router.register('alerts', AlertViewSet)
│  │  ├─ router.register('alert-thresholds', AlertThresholdViewSet)
│  │  └─ path('', include(router.urls))
│  │
│  ├─ cache_decorators.py
│  │  └─ @cache_response(timeout=300) decorator
│  │
│  ├─ filters.py
│  │  ├─ Custom FilterBackend classes
│  │  └─ Dynamic filter fields
│  │
│  ├─ auth_views.py
│  │  ├─ @action POST /login/
│  │  ├─ @action POST /logout/
│  │  └─ @action POST /refresh/
│  │
│  └─ permissions.py
│     ├─ class IsAuthenticatedReadOnly
│     ├─ class IsAdmin
│     └─ class HasAlertPermission
│
├─ ai_chat/ (Chatbot AI)
│  ├─ views.py
│  │  ├─ @api_view POST /api/ai/chat/
│  │  └─ Calls ChatService.process_chat_message()
│  │
│  ├─ chat_service.py
│  │  ├─ class ChatService
│  │  │  ├─ process_chat_message(question)
│  │  │  │  ├─ Normalize question
│  │  │  │  ├─ Get query engine
│  │  │  │  ├─ Generate SQL
│  │  │  │  ├─ Execute query
│  │  │  │  └─ Format response
│  │  │  └─ get_query_history()
│  │  │
│  │  └─ Class methods for chat flow
│  │
│  ├─ query_engine.py (Core Logic)
│  │  ├─ class TextNormalizer
│  │  │  ├─ normalize(question)
│  │  │  │  ├─ Apply synonyms
│  │  │  │  ├─ Handle negations
│  │  │  │  └─ Standardize accents
│  │  │  └─ ~50 synonym pairs
│  │  │
│  │  ├─ class QueryPattern
│  │  │  ├─ patterns: List[str]
│  │  │  ├─ sql_template: str
│  │  │  ├─ matches(question) → bool
│  │  │  └─ extract_params(question) → dict
│  │  │
│  │  ├─ class RuleBasedQueryEngine
│  │  │  ├─ __init__() - 30+ patterns
│  │  │  ├─ generate_sql(question)
│  │  │  │  ├─ Normalize question
│  │  │  │  ├─ Match pattern
│  │  │  │  ├─ Extract params
│  │  │  │  ├─ Format SQL
│  │  │  │  └─ Return (sql, description, category, is_rule)
│  │  │  └─ execute_sql(sql)
│  │  │
│  │  └─ Optional: class GPTQueryEngine (fallback)
│  │
│  ├─ text_normalizer.py
│  │  └─ Synonym mappings + utilities
│  │
│  └─ urls.py
│     ├─ path('chat/', chat_message_view)
│     ├─ path('history/', chat_history_view)
│     └─ path('query/', sql_query_view)
│
├─ manage.py (CLI)
│
└─ Tests
   ├─ test_api_financier.py
   ├─ test_api_occupation.py
   ├─ test_api_clients.py
   ├─ test_alerts.py
   ├─ test_chatbot.py
   └─ test_auth.py
```

---

## 4. Database Schema Architecture

```
PostgreSQL Database: sigeti_node_db
│
├─ Schema: public
│  ├─ TABLE: analytics_alert
│  │  ├─ id (PK)
│  │  ├─ alert_type (VARCHAR 50)
│  │  ├─ severity (VARCHAR 20)
│  │  ├─ status (VARCHAR 20)
│  │  ├─ title (VARCHAR 255)
│  │  ├─ message (TEXT)
│  │  ├─ context_data (JSONB)
│  │  ├─ threshold_value (DECIMAL)
│  │  ├─ actual_value (DECIMAL)
│  │  ├─ created_at (TIMESTAMP)
│  │  ├─ updated_at (TIMESTAMP)
│  │  ├─ acknowledged_at (TIMESTAMP, nullable)
│  │  └─ resolved_at (TIMESTAMP, nullable)
│  │
│  ├─ TABLE: analytics_alertthreshold
│  │  ├─ id (PK)
│  │  ├─ alert_type (VARCHAR 50)
│  │  ├─ threshold_operator (VARCHAR 2, <|>|=|!=)
│  │  ├─ threshold_value (DECIMAL)
│  │  ├─ severity_when_triggered (VARCHAR 20)
│  │  ├─ is_active (BOOLEAN)
│  │  ├─ created_at (TIMESTAMP)
│  │  └─ updated_at (TIMESTAMP)
│  │
│  ├─ TABLE: auth_user
│  │  ├─ id (PK)
│  │  ├─ username (VARCHAR 150, UNIQUE)
│  │  ├─ email (VARCHAR 254)
│  │  ├─ password (VARCHAR 128)
│  │  ├─ first_name (VARCHAR 150)
│  │  ├─ last_name (VARCHAR 150)
│  │  ├─ is_active (BOOLEAN)
│  │  ├─ is_staff (BOOLEAN)
│  │  ├─ is_superuser (BOOLEAN)
│  │  ├─ last_login (TIMESTAMP)
│  │  └─ date_joined (TIMESTAMP)
│  │
│  └─ TABLE: authtoken_token
│     ├─ key (PK, VARCHAR 40)
│     ├─ user_id (FK → auth_user)
│     └─ created (TIMESTAMP)
│
├─ Schema: source (External/View)
│  ├─ TABLE: entreprises
│  │  ├─ id_entreprise
│  │  ├─ raison_sociale
│  │  ├─ secteur_activite
│  │  ├─ zone_location
│  │  └─ ... (status, email, phone, etc.)
│  │
│  ├─ TABLE: factures
│  │  ├─ id_facture
│  │  ├─ id_entreprise (FK)
│  │  ├─ montant_facture
│  │  ├─ date_emission
│  │  ├─ date_echeance
│  │  └─ statut_paiement
│  │
│  ├─ TABLE: paiements
│  │  ├─ id_paiement
│  │  ├─ id_facture (FK)
│  │  ├─ montant_paye
│  │  ├─ date_paiement
│  │  └─ mode_paiement
│  │
│  └─ TABLE: zones
│     ├─ id_zone
│     ├─ nom_zone
│     ├─ superficie_hectares
│     ├─ nb_lots
│     ├─ coordonnees (GEOMETRY)
│     └─ status_viabilisation
│
├─ Schema: dwh_staging (Intermediate)
│  ├─ VIEW: stg_entreprises
│  ├─ VIEW: stg_factures
│  ├─ VIEW: stg_paiements
│  └─ VIEW: stg_zones
│
├─ Schema: dwh_dimensions (Reference)
│  ├─ TABLE: dim_entreprises
│  │  ├─ id_entreprise (PK)
│  │  ├─ raison_sociale
│  │  ├─ secteur_activite
│  │  ├─ segment (A/B/C)
│  │  ├─ date_premiere_facture
│  │  ├─ is_active
│  │  ├─ dbt_scd_id
│  │  └─ dbt_updated_at
│  │
│  ├─ TABLE: dim_zones
│  │  ├─ id_zone (PK)
│  │  ├─ nom_zone
│  │  ├─ superficie_hectares
│  │  ├─ region
│  │  ├─ coordonnees (GEOMETRY)
│  │  └─ dbt_updated_at
│  │
│  └─ TABLE: dim_dates
│     ├─ date_key (PK)
│     ├─ date (DATE)
│     ├─ year, month, quarter, week, day_of_week
│     ├─ is_weekend, is_holiday
│     └─ date_label
│
├─ Schema: dwh_facts (Granular)
│  ├─ TABLE: fact_factures
│  │  ├─ id_facture (PK)
│  │  ├─ id_entreprise (FK → dim_entreprises)
│  │  ├─ date_facture (FK → dim_dates)
│  │  ├─ montant_facture (DECIMAL)
│  │  ├─ statut_paiement (VARCHAR)
│  │  └─ dbt_updated_at
│  │
│  ├─ TABLE: fact_paiements
│  │  ├─ id_paiement (PK)
│  │  ├─ id_facture (FK)
│  │  ├─ date_paiement (FK → dim_dates)
│  │  ├─ montant_paye (DECIMAL)
│  │  ├─ delai_paiement_jours (INTEGER)
│  │  └─ dbt_updated_at
│  │
│  └─ TABLE: fact_occupation
│     ├─ id_zone (FK → dim_zones)
│     ├─ date_key (FK → dim_dates)
│     ├─ lots_attribues (INTEGER)
│     ├─ lots_disponibles (INTEGER)
│     ├─ taux_occupation (DECIMAL)
│     └─ dbt_updated_at
│
├─ Schema: dwh_marts_financier (Analytics)
│  └─ VIEW: mart_performance_financiere
│     ├─ zone (VARCHAR)
│     ├─ ca_total (DECIMAL)
│     ├─ ca_moyen_par_client (DECIMAL)
│     ├─ montant_impaye (DECIMAL)
│     ├─ taux_impaye_pct (DECIMAL)
│     ├─ taux_paiement_pct (DECIMAL)
│     ├─ delai_moyen_paiement (INTEGER)
│     ├─ taux_recouvrement_moyen (DECIMAL)
│     ├─ creances_clients_montant (DECIMAL)
│     ├─ factures_payees (INTEGER)
│     ├─ factures_impayees (INTEGER)
│     └─ date_MAJ (TIMESTAMP)
│
├─ Schema: dwh_marts_occupation
│  └─ VIEW: mart_occupation_zones
│     ├─ zone_id
│     ├─ zone_name (VARCHAR)
│     ├─ region (VARCHAR)
│     ├─ total_lots (INTEGER)
│     ├─ lots_disponibles (INTEGER)
│     ├─ lots_attribues (INTEGER)
│     ├─ taux_occupation (DECIMAL)
│     ├─ surface_total_hectares (DECIMAL)
│     ├─ surface_attribuee_hectares (DECIMAL)
│     ├─ viabilisation_status (VARCHAR)
│     ├─ secteurs_presents (TEXT)
│     └─ date_MAJ (TIMESTAMP)
│
├─ Schema: dwh_marts_clients
│  └─ VIEW: mart_portefeuille_clients
│     ├─ id_entreprise
│     ├─ raison_sociale (VARCHAR)
│     ├─ secteur_activite (VARCHAR)
│     ├─ zone_location (VARCHAR)
│     ├─ chiffre_affaires_total (DECIMAL)
│     ├─ nombre_lots_attribues (INTEGER)
│     ├─ taux_paiement_pct (DECIMAL)
│     ├─ delai_moyen_paiement (INTEGER)
│     ├─ segment_client (VARCHAR: A/B/C)
│     ├─ statut_activite (VARCHAR: Actif/Inactif)
│     ├─ date_derniere_facture (DATE)
│     ├─ montant_impaye (DECIMAL)
│     └─ risk_score (DECIMAL: 0-100)
│
└─ Schema: dwh_marts_operationnel
   └─ VIEW: mart_kpi_operationnels
      ├─ zone (VARCHAR)
      ├─ date (DATE)
      ├─ kpi_name (VARCHAR)
      ├─ valeur_actuelle (DECIMAL)
      ├─ valeur_periode_precedente (DECIMAL)
      ├─ variance_pct (DECIMAL)
      ├─ tendance (VARCHAR: ↑/↓/=)
      └─ date_MAJ (TIMESTAMP)

INDEXES:
├─ alerts_status_severity (status, severity)
├─ alerts_created_at (created_at DESC)
├─ mart_performance_zone (zone)
├─ mart_occupation_zone_name (zone_name)
├─ mart_clients_segment (segment_client)
├─ mart_clients_zone (zone_location)
└─ dim_zones_geometry (coordonnees)
```

---

## 5. Data Flow Diagram

```
INGESTION LAYER
───────────────────────────────────────────────────────────────
External Sources (SIGETI Node DB)
    ├─ Entreprises CSV/DB
    ├─ Factures DB
    ├─ Paiements DB
    └─ Zones GeoJSON/DB

                    ▼ dbt seed / source yaml

TRANSFORMATION LAYER (dbt)
───────────────────────────────────────────────────────────────
Staging Layer (Vues)
    ├─ stg_entreprises
    ├─ stg_factures
    ├─ stg_paiements
    └─ stg_zones
    
                    ▼ dbt run staging

Dimension Layer (Tables Dénormalisées)
    ├─ dim_entreprises (SCD Type 2 via snapshot)
    ├─ dim_zones
    ├─ dim_dates
    └─ dim_client_segment
    
                    ▼ dbt run dimensions

Facts Layer (Tables de Faits Normalisées)
    ├─ fact_factures (à grain facture)
    ├─ fact_paiements (à grain paiement)
    └─ fact_occupation (à grain zone-date)
    
                    ▼ dbt run facts

Marts Layer (Vues Matérialisées pour Analytics)
    ├─ mart_performance_financiere
    ├─ mart_occupation_zones
    ├─ mart_portefeuille_clients
    └─ mart_kpi_operationnels
    
                    ▼ dbt test + generate docs

QUALITY CHECKS
───────────────────────────────────────────────────────────────
    ├─ NOT NULL tests
    ├─ Unique constraints
    ├─ Foreign key relationships
    ├─ Data freshness (dbt_updated_at)
    ├─ Custom data quality tests
    └─ Documentation generation (dbt docs)

CONSUMPTION LAYER (Backend API)
───────────────────────────────────────────────────────────────
Backend Services Query Marts
    ├─ MartPerformanceFinanciereViewSet
    │  ├─ Reads from mart_performance_financiere
    │  ├─ Applies filters (date range, zone, sector)
    │  ├─ Aggregates (SUM, AVG, COUNT)
    │  ├─ Caches (5-30 min depending on endpoint)
    │  └─ Returns JSON via REST API
    │
    ├─ MartOccupationZonesViewSet
    │  └─ Similar flow...
    │
    ├─ MartPortefeuilleClientsViewSet
    │  └─ Similar flow...
    │
    ├─ MartKPIOperationnelsViewSet
    │  └─ Similar flow...
    │
    ├─ AlertViewSet
    │  ├─ Reads from analytics_alert table
    │  ├─ Filters by status, severity
    │  └─ Returns alert list/details
    │
    └─ ChatBot Query Engine
       ├─ Normalizes question
       ├─ Matches patterns
       ├─ Generates SQL
       ├─ Queries marts
       └─ Formats response

PRESENTATION LAYER (Frontend)
───────────────────────────────────────────────────────────────
React Components Fetch APIs
    ├─ Dashboard.jsx
    │  ├─ useQuery: /api/financier/summary/
    │  ├─ useQuery: /api/occupation/summary/
    │  ├─ useQuery: /api/clients/summary/
    │  ├─ useQuery: /api/operationnel/summary/
    │  └─ useQuery: /api/alerts/active/
    │
    ├─ Financier.jsx
    │  ├─ useQuery: /api/financier/*
    │  ├─ useMutation: filter changes
    │  └─ Recharts graphs + DataTable
    │
    ├─ Occupation.jsx
    │  ├─ useQuery: /api/occupation/zones_map/
    │  ├─ Leaflet ZonesMap component
    │  └─ Occupation metrics
    │
    ├─ Clients.jsx
    │  ├─ useQuery: /api/clients/*
    │  ├─ Segmentation visualizations
    │  └─ Client tables
    │
    └─ User Views Dashboards
       └─ Interactive exploration

MONITORING & AUTOMATION
───────────────────────────────────────────────────────────────
Alert System:
    ├─ Scheduler checks every 10 min
    ├─ Compares actual vs AlertThreshold
    ├─ Creates Alert records
    ├─ Frontend fetches /api/alerts/
    └─ User sees notifications

Prefect Orchestration:
    ├─ Runs dbt pipeline every 10 min
    ├─ Monitors execution
    ├─ Logs all steps
    ├─ Retries on failure
    └─ Alerts on critical errors
```

---

**Document généré**: Novembre 2025
**Versions**: PostgreSQL 14+, Django 5.0, React 18.2, dbt 1.5+

