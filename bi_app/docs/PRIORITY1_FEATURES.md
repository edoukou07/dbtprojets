# Guide d'Utilisation - Fonctionnalités Essentielles SIGETI BI

## 🎯 Priorité 1 : Fonctionnalités Implémentées

### 1. **FilterBar - Filtres Dynamiques & Période Personnalisée** ✅

#### Emplacement
- Tous les dashboards principaux
- En haut de page, avant les KPIs

#### Fonctionnalités
- **Sélection de Période** :
  - Aujourd'hui
  - 7 derniers jours
  - 30 derniers jours
  - Ce mois
  - Ce trimestre
  - Cette année
  - **Période personnalisée** (dates manuelles)

- **Filtres Contextuels** :
  - **Zone Industrielle** : Filtrer par zone spécifique
  - **Domaine d'Activité** : Filtrer par secteur
  - **Comparaison N vs N-1** : Comparer avec période précédente (checkbox)

#### Utilisation
```jsx
import FilterBar from '../components/FilterBar'

<FilterBar 
  onFilterChange={(newFilters) => setFilters(newFilters)}
  showZoneFilter={true}
  showDomaineFilter={true}
  showComparison={true}
/>
```

#### Props
- `onFilterChange`: Callback appelé lors du changement de filtres
- `showZoneFilter`: Afficher le filtre zone (default: true)
- `showDomaineFilter`: Afficher le filtre domaine (default: true)
- `showComparison`: Afficher l'option de comparaison (default: false)

---

### 2. **ExportButton - Export Multi-formats** ✅

#### Formats Supportés
- **Excel (.xlsx)** : Format tableur complet avec colonnes ajustées
- **CSV (.csv)** : Données brutes pour import dans d'autres outils
- **PDF (.pdf)** : Rapport imprimable avec header, footer, pagination

#### Fonctionnalités
- Export avec nom de fichier automatique (horodatage)
- Indicateur de progression
- Message de succès visuel
- Compteur de lignes de données
- Dropdown menu élégant

#### Utilisation
```jsx
import ExportButton from '../components/ExportButton'

const data = [
  { Nom: 'Client A', CA: 1000000, Status: 'Actif' },
  { Nom: 'Client B', CA: 500000, Status: 'Inactif' },
]

<ExportButton 
  data={data}
  filename="rapport_clients"
  title="Rapport Clients SIGETI"
  showPDF={true}
  showExcel={true}
  showCSV={true}
/>
```

#### Props
- `data`: Array d'objets à exporter (requis)
- `filename`: Nom du fichier (default: 'export')
- `title`: Titre du rapport PDF (default: 'Rapport')
- `showPDF`: Afficher option PDF (default: true)
- `showExcel`: Afficher option Excel (default: true)
- `showCSV`: Afficher option CSV (default: true)

#### Exemple PDF Généré
```
┌──────────────────────────────────────┐
│ Rapport Clients SIGETI               │
│ Généré le 13/11/2025                 │
├──────────────────────────────────────┤
│ Nom      │ CA        │ Status       │
├──────────────────────────────────────┤
│ Client A │ 1,000,000 │ Actif        │
│ Client B │   500,000 │ Inactif      │
└──────────────────────────────────────┘
         Page 1 / 1
```

---

### 3. **AlertsPanel - Système d'Alertes** ✅

#### Types d'Alertes
- `taux_recouvrement` : Taux de Recouvrement Critique
- `facture_impayee` : Facture Impayée Ancienne
- `client_inactif` : Client Inactif
- `occupation_faible` : Taux d'Occupation Faible
- `objectif_non_atteint` : Objectif Non Atteint

#### Niveaux de Sévérité
- **Critical** 🔴 : Action immédiate requise
- **High** 🟠 : Attention prioritaire
- **Medium** 🟡 : À surveiller
- **Low** 🔵 : Information

#### États d'Alerte
- **Active** : Nouvelle alerte, action requise
- **Acquittée** : Prise en compte, en cours de traitement
- **Résolue** : Problème corrigé
- **Ignorée** : Alerte non pertinente

#### Utilisation
```jsx
import AlertsPanel from '../components/AlertsPanel'

<AlertsPanel 
  showOnlyActive={true}
  maxAlerts={5}
/>
```

#### Props
- `showOnlyActive`: Afficher uniquement les alertes actives (default: false)
- `maxAlerts`: Nombre maximum d'alertes affichées (default: 5)

#### Actions Disponibles
- **Acquitter** : Marquer l'alerte comme vue/en cours
- **Résoudre** : Marquer le problème comme corrigé
- **Voir Détails** : Modal avec contexte complet (seuils, données)

---

