# Dashboard Conformité & Infractions

## 📊 Vue d'ensemble

Le **Dashboard Conformité & Infractions** offre une visibilité complète sur les infractions identifiées, leur sévérité et leur résolution au sein de l'organisation SIGETI.

## 🎯 KPIs Principaux

### Cartes de Statistiques
1. **Total Infractions** - Nombre total d'infractions détectées
2. **Taux de Résolution** - Pourcentage d'infractions résolues
3. **Délai Moyen** - Temps moyen de résolution en jours
4. **Infractions Critiques** - Nombre d'infractions de sévérité critique
5. **Zones Affectées** - Nombre de zones avec infractions
6. **Sévérité Moyenne** - Score moyen de sévérité (1-4)

### Visualisations

#### 1. Tendance Annuelle des Infractions
- **Type**: Area Chart + Line Chart combiné
- **Données**: 
  - Area: Total infractions par mois
  - Line: Taux de résolution (%)
- **Utilité**: Identifier les tendances et pics d'infractions

#### 2. Distribution par Gravité
- **Type**: Pie Chart
- **Catégories**:
  - 🟢 Mineure (Green)
  - 🟡 Modérée (Amber)
  - 🔴 Majeure (Red)
  - 🟣 Critique (Purple)
- **Utilité**: Comprendre la composition des infractions

#### 3. Infractions par Zone
- **Type**: Stacked Bar Chart
- **Données**: Infractions groupées par zone et sévérité
- **Utilité**: Identifier les zones problématiques

#### 4. Performance de Résolution
- **Type**: Scatter Chart
- **Axes**:
  - X: Total infractions par zone
  - Y: Taux de résolution (%)
- **Utilité**: Correlation entre volume et efficacité de résolution

#### 5. Détail des Infractions
- **Type**: Data Table
- **Colonnes**:
  - Zone
  - Type
  - Gravité (avec badge coloré)
  - Statut (Résolue/En cours)
  - Date de détection
  - Délai en jours
- **Filtres**:
  - Année
  - Zone
  - Gravité
  - Statut (Résolues/Non résolues)

## 🔧 Filtres Disponibles

### Filtre Année
- Sélection: 2023, 2024, 2025, 2026
- Défaut: Année courante
- Impact: Affecte TOUS les graphiques et cartes

### Filtre Zone
- Options: Toutes les zones du système
- Défaut: Toutes les zones
- Impact: Filtre les infractions au détail

### Filtre Gravité
- Options: Mineure, Modérée, Majeure, Critique
- Défaut: Toutes les gravités
- Impact: Filtre les infractions au détail

### Filtres Statut
- **Résolues** (toggle): Infractions résolues
- **Non résolues** (toggle): Infractions en attente de résolution
- Défaut: Afficher les deux
- Impact: Filtre les infractions au détail

## 📈 Architecture Technique

### Frontend (React)
```
bi_app/frontend/src/pages/ComplianceInfractions.jsx
├── State Management (useState)
│   ├── selectedYear
│   ├── selectedZone
│   ├── selectedSeverity
│   ├── showResolved
│   └── showUnresolved
├── Data Fetching (useQuery)
│   ├── getSummary()
│   ├── getTendancesAnnuelles()
│   ├── getInfractionsParZone()
│   ├── getDistributionGravite()
│   ├── getResolutionStats()
│   ├── getInfractionsDetail()
│   └── getZones()
├── Components
│   ├── StatsCard (x6)
│   ├── LineChart/AreaChart
│   ├── PieChart
│   ├── BarChart
│   ├── ScatterChart
│   └── Data Table
└── Export
    └── ExportButton
```

### Backend (Django)
```
bi_app/backend/api/compliance_views.py
├── ComplianceViewSet
│   ├── @summary() - KPIs résumé
│   ├── @tendances_annuelles() - Tendances mensuelles
│   ├── @infractions_par_zone() - Groupement par zone
│   ├── @distribution_gravite() - Distribution par sévérité
│   ├── @resolution_stats() - Performance résolution
│   ├── @infractions_detail() - Détail avec filtres
│   ├── @zones() - Liste des zones
│   └── @export_rapport() - Export complet
```

### Data Mart (dBT)
```
models/marts/operationnel/mart_conformite_infractions.sql
├── Source: fait_infractions + dim_zones_industrielles
├── Aggregations
│   ├── Volume: nombre_infractions, resolues, non_resolues
│   ├── Distribution: par gravité (mineure/moderee/majeure/critique)
│   ├── Taux: taux_resolution_pct
│   ├── Délais: moyen, max, median
│   └── Sévérité: score moyen
├── Dimensions
│   ├── zone_id, zone_name
│   ├── annee, mois, annee_mois
│   └── date_detection, date_resolution
└── Indexes
    ├── zone_id
    └── date_detection
```

## 🔌 Endpoints API

### Tous les endpoints sont au préfixe: `/api/compliance/`

#### 1. GET `/summary/`
**Résumé des infractions**
```bash
curl -X GET "http://localhost:8000/api/compliance/summary/?annee=2024"
```
**Réponse**:
```json
{
  "nombre_total_infractions": 156,
  "infractions_resolues": 142,
  "taux_resolution_moyen_pct": 91.03,
  "delai_moyen_resolution": 3.45,
  "nombre_infractions_critiques": 8,
  "nombre_zones_affectees": 12,
  "severite_moyenne": 1.85
}
```

