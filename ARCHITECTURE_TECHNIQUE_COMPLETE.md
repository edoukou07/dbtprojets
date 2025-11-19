# 📐 Architecture Technique Complète - SIGETI BI

## Table des matières
1. [Architecture Globale](#architecture-globale)
2. [Partie Data (dbt & DWH)](#partie-data)
3. [Partie Backend (Django REST API)](#partie-backend)
4. [Partie Frontend (React & Vite)](#partie-frontend)
5. [Flux de Données](#flux-de-données)
6. [Technologies Utilisées](#technologies-utilisées)

---

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                     SIGETI BI Application                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│   Frontend (React)   │────▶│ Backend (Django API) │
│  - Dashboard         │     │ - REST Endpoints     │
│  - Visualisations    │     │ - Alertes            │
│  - Authentification  │     │ - Chatbot IA         │
└──────────────────────┘     └──────────────────────┘
                                      │
                                      ▼
                             ┌──────────────────────┐
                             │  PostgreSQL DWH      │
                             │ - Staging            │
                             │ - Dimensions         │
                             │ - Facts              │
                             │ - Marts              │
                             └──────────────────────┘
                                      ▲
                                      │
                        ┌─────────────────────────┐
                        │  dbt (Data Pipeline)    │
                        │ - Transformations       │
                        │ - Tests de qualité      │
                        │ - Documentation         │
                        └─────────────────────────┘
                                      ▲
                                      │
                        ┌─────────────────────────┐
                        │  Prefect (Orchestration)│
                        │ - Scheduling            │
                        │ - Monitoring            │
                        └─────────────────────────┘
```

---

# PARTIE DATA - dbt & Data Warehouse

## 🏗️ Architecture Data

### 1. Composants Principaux

```
models/
├── sources.yml                      # Définition des sources (SIGETI Node)
├── staging/                         # ✅ Couche Staging (Vues)
│   ├── stg_entreprises.sql         # Entreprises
│   ├── stg_factures.sql            # Factures
│   ├── stg_paiements.sql           # Paiements
│   └── stg_zones.sql               # Zones
│
├── dimensions/                      # ✅ Tables de Dimensions
│   ├── dim_entreprises.sql         # Dimension Entreprises
│   ├── dim_zones.sql               # Dimension Zones
│   ├── dim_dates.sql               # Dimension Dates
│   └── dim_client_segment.sql      # Segmentation Clients
│
├── facts/                           # ✅ Tables de Faits
│   ├── fact_factures.sql           # Faits Factures
│   ├── fact_paiements.sql          # Faits Paiements
│   └── fact_occupation.sql         # Faits Occupation
│
└── marts/                           # ✅ Data Marts (Vues Matérialisées)
    ├── financier/
    │   └── mart_performance_financiere.sql
    ├── occupation/
    │   └── mart_occupation_zones.sql
    ├── clients/
    │   └── mart_portefeuille_clients.sql
    └── operationnel/
        └── mart_kpi_operationnels.sql

snapshots/
└── snapshot_entreprises.sql         # Historique des changements

macros/
└── sigeti_macros.sql                # Macros dbt réutilisables
```

### 2. Flux de Transformation

```
Sources (SIGETI Node DB)
         │
         ▼
    STAGING LAYER (Vues)
    ├─ stg_entreprises
    ├─ stg_factures
    ├─ stg_paiements
    └─ stg_zones
         │
         ▼
    DIMENSIONS LAYER
    ├─ dim_entreprises
    ├─ dim_zones
    ├─ dim_dates
    └─ dim_client_segment
         │
         ├─────────────────┐
         ▼                 ▼
    FACTS LAYER        MARTS LAYER
    ├─ fact_factures   ├─ mart_performance_financiere
    ├─ fact_paiements  ├─ mart_occupation_zones
    └─ fact_occupation ├─ mart_portefeuille_clients
                       └─ mart_kpi_operationnels
```

### 3. Fonctionnalités Data

| **Fonctionnalité** | **Description** | **Implémentation** |
|---|---|---|
| **ETL Complet** | Extraction, transformation, chargement des données | dbt + PostgreSQL |
| **Staging Models** | Couche intermédiaire de transformation | Views SQL |
| **Dimensions** | Tables de référence dénormalisées | Tables physiques |
| **Facts Tables** | Tables de faits granulaires | Tables physiques |
| **Data Marts** | Vues matérialisées pour dashboards | Views matérialisées |
| **Tests de Qualité** | Validation des données | dbt tests (tests_quality.yml) |
| **Snapshots** | Capture des changements historiques | Snapshots dbt |
| **Macros** | Transformations réutilisables | Macros dbt |
| **Documentation** | Documentation auto-générée | dbt docs |
| **Performance** | Indexation et optimisation requêtes | Indexes SQL |

### 4. Marts Disponibles

#### 📊 mart_performance_financiere
```sql
Colonnes principales:
- ca_total                    -- Chiffre d'affaires total
- montant_impaye              -- Montant impayé
- taux_paiement_pct           -- Taux de paiement (%)
- delai_moyen_paiement        -- Délai moyen de paiement (jours)
- taux_recouvrement_moyen     -- Taux de recouvrement (%)
- creances_clients_montant    -- Montant des créances
```

#### 📍 mart_occupation_zones
```sql
Colonnes principales:
- zone_name                   -- Nom de la zone
- total_lots                  -- Nombre total de lots
- lots_disponibles            -- Lots non attribués
- lots_attribues              -- Lots attribués
- taux_occupation             -- Taux d'occupation (%)
- surface_total_hectares      -- Surface totale (ha)
- viabilisation_status        -- Statut de viabilisation
```

#### 👥 mart_portefeuille_clients
```sql
Colonnes principales:
- raison_sociale              -- Nom de l'entreprise
- secteur_activite            -- Secteur d'activité
- chiffre_affaires_total      -- CA de l'entreprise
- nombre_lots_attribues       -- Lots possédés
- taux_paiement_pct           -- Taux de paiement
- segment_client              -- Segmentation (A/B/C)
```

#### 📈 mart_kpi_operationnels
```sql
Colonnes principales:
- kpi_name                    -- Nom du KPI
- valeur_actuelle             -- Valeur actuelle
- valeur_precedente           -- Valeur période précédente
- variance_pct                -- Variance (%)
- tendance                    -- Direction (↑/↓)
```

### 5. Commandes dbt Courantes

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Construire tous les modèles
dbt run

# Construire par couche
dbt run --select staging.*        # Staging uniquement
dbt run --select dimensions.*     # Dimensions uniquement
dbt run --select facts.*          # Facts uniquement
dbt run --select marts.*          # Marts uniquement

# Construire un modèle spécifique
dbt run --select mart_performance_financiere

# Exécuter les tests
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve                    # Accès à http://localhost:8080

# Analyser la dépendance
dbt dag
```

---

# PARTIE BACKEND - Django REST API

## 🔌 Architecture Backend

### 1. Structure du Projet

```
backend/
├── sigeti_bi/                        # Configuration Django
│   ├── settings.py                  # Paramètres (DB, CORS, REST Framework)
│   ├── urls.py                      # Routes principales
│   └── wsgi.py                      # WSGI pour production
│
├── analytics/                        # App modèles DWH
│   ├── models.py                    # Models mappant les marts
│   │   ├── MartPerformanceFinanciere
│   │   ├── MartOccupationZones
│   │   ├── MartPortefeuilleClients
│   │   ├── MartKPIOperationnels
│   │   ├── Alert
│   │   └── AlertThreshold
│   └── apps.py
│
├── api/                              # App API REST
│   ├── views.py                     # ViewSets et endpoints
│   │   ├── MartPerformanceFinanciereViewSet
│   │   ├── MartOccupationZonesViewSet
│   │   ├── MartPortefeuilleClientsViewSet
│   │   ├── MartKPIOperationnelsViewSet
│   │   ├── AlertViewSet
│   │   └── AlertThresholdViewSet
│   ├── serializers.py               # Sérialiseurs DRF
│   ├── urls.py                      # Routes API
│   ├── auth_views.py               # Authentification JWT
│   ├── cache_decorators.py         # Mise en cache
│   └── filters.py                  # Filtres personnalisés
│
├── ai_chat/                          # App Chatbot IA
│   ├── views.py                    # Endpoints chat
│   ├── query_engine.py             # Moteur requêtes (règles + GPT)
│   ├── chat_service.py             # Service chat
│   ├── text_normalizer.py          # Normalisation texte
│   └── urls.py                     # Routes chat
│
├── alerts/                           # App Alertes
│   ├── views.py                    # Endpoints alertes
│   ├── serializers.py              # Sérialiseurs
│   └── urls.py                     # Routes alertes
│
└── manage.py                        # CLI Django
```

### 2. Endpoints API

#### 📊 **Endpoints Financiers**
```
GET  /api/financier/                           # Tous les enregistrements
GET  /api/financier/summary/                   # Résumé financier global
GET  /api/financier/by_zone/                   # Financier par zone
GET  /api/financier/tendances_mensuelles/      # Tendances mensuelles
GET  /api/financier/tendances_trimestrielles/  # Tendances trimestrielles
GET  /api/financier/analyse_recouvrement/      # Analyse recouvrement
GET  /api/financier/top_zones_performance/     # Zones les plus performantes
GET  /api/financier/clients_inactifs/          # Clients inactifs
GET  /api/financier/impaye_analyse/            # Analyse des impayés
```

#### 📍 **Endpoints Occupation**
```
GET  /api/occupation/                          # Tous les enregistrements
GET  /api/occupation/summary/                  # Résumé occupation
GET  /api/occupation/by_zone/                  # Occupation par zone
GET  /api/occupation/zones_map/                # Zones avec coordonnées
GET  /api/occupation/top_zones_performance/    # Zones performantes
GET  /api/occupation/utilisation_comparatif/   # Comparatif utilisation
GET  /api/occupation/projection_futures/       # Projection future
```

#### 👥 **Endpoints Clients**
```
GET  /api/clients/                             # Tous les clients
GET  /api/clients/summary/                     # Résumé portefeuille
GET  /api/clients/by_segment/                  # Clients par segment
GET  /api/clients/top_clients/                 # Top clients
GET  /api/clients/inactifs/                    # Clients inactifs
GET  /api/clients/by_zone/                     # Clients par zone
GET  /api/clients/risque_analyse/              # Analyse des risques
GET  /api/clients/segmentation/                # Segmentation clients
```

#### 📈 **Endpoints Opérationnels**
```
GET  /api/operationnel/                        # Tous les KPIs
GET  /api/operationnel/summary/                # Résumé opérationnel
GET  /api/operationnel/kpi_details/            # Détail KPIs
GET  /api/operationnel/by_zone/                # KPIs par zone
GET  /api/operationnel/tendances/              # Tendances KPIs
```

#### 🚨 **Endpoints Alertes**
```
GET    /api/alerts/                            # Toutes les alertes
POST   /api/alerts/                            # Créer une alerte
GET    /api/alerts/{id}/                       # Détail alerte
PATCH  /api/alerts/{id}/                       # Mettre à jour
DELETE /api/alerts/{id}/                       # Supprimer
GET    /api/alerts/active/                     # Alertes actives
POST   /api/alerts/{id}/acknowledge/           # Acquitter
POST   /api/alerts/{id}/resolve/               # Résoudre
```

#### 🤖 **Endpoints Chatbot IA**
```
POST   /api/ai/chat/                           # Envoyer message
GET    /api/ai/history/                        # Historique chat
POST   /api/ai/query/                          # Requête SQL
GET    /api/ai/configure/                      # Configuration
```

#### 🔐 **Endpoints Authentification**
```
POST   /api/auth/login/                        # Se connecter
POST   /api/auth/logout/                       # Se déconnecter
POST   /api/auth/refresh/                      # Rafraîchir token
GET    /api/auth/me/                           # Profil utilisateur
```

### 3. Fonctionnalités Backend

| **Fonctionnalité** | **Description** | **Implémentation** |
|---|---|---|
| **REST API** | Endpoints pour tous les dashboards | Django REST Framework |
| **Authentification JWT** | Sécurisation des endpoints | Token-based auth |
| **Filtrage & Agrégation** | Filtres flexibles sur les données | django-filter |
| **Mise en Cache** | Optimisation des requêtes coûteuses | Cache decorators |
| **Alertes Automatiques** | Génération d'alertes basée sur seuils | Alert models + scheduler |
| **Chatbot IA** | Requêtes en langage naturel | Query engine + GPT |
| **Text Normalization** | Normalisation pour reconnaissance patterns | TextNormalizer |
| **Logging & Monitoring** | Traçabilité des requêtes | Django logging |
| **CORS** | Communication avec frontend React | django-cors-headers |
| **Pagination** | Gestion des gros datasets | DRF pagination |

### 4. Modèles Django

#### 🏪 Models (Read-only sur Marts)
```python
# bi_app/backend/analytics/models.py

class MartPerformanceFinanciere(models.Model):
    """Modèle mapping mart_performance_financiere"""
    zone = models.CharField()
    ca_total = models.DecimalField()
    montant_impaye = models.DecimalField()
    taux_paiement_pct = models.DecimalField()
    delai_moyen_paiement = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'dwh_marts_financier.mart_performance_financiere'

class MartOccupationZones(models.Model):
    """Modèle mapping mart_occupation_zones"""
    zone_name = models.CharField()
    total_lots = models.IntegerField()
    taux_occupation = models.DecimalField()
    class Meta:
        managed = False
        db_table = 'dwh_marts_occupation.mart_occupation_zones'

class Alert(models.Model):
    """Système d'alertes pour seuils critiques"""
    alert_type = models.CharField(choices=ALERT_TYPES)
    severity = models.CharField(choices=SEVERITY_LEVELS)
    status = models.CharField(choices=STATUS_CHOICES)
    title = models.CharField()
    message = models.TextField()
    context_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AlertThreshold(models.Model):
    """Configuration des seuils d'alerte"""
    alert_type = models.CharField()
    threshold_operator = models.CharField()
    threshold_value = models.DecimalField()
    severity_when_triggered = models.CharField()
```

### 5. Configuration des Alertes

```python
# Seuils configurables (AlertThreshold)

Seuil d'Occupation:
├─ Critique: < 30% ou > 95%   → Alerte RED
├─ Élevé: < 50% ou > 85%      → Alerte ORANGE
└─ Normal: 50-85%              → OK

Taux de Recouvrement:
├─ Critique: < 60%             → Alerte RED
├─ À surveiller: 60-80%        → Alerte YELLOW
└─ Bon: > 80%                  → OK

Taux d'Impayés:
├─ Critique: > 40%             → Alerte RED
├─ À surveiller: 30-40%        → Alerte YELLOW
└─ Normal: < 30%               → OK
```

### 6. Query Engine IA

```python
# bi_app/backend/ai_chat/query_engine.py

Architecture du moteur:
├─ TextNormalizer
│  └─ Normalise questions utilisateur
│     └─ Remplace synonymes
│        └─ Gère négations
│
└─ RuleBasedQueryEngine
   ├─ 30+ patterns prédéfinis
   ├─ Correspond questions aux patterns
   └─ Génère SQL + répond
   
Fonctionnalités:
- Compréhension langage naturel français
- Pattern matching avec normalisation
- Génération SQL automatique
- Cache des requêtes fréquentes
- Fallback GPT (optionnel)
```

### 7. Commandes Backend Courantes

```powershell
# Démarrer le serveur
cd bi_app/backend
python manage.py runserver

# Créer migration
python manage.py makemigrations

# Appliquer migrations
python manage.py migrate

# Tester un endpoint
python manage.py shell -c "exec(open('test_api.py').read())"

# Créer un superutilisateur
python manage.py createsuperuser

# Accéder à l'admin
# http://localhost:8000/admin
```

---

# PARTIE FRONTEND - React & Vite

## 🎨 Architecture Frontend

### 1. Structure du Projet

```
frontend/
├── src/
│   ├── pages/                        # Pages principales
│   │   ├── Login.jsx                # Page de connexion
│   │   ├── Dashboard.jsx            # Accueil (vue d'ensemble)
│   │   ├── Financier.jsx            # Dashboard financier
│   │   │   └── Composants:
│   │   │       ├─ Résumé financier
│   │   │       ├─ Graphiques CA/Impayés
│   │   │       ├─ Taux paiement
│   │   │       ├─ Délai moyen paiement
│   │   │       └─ Top clients par CA
│   │   │
│   │   ├── Occupation.jsx           # Dashboard occupation
│   │   │   └── Composants:
│   │   │       ├─ Carte zones (Leaflet)
│   │   │       ├─ Résumé occupation
│   │   │       ├─ Taux par zone
│   │   │       ├─ Disponibilité lots
│   │   │       └─ Viabilisation
│   │   │
│   │   ├── OccupationZoneDetails.jsx # Détail zone
│   │   ├── Clients.jsx              # Dashboard clients
│   │   │   └── Composants:
│   │   │       ├─ Segmentation clients
│   │   │       ├─ Top clients
│   │   │       ├─ Clients inactifs
│   │   │       ├─ Analyse risque
│   │   │       └─ Distribution secteurs
│   │   │
│   │   ├── ClientDetails.jsx        # Détail client
│   │   ├── Operationnel.jsx         # Dashboard opérationnel
│   │   │   └── Composants:
│   │   │       ├─ KPIs clés
│   │   │       ├─ Tendances
│   │   │       ├─ Performance zones
│   │   │       └─ Comparatifs
│   │   │
│   │   ├── AlertsAnalytics.jsx      # Dashboard alertes
│   │   │   └── Composants:
│   │   │       ├─ Résumé alertes actives
│   │   │       ├─ Graphiques risques
│   │   │       ├─ Scores zones
│   │   │       └─ Liste détaillée alertes
│   │   │
│   │   ├── ChatBot.jsx              # Interface chatbot
│   │   ├── ReportConfig.jsx         # Configuration rapports
│   │   └── AdminPanel.jsx           # Panneau admin
│   │
│   ├── components/                  # Composants réutilisables
│   │   ├── Layout.jsx              # Layout + navigation
│   │   ├── ProtectedRoute.jsx       # Guard authentification
│   │   ├── ZonesMap.jsx            # Carte Leaflet
│   │   ├── ChartsLibrary.jsx       # Graphiques Recharts
│   │   ├── DataTable.jsx           # Tables données
│   │   ├── KPICard.jsx             # Carte KPI
│   │   ├── LoadingSpinner.jsx      # Indicateur chargement
│   │   └── ErrorBoundary.jsx       # Gestion erreurs
│   │
│   ├── services/
│   │   ├── api.js                  # Client HTTP Axios
│   │   │   ├─ financierAPI.*
│   │   │   ├─ occupationAPI.*
│   │   │   ├─ clientsAPI.*
│   │   │   ├─ alertsAPI.*
│   │   │   └─ authAPI.*
│   │   └── auth.js                 # Gestion authentification
│   │
│   ├── hooks/                      # React Hooks personnalisés
│   │   ├─ useAuth.js
│   │   ├─ useFetch.js
│   │   ├─ useCache.js
│   │   └─ useNotification.js
│   │
│   ├── store/                      # État global (optionnel)
│   │   ├─ authContext.js
│   │   └─ dataContext.js
│   │
│   ├── styles/                     # Fichiers CSS/Tailwind
│   │   ├─ globals.css
│   │   └─ components.css
│   │
│   ├── App.jsx                     # Composant racine
│   ├── index.css                   # CSS global
│   └── main.jsx                    # Point d'entrée
│
├── public/                          # Assets statiques
├── vite.config.js                  # Configuration Vite
├── tailwind.config.js              # Configuration Tailwind
├── postcss.config.js               # Configuration PostCSS
└── package.json                    # Dépendances npm

public/
├── index.html                      # HTML principal
└── assets/                         # Logos, images
```

### 2. Pages et Fonctionnalités

#### 📱 **Page Login**
```jsx
Fonctionnalités:
✅ Formulaire connexion (email/mot de passe)
✅ Validation des entrées
✅ Gestion des erreurs
✅ Redirection après connexion
✅ Mémorisation session (token JWT)
✅ Design responsive
```

#### 📊 **Dashboard Principal**
```jsx
Affiche:
✅ Vue d'ensemble (KPIs clés)
✅ Résumé financier
✅ Résumé occupation
✅ Résumé clients
✅ Résumé opérationnel
✅ Alertes actives
✅ Graphiques tendances
```

#### 💰 **Dashboard Financier**
```jsx
Sections:
┌─ Résumé
│  ├─ CA Total (FCFA)
│  ├─ Montant Impayé (FCFA)
│  ├─ Taux Paiement (%)
│  ├─ Délai Moyen Paiement (jours)
│  ├─ Taux Recouvrement (%)
│  └─ Créances Clients (FCFA)
│
├─ Graphiques
│  ├─ CA vs Impayés (Bar Chart)
│  ├─ Taux Paiement Évolution (Line Chart)
│  ├─ Top 10 Clients par CA (Bar Chart)
│  ├─ Répartition Secteurs (Pie Chart)
│  ├─ Tendances Mensuelles (Area Chart)
│  └─ Délai Paiement par Zone (Treemap)
│
├─ Filtres
│  ├─ Plage de dates
│  ├─ Zone(s)
│  ├─ Secteur(s)
│  ├─ Client(s)
│  └─ Statut de paiement
│
└─ Exports
   ├─ PDF
   ├─ Excel
   └─ CSV
```

#### 📍 **Dashboard Occupation**
```jsx
Sections:
┌─ Résumé
│  ├─ Taux Occupation Global (%)
│  ├─ Lots Disponibles
│  ├─ Lots Attribués
│  ├─ Surface Total (ha)
│  ├─ Zones Critiques (nb)
│  └─ Viabilisation (%)
│
├─ Composants
│  ├─ Carte Leaflet avec zones
│  │  ├─ Zone en vert: >70%
│  │  ├─ Zone en jaune: 50-70%
│  │  ├─ Zone en rouge: <50%
│  │  └─ Popup détail au clic
│  │
│  ├─ Tableau zones avec métriques
│  ├─ Graphique taux occupation
│  ├─ Disponibilité lots (gauge)
│  ├─ Viabilisation status
│  └─ Projection future
│
├─ Filtres
│  ├─ État occupation
│  ├─ Viabilisation
│  └─ Secteur activité
│
└─ Navigation
   └─ Clic sur zone → OccupationZoneDetails
```

#### 👥 **Dashboard Clients**
```jsx
Sections:
┌─ Résumé
│  ├─ Nb Clients Total
│  ├─ Nb Clients Actifs
│  ├─ Nb Clients Inactifs
│  ├─ CA Moyen Client
│  ├─ Taux Paiement Moyen
│  └─ Secteur Dominant
│
├─ Graphiques
│  ├─ Segmentation A/B/C (Donut)
│  ├─ Distribution secteurs (Bar)
│  ├─ Top 20 clients (Bar)
│  ├─ Clients inactifs (List)
│  ├─ Analyse risque (Risk Score)
│  └─ Répartition zones (Sunburst)
│
├─ Tableaux
│  ├─ Clients par segment
│  ├─ Clients inactifs
│  ├─ Clients à risque
│  └─ Répartition par zone
│
├─ Filtres
│  ├─ Segment (A/B/C)
│  ├─ Secteur
│  ├─ Zone
│  ├─ Statut activité
│  └─ Plage CA
│
└─ Navigation
   └─ Clic sur client → ClientDetails
```

#### 📈 **Dashboard Opérationnel**
```jsx
Sections:
┌─ KPIs Clés
│  ├─ Taux Occupation Global
│  ├─ Délai Moyen Paiement
│  ├─ Taux Recouvrement
│  ├─ Nb Clients Actifs
│  ├─ CA Total
│  └─ Impayés Total
│
├─ Tendances
│  ├─ KPIs mensuels
│  ├─ Variance vs période précédente
│  ├─ Comparatif zones
│  └─ Prévisions futures
│
├─ Performance Zones
│  ├─ Ranking zones
│  ├─ Scores composites
│  └─ Recommandations
│
└─ Comparatifs
   ├─ Zones vs KPI
   ├─ Périodes vs KPI
   └─ Segments vs KPI
```

#### 🚨 **Dashboard Alertes**
```jsx
Sections:
┌─ Résumé Alertes
│  ├─ Nb Alertes Actives
│  ├─ Nb Alertes Critiques
│  ├─ Nb Alertes Élevées
│  └─ Nb Alertes Moyennes
│
├─ Graphiques
│  ├─ Alertes par sévérité
│  ├─ Alertes par type
│  ├─ Alertes timeline
│  └─ Zones de risque (heatmap)
│
├─ Liste Détaillée
│  ├─ Sévérité (couleur)
│  ├─ Titre alerte
│  ├─ Message
│  ├─ Date création
│  ├─ Statut (actif/acquitté/résolu)
│  └─ Actions (Acquitter/Résoudre)
│
├─ Filtres
│  ├─ Sévérité
│  ├─ Type alerte
│  ├─ Statut
│  ├─ Zone
│  └─ Plage dates
│
└─ Tri
   ├─ Par date (récent)
   ├─ Par sévérité
   ├─ Par zone
   └─ Par statut
```

#### 🤖 **Chatbot IA**
```jsx
Fonctionnalités:
✅ Interface chat conversationnelle
✅ Questions en langage naturel français
✅ Réponses structurées avec données
✅ Historique conversation
✅ Suggestions questions
✅ Affichage tableaux/graphiques
✅ Export résultats

Capacités:
- Requêtes financières
- Requêtes occupation
- Requêtes clients
- Analyse tendances
- Recherche spécifique
```

#### 📋 **Configuration Rapports**
```jsx
Fonctionnalités:
✅ Sélection dashboard
✅ Sélection dates
✅ Sélection bénéficiaires
✅ Planification (immédiat/futur)
✅ Récurrence (une fois/quotidien/hebdomadaire)
✅ Format (PDF/Excel)
✅ Aperçu avant envoi
```

### 3. Composants Réutilisables

| **Composant** | **Utilisation** | **Props** |
|---|---|---|
| **Layout** | Navigation + Layout global | `children, user` |
| **ProtectedRoute** | Gestion authentification | `component, path` |
| **ZonesMap** | Carte Leaflet interactive | `zones, onZoneClick` |
| **KPICard** | Affichage d'un KPI | `title, value, unit, status` |
| **DataTable** | Tableau paginé filtrable | `data, columns, actions` |
| **LineChart** | Graphique en ligne | `data, x, y, title` |
| **BarChart** | Graphique en barres | `data, categories, title` |
| **PieChart** | Graphique circulaire | `data, categories, title` |
| **LoadingSpinner** | Indicateur chargement | `size, color` |
| **ErrorBoundary** | Gestion des erreurs | `children` |

### 4. API Service

```javascript
// bi_app/frontend/src/services/api.js

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// Interceptor pour ajouter token JWT
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor pour gérer 401
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Financier APIs
export const financierAPI = {
  getSummary: () => api.get('/financier/summary/'),
  getByZone: (zone) => api.get(`/financier/by_zone/${zone}/`),
  getTendances: (period) => api.get(`/financier/tendances_${period}/`),
}

// Occupation APIs
export const occupationAPI = {
  getSummary: () => api.get('/occupation/summary/'),
  getZones: () => api.get('/occupation/zones_map/'),
  getByZone: (zone) => api.get(`/occupation/${zone}/`),
}

// ... etc pour clients, alertes, auth
```

### 5. React Query pour la Gestion d'État

```javascript
// Exemple d'utilisation
const { data: financier, isLoading } = useQuery({
  queryKey: ['financier-summary'],
  queryFn: () => financierAPI.getSummary(),
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
})

// Avantages:
- Gestion automatique du cache
- Gestion des erreurs
- Refetch automatique
- Background updates
```

### 6. Commandes Frontend Courantes

```powershell
# Installation des dépendances
cd bi_app/frontend
npm install

# Démarrer le serveur de développement
npm run dev
# Accès à http://localhost:5173

# Build pour production
npm run build

# Aperçu build
npm run preview

# Linting (si ESLint configuré)
npm run lint
```

### 7. Configuration Vite

```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

## 🔄 Flux de Données Complet

### Flux Requête (Frontend → Backend → Data)

```
1. USER ACTION (Frontend React)
   └─ Clique sur page Financier
   
2. REACT QUERY REQUEST
   └─ const { data } = useQuery({
       queryKey: ['financier-summary'],
       queryFn: () => financierAPI.getSummary()
      })
   
3. AXIOS CALL (Frontend)
   └─ GET http://localhost:8000/api/financier/summary/
      Headers: Authorization: Bearer <JWT_TOKEN>
   
4. DJANGO ROUTING (Backend)
   └─ api/urls.py route vers:
      router.register('financier', MartPerformanceFinanciereViewSet)
   
5. VIEWSET PROCESSING (Backend)
   └─ MartPerformanceFinanciereViewSet.list()
      ├─ Récupère queryset
      ├─ Applique filtres
      ├─ Applique agrégations
      ├─ Applique pagination
      ├─ Sérialise en JSON
      └─ Retourne réponse
   
6. DATABASE QUERY (PostgreSQL)
   └─ SELECT * FROM dwh_marts_financier.mart_performance_financiere
      ├─ WHERE conditions (filtres)
      ├─ GROUP BY (agrégations)
      └─ ORDER BY (tri)
   
7. RESPONSE FLOW (Backend → Frontend)
   └─ Django retourne JSON
      ├─ Http 200 OK
      ├─ Content-Type: application/json
      └─ Body: { results: [...], count: N, ... }
   
8. REACT QUERY CACHE
   └─ Met en cache la réponse
      ├─ Validité: 5 minutes
      ├─ Mise à jour auto après 5 min
      └─ Manuel refetch possible
   
9. COMPONENT RENDER (Frontend React)
   └─ Composant Financier.jsx reçoit data
      ├─ Transforme data si besoin
      ├─ Génère graphiques (Recharts)
      ├─ Affiche tableaux (DataTable)
      └─ Re-render UI avec données
```

### Flux Alerte (Data → Backend → Frontend)

```
1. DBT PIPELINE (nightly)
   └─ dbt run --select marts.*
      ├─ Refreshe mart_performance_financiere
      ├─ Refreshe mart_occupation_zones
      ├─ Refreshe mart_portefeuille_clients
      └─ Refreshe mart_kpi_operationnels

2. ALERT CHECKING (Scheduler - Backend)
   └─ Toutes les 10 minutes, task:
      ├─ Lit AlertThreshold config
      ├─ Query les marts
      ├─ Compare actual vs threshold
      ├─ Si dépassement → Crée Alert
      └─ Stored en BD: analytics_alert table

3. ALERT API (Backend)
   └─ GET /api/alerts/
      ├─ Retrieves from analytics_alert
      ├─ Filtre par status=active
      ├─ Sort par created_at DESC
      └─ Retourne JSON

4. ALERT DISPLAY (Frontend)
   └─ useQuery fetche /api/alerts/
      ├─ Cache 2 minutes
      ├─ Poll refresh toutes les 5 min
      ├─ Affiche dans AlertsAnalytics.jsx
      └─ Color-code par sévérité

5. USER ACTION
   └─ User ack alerte
      ├─ PATCH /api/alerts/{id}/acknowledge/
      ├─ Backend met à jour status
      ├─ Frontend refetch
      └─ UI met à jour
```

---

## 🛠️ Technologies Utilisées

### **Backend**
```
Framework:
  ├─ Django 5.0
  ├─ Django REST Framework 3.14
  ├─ django-cors-headers
  ├─ django-filter
  └─ psycopg2-binary

Authentication:
  ├─ Django Token Auth
  ├─ JWT (via djangorestframework-simplejwt)
  └─ Session Auth (legacy)

Database:
  ├─ PostgreSQL 14+
  ├─ psycopg2 adapter
  └─ Django ORM

AI/NLP:
  ├─ OpenAI GPT (optional)
  ├─ Custom Text Normalization
  ├─ Pattern Matching Engine
  └─ SQL Generation

Utilities:
  ├─ pandas (data manipulation)
  ├─ python-dotenv (config)
  └─ logging (monitoring)
```

### **Frontend**
```
Framework & Build:
  ├─ React 18.2
  ├─ Vite 5.0
  ├─ React Router 6.20
  └─ Tailwind CSS 3.3

State & Data:
  ├─ TanStack Query 5.14 (React Query)
  ├─ Axios 1.6
  └─ localStorage (for JWT)

Charts & Maps:
  ├─ Recharts 2.10
  ├─ Leaflet 1.9+
  ├─ react-leaflet 4.0+
  └─ Lucide React (icons)

UI Components:
  ├─ React Router components
  ├─ Custom components library
  ├─ HTML5 semantic
  └─ CSS3 Flexbox/Grid
```

### **Data & ETL**
```
Orchestration:
  ├─ dbt 1.5+
  ├─ Prefect 2.0+
  └─ PostgreSQL 14+

Source:
  ├─ PostgreSQL (SIGETI Node DB)
  └─ CSV/Seeds

Testing:
  ├─ dbt test
  ├─ Great Expectations (optional)
  └─ SQL validation
```

---

## 📊 Résumé des Fonctionnalités

### **Couche Data (dbt)**
✅ Staging models (7 sources)
✅ Dimensions (4+)
✅ Facts (3+)
✅ Marts (4 domaines)
✅ Tests de qualité
✅ Snapshots historiques
✅ Macros réutilisables
✅ Documentation auto-générée

### **Couche Backend (Django)**
✅ 40+ endpoints REST
✅ JWT authentification
✅ Alertes automatiques (12+ types)
✅ Chatbot IA conversationnel
✅ Query engine hybride (rules + GPT)
✅ Caching intelligent
✅ Filtrage & agrégation
✅ Pagination
✅ Logging détaillé
✅ CORS configuré

### **Couche Frontend (React)**
✅ 8+ pages dashboards
✅ 3 cartes interactives (Leaflet)
✅ 50+ graphiques (Recharts)
✅ 20+ tableaux de données
✅ Authentification JWT
✅ Navigation fluide
✅ Responsive design
✅ Export PDF/Excel
✅ Configuration rapports
✅ Chatbot conversationnel

---

## 🚀 Démarrage Complet

```powershell
# 1. Data Pipeline
cd DWH_SIG
.\venv\Scripts\Activate.ps1
dbt deps
dbt run
dbt test

# 2. Backend API
cd bi_app/backend
python manage.py migrate
python manage.py runserver
# http://localhost:8000

# 3. Frontend React
cd bi_app/frontend
npm install
npm run dev
# http://localhost:5173

# 4. Chatbot (optionnel - configuré automatiquement)
# Disponible via http://localhost:5173/chatbot
```

---

**Dernière mise à jour**: Novembre 2025
**Status**: ✅ Production Ready