### 4. **DrillDownModal - Navigation Hiérarchique** ✅

#### Fonctionnalités
- Navigation hiérarchique (breadcrumb)
- Tableau paginé (10 lignes par page)
- Statistiques de résumé (total lignes, totaux)
- Formatage automatique (currency, date, status, link)
- Recherche et tri (à venir)

#### Utilisation
```jsx
import DrillDownModal from '../components/DrillDownModal'

const [showModal, setShowModal] = useState(false)
const [detailData, setDetailData] = useState([])

// Données exemple
const data = [
  { id: 1, client: 'Entreprise A', montant: 1500000, date: '2025-01-15', status: 'Payé' },
  { id: 2, client: 'Entreprise B', montant: 800000, date: '2025-02-20', status: 'En attente' },
]

// Définition des colonnes
const columns = [
  { key: 'id', label: 'ID', type: 'number' },
  { key: 'client', label: 'Client', type: 'text' },
  { key: 'montant', label: 'Montant', type: 'currency' },
  { key: 'date', label: 'Date', type: 'date' },
  { key: 'status', label: 'Statut', type: 'status' },
]

// Breadcrumb (fil d'Ariane)
const breadcrumb = ['Tableau de Bord', 'Financier', 'Zone Yopougon']

// Ouverture du modal (ex: au clic sur un graphique)
<BarChart onClick={() => {
  setDetailData(data)
  setShowModal(true)
}}>
  {/* ... */}
</BarChart>

// Modal
<DrillDownModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  title="Détails des Factures - Zone Yopougon"
  data={detailData}
  columns={columns}
  breadcrumb={breadcrumb}
/>
```

#### Types de Colonnes
- `text` : Texte simple
- `number` : Nombre formaté (K, M)
- `currency` : Montant en FCFA
- `date` : Date formatée (jj/mm/aaaa)
- `status` : Badge coloré selon statut
- `link` : Lien cliquable (prop `href` requise)

#### Exemple de Modal Généré
```
┌────────────────────────────────────────────┐
│ Détails des Factures - Zone Yopougon   ✕ │
│ Tableau de Bord > Financier > Zone Yop... │
├────────────────────────────────────────────┤
│ Stats: 45 lignes | Total: 12.5M F | P 1/5 │
├───┬─────────────┬──────────┬────────┬──────┤
│ID │ Client      │ Montant  │ Date   │Status│
├───┼─────────────┼──────────┼────────┼──────┤
│ 1 │Entreprise A │1,500,000F│15/01/25│ Payé │
│ 2 │Entreprise B │  800,000F│20/02/25│En att│
└───┴─────────────┴──────────┴────────┴──────┘
    Affichage 1-10 sur 45    < 1 2 3 4 5 >
```

---

## 🔧 Configuration Backend - Alertes

### 1. **Modèles Django**

#### Alert
```python
from analytics.models import Alert

# Créer une alerte manuellement
Alert.objects.create(
    alert_type='taux_recouvrement',
    severity='high',
    title="Taux de recouvrement faible",
    message="Le taux est de 45%, en dessous du seuil de 60%",
    threshold_value=60,
    actual_value=45,
    context_data={'zone': 'Yopougon', 'mois': 11}
)
```

#### AlertThreshold
```python
from analytics.models import AlertThreshold

# Configurer un seuil d'alerte
AlertThreshold.objects.create(
    alert_type='taux_recouvrement',
    is_active=True,
    threshold_value=60,
    threshold_operator='<',
    check_interval=60,  # minutes
    send_email=True,
    email_recipients='admin@sigeti.ci,direction@sigeti.ci'
)
```

### 2. **API Endpoints**

#### GET /api/alerts/
Liste toutes les alertes (filtrable par status, severity, type)

#### GET /api/alerts/active/
Alertes actives uniquement

#### POST /api/alerts/{id}/acknowledge/
Acquitter une alerte

#### POST /api/alerts/{id}/resolve/
Résoudre une alerte

#### POST /api/alerts/check_thresholds/
Vérifier tous les seuils et créer alertes si nécessaire

**Exemple de réponse:**
```json
{
  "id": 1,
  "alert_type": "taux_recouvrement",
  "severity": "high",
  "severity_display": "Élevé",
  "status": "active",
  "title": "Taux de recouvrement critique: 45.0%",
  "message": "Le taux de recouvrement moyen (45.0%) est en dessous du seuil de 60%. Action immédiate requise.",
  "threshold_value": "60.00",
  "actual_value": "45.00",
  "context_data": {
    "annee": 2025,
    "mois": 11,
    "zone": "Yopougon"
  },
  "created_at": "2025-11-13T10:30:00Z"
}
```

### 3. **Vérification Automatique (Scheduler)**