#### 2. GET `/tendances-annuelles/`
**Tendances mensuelles**
```bash
curl -X GET "http://localhost:8000/api/compliance/tendances-annuelles/"
```
**Réponse**:
```json
[
  {
    "annee_mois": "2024-01",
    "nombre_infractions": 12,
    "infractions_resolues": 10,
    "taux_resolution_pct": 83.33,
    "delai_moyen_resolution": 4.2
  }
]
```

#### 3. GET `/infractions-par-zone/`
**Infractions par zone**
```bash
curl -X GET "http://localhost:8000/api/compliance/infractions-par-zone/?annee=2024"
```

#### 4. GET `/distribution-gravite/`
**Distribution par gravité**
```bash
curl -X GET "http://localhost:8000/api/compliance/distribution-gravite/?annee=2024"
```

#### 5. GET `/resolution-stats/`
**Statistiques de résolution**
```bash
curl -X GET "http://localhost:8000/api/compliance/resolution-stats/?annee=2024"
```

#### 6. GET `/infractions-detail/`
**Détail avec filtres**
```bash
curl -X GET "http://localhost:8000/api/compliance/infractions-detail/?annee=2024&zone_id=5&gravite=critique&statut=unresolved"
```

#### 7. GET `/zones/`
**Liste des zones**
```bash
curl -X GET "http://localhost:8000/api/compliance/zones/"
```

#### 8. GET `/export-rapport/`
**Export rapport complet**
```bash
curl -X GET "http://localhost:8000/api/compliance/export-rapport/?annee=2024" --output rapport.csv
```

## 📊 Schéma de la Mart

### Colonnes Principales

| Colonne | Type | Description |
|---------|------|-------------|
| zone_id | INT | Identifiant de la zone |
| zone_name | VARCHAR | Nom de la zone |
| annee | INT | Année |
| mois | INT | Mois (1-12) |
| annee_mois | VARCHAR | Format YYYY-MM |
| nombre_infractions | INT | Total infractions |
| infractions_resolues | INT | Nombre résolues |
| infractions_non_resolues | INT | Nombre non résolues |
| infractions_mineures | INT | Count by gravité |
| infractions_moderees | INT | Count by gravité |
| infractions_majeures | INT | Count by gravité |
| infractions_critiques | INT | Count by gravité |
| taux_resolution_pct | DECIMAL | % résolues |
| delai_moyen_resolution_jours | DECIMAL | Jours moyens |
| delai_max_resolution_jours | INT | Max jours |
| severite_moyenne | DECIMAL | Score 1-4 |

## 🚀 Déploiement

### Prérequis
1. dBT avec mart activée (`enabled=true`)
2. Django avec ComplianceViewSet enregistré dans URLs
3. React avec composant ComplianceInfractions importé
4. Data source: Table `fait_infractions` remplie

### Steps
```bash
# 1. Activer la mart
dbt run --select mart_conformite_infractions

# 2. Vérifier les données
psql -c "SELECT COUNT(*) FROM marts_operationnel.mart_conformite_infractions;"

# 3. Lancer les tests
dbt test --select mart_conformite_infractions

# 4. Frontend: Component déjà intégré dans le routeur
```

## 📝 Exemples d'Utilisation

### Cas d'usage 1: Monitoring Conformité
- Accéder à `/compliance`
- Observer les KPIs principaux (total, taux résolution, délai)
- Identifier si 🔴 tendances négatives
- Action: Cliquer sur les zones problématiques

### Cas d'usage 2: Analyse par Gravité
- Sélectionner une gravité dans le filtre
- Observer la distribution dans le pie chart
- Comparer avec la tendance (monthly trend)
- Action: Drill-down au détail pour voir infractions spécifiques

### Cas d'usage 3: Export pour Reporting
- Cliquer "Export" en haut à droite
- Télécharger le rapport CSV
- Importer dans Excel pour présentation
- Utiliser pour reporting mensuel

### Cas d'usage 4: Investigation Zone
- Sélectionner une zone dans le filtre
- Observer le scatter chart (volume vs resolution rate)
- Voir le détail au tableau
- Identifier infractions non résolues
- Action: Créer plan d'action

## 🔐 Permissions

- ✅ **Tous les utilisateurs**: Lecture dashboard
- ✅ **Dashboard "compliance"**: Peut être restreint par rôle
- ❌ **Modification**: Non disponible (read-only)
- ✅ **Export**: Disponible pour tous

## 📞 Support

### Issues Communes

**Q: Aucune donnée affichée**
- A: Vérifier que mart est activée (`enabled=true`)
- A: Vérifier que `fait_infractions` contient des données
- A: Vérifier que l'année sélectionnée a des données

**Q: Graphiques vides**
- A: Vérifier les filtres sélectionnés
- A: Essayer "Toutes les gravités"
- A: Essayer année précédente (données plus anciennes)

**Q: Erreur API 404**
- A: Vérifier que endpoints sont enregistrés dans `urls.py`
- A: Vérifier que `compliance_views.py` est importé correctement
- A: Relancer Django: `python manage.py runserver`

**Q: Performances lentes**
- A: Vérifier les indexes sur zone_id et date_detection
- A: Limiter la plage de dates
- A: Vérifier la charge du serveur