Pour une vérification automatique régulière, configurer un cron job ou Celery:

```bash
# Cron (chaque heure)
0 * * * * cd /path/to/bi_app/backend && python manage.py shell -c "import requests; requests.post('http://localhost:8000/api/alerts/check_thresholds/', headers={'Authorization': 'Token YOUR_TOKEN'})"
```

Ou avec Django management command (à créer):
```bash
python manage.py check_alert_thresholds
```

---

## 📊 Intégration Complète - Exemple Dashboard

```jsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import FilterBar from '../components/FilterBar'
import ExportButton from '../components/ExportButton'
import AlertsPanel from '../components/AlertsPanel'
import DrillDownModal from '../components/DrillDownModal'
import { financierAPI } from '../services/api'

export default function FinancierDashboard() {
  const [filters, setFilters] = useState({})
  const [drillDown, setDrillDown] = useState({ open: false, data: [], title: '' })

  const { data } = useQuery({
    queryKey: ['financier', filters],
    queryFn: () => financierAPI.getData(filters).then(res => res.data)
  })

  return (
    <div className="space-y-6">
      {/* Filtres */}
      <FilterBar 
        onFilterChange={setFilters}
        showComparison={true}
      />

      {/* Header avec Export */}
      <div className="flex justify-between">
        <h1>Dashboard Financier</h1>
        <ExportButton 
          data={data}
          filename="financier"
          title="Rapport Financier"
        />
      </div>

      {/* Alertes */}
      <AlertsPanel showOnlyActive={true} maxAlerts={3} />

      {/* Graphiques avec Drill-Down */}
      <BarChart 
        data={data}
        onClick={(item) => {
          setDrillDown({
            open: true,
            data: item.details,
            title: `Détails ${item.label}`
          })
        }}
      />

      {/* Modal Drill-Down */}
      <DrillDownModal
        isOpen={drillDown.open}
        onClose={() => setDrillDown({ ...drillDown, open: false })}
        title={drillDown.title}
        data={drillDown.data}
        columns={[
          { key: 'facture_id', label: 'N° Facture', type: 'text' },
          { key: 'montant', label: 'Montant', type: 'currency' },
          { key: 'date', label: 'Date', type: 'date' },
          { key: 'status', label: 'Statut', type: 'status' },
        ]}
      />
    </div>
  )
}
```

---

## 🚀 Prochaines Étapes

### Installation
```bash
# Dépendances déjà installées
cd bi_app/frontend
npm install xlsx jspdf jspdf-autotable

# Migrations backend déjà appliquées
cd bi_app/backend
python manage.py makemigrations analytics
python manage.py migrate analytics
```

### Utilisation Immédiate
1. ✅ Redémarrer le serveur backend : `python manage.py runserver`
2. ✅ Redémarrer le serveur frontend : `npm run dev`
3. ✅ Accéder au Dashboard : `http://localhost:5173`
4. ✅ Tester les filtres, exports et alertes

### Configuration Initiale Alertes
```bash
# Django shell
python manage.py shell

# Créer des seuils d'alerte
from analytics.models import AlertThreshold

AlertThreshold.objects.create(
    alert_type='taux_recouvrement',
    threshold_value=60,
    threshold_operator='<',
    is_active=True
)

# Vérifier les seuils (créer alertes)
import requests
requests.post('http://localhost:8000/api/alerts/check_thresholds/')
```

---

## 📖 Documentation API

### Alertes

#### Liste des alertes
```http
GET /api/alerts/
GET /api/alerts/active/
GET /api/alerts/?status=active&severity=high
```

#### Actions sur alertes
```http
POST /api/alerts/{id}/acknowledge/
POST /api/alerts/{id}/resolve/
POST /api/alerts/check_thresholds/
```

#### Gestion des seuils
```http
GET /api/alert-thresholds/
POST /api/alert-thresholds/
PUT /api/alert-thresholds/{id}/
POST /api/alert-thresholds/{id}/toggle/
```

---

## 🎨 Personnalisation

### Couleurs des Alertes
Modifier dans `AlertsPanel.jsx` :
```jsx
const getSeverityConfig = (severity) => {
  return {
    critical: { color: 'red', icon: AlertTriangle },
    high: { color: 'orange', icon: AlertCircle },
    // ...
  }
}
```

### Périodes Prédéfinies
Modifier dans `FilterBar.jsx` :
```jsx
const periodePresets = [
  { value: 'custom_q1', label: 'Q1 2025' },
  // Ajouter vos périodes
]
```

---

**Documentation créée le 13/11/2025**  
**Version SIGETI BI v1.0 - Priorité 1 Fonctionnalités Essentielles**
