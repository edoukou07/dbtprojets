# 📊 SIGETI BI - Business Intelligence Application

Application de Business Intelligence développée avec Django (backend) et React (frontend) pour visualiser les données du Data Warehouse SIGETI.

## 🏗️ Architecture

```
SIGETI BI Application
├── Backend (Django + Django REST Framework)
│   ├── API REST pour 4 marts
│   ├── Connexion PostgreSQL au DWH
│   └── Endpoints avec filtres et agrégations
│
└── Frontend (React + Vite + Tailwind CSS)
    ├── 5 pages (Accueil + 4 dashboards)
    ├── Graphiques interactifs (Recharts)
    └── Design moderne et responsive
```

---

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.12+ avec venv activé
- Node.js 18+ et npm
- PostgreSQL avec DWH SIGETI
- PowerShell 5.1+

### Installation (Première fois uniquement)

```powershell
# Depuis la racine du projet (DWH_SIG/)
cd bi_app
.\setup.ps1
```

Ce script va :
1. ✅ Installer les dépendances Django (requirements.txt)
2. ✅ Installer les dépendances React (npm install)

**Durée estimée** : 3-5 minutes

### Démarrage de l'application

```powershell
# Depuis la racine du projet (DWH_SIG/)
.\bi_app\start.ps1
```

Ce script va ouvrir 2 fenêtres PowerShell :
- **Backend Django** : http://localhost:8000
- **Frontend React** : http://localhost:5173

**Accès** : Ouvrez votre navigateur sur http://localhost:5173

---

## 📁 Structure du Projet

```
bi_app/
├── backend/                    # Backend Django
│   ├── sigeti_bi/             # Configuration Django
│   │   ├── settings.py        # Paramètres (DB, CORS, REST Framework)
│   │   ├── urls.py            # Routes principales
│   │   └── wsgi.py            # WSGI pour production
│   │
│   ├── analytics/             # App modèles DWH
│   │   ├── models.py          # Models mappant les marts
│   │   └── apps.py
│   │
│   ├── api/                   # App API REST
│   │   ├── views.py           # ViewSets et endpoints
│   │   ├── serializers.py     # Sérialiseurs DRF
│   │   └── urls.py            # Routes API
│   │
│   ├── manage.py              # CLI Django
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── pages/             # Pages principales
│   │   │   ├── Dashboard.jsx  # Accueil (vue d'ensemble)
│   │   │   ├── Financier.jsx  # Dashboard financier
│   │   │   ├── Occupation.jsx # Dashboard occupation
│   │   │   ├── Clients.jsx    # Dashboard clients
│   │   │   └── Operationnel.jsx # Dashboard opérationnel
│   │   │
│   │   ├── components/
│   │   │   └── Layout.jsx     # Layout + navigation
│   │   │
│   │   ├── services/
│   │   │   └── api.js         # Client API (axios)
│   │   │
│   │   ├── App.jsx            # Composant principal
│   │   ├── main.jsx           # Point d'entrée
│   │   └── index.css          # Styles Tailwind
│   │
│   ├── package.json           # Dépendances npm
│   ├── vite.config.js         # Configuration Vite
│   └── tailwind.config.js     # Configuration Tailwind
│
├── setup.ps1                  # Script d'installation
├── start.ps1                  # Script de démarrage
└── README.md                  # Ce fichier
```

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Endpoints Disponibles

#### 1. **Mart Financier** (`/api/financier/`)

```http
GET /api/financier/              # Liste des données financières
GET /api/financier/summary/      # Résumé financier (agrégations)
GET /api/financier/by_zone/      # Données par zone

# Filtres disponibles
?annee=2025                      # Filtrer par année
?mois=6                          # Filtrer par mois
?trimestre=2                     # Filtrer par trimestre
?nom_zone=Zone+A                 # Filtrer par zone
```

**Exemple de réponse (summary)** :
```json
{
  "total_factures": 1234,
  "ca_total": 45000000,
  "ca_paye": 38000000,
  "ca_impaye": 7000000,
  "taux_paiement_moyen": 84.5,
  "total_collectes": 56,
  "montant_recouvre": 32000000
}
```

#### 2. **Mart Occupation** (`/api/occupation/`)

```http
GET /api/occupation/             # Liste des zones
GET /api/occupation/summary/     # Résumé occupation

# Filtres disponibles
?nom_zone=Zone+A                 # Filtrer par zone
```

**Exemple de réponse (summary)** :
```json
{
  "total_lots": 450,
  "lots_disponibles": 120,
  "lots_attribues": 300,
  "superficie_totale": 125000,
  "taux_occupation_moyen": 66.7,
  "valeur_totale": 150000000
}
```

#### 3. **Mart Clients** (`/api/clients/`)

```http
GET /api/clients/                # Liste des clients
GET /api/clients/summary/        # Résumé portefeuille
GET /api/clients/top_clients/    # Top 10 clients
GET /api/clients/at_risk/        # Clients à risque

# Filtres disponibles
?segment_client=Grand+client     # Filtrer par segment
?niveau_risque=Risque+élevé      # Filtrer par risque
?search=Entreprise               # Recherche par nom
```

**Exemple de réponse (summary)** :
```json
{
  "total_clients": 245,
  "ca_total": 45000000,
  "ca_paye": 38000000,
  "ca_impaye": 7000000,
  "taux_paiement_moyen": 84.5,
  "segmentation": [
    {"segment_client": "Grand client", "count": 12, "ca_total": 25000000},
    {"segment_client": "Client moyen", "count": 78, "ca_total": 18000000},
    {"segment_client": "Petit client", "count": 155, "ca_total": 2000000}
  ]
}
```

#### 4. **Mart Opérationnel** (`/api/operationnel/`)

```http
GET /api/operationnel/           # Liste des KPIs
GET /api/operationnel/summary/   # Résumé opérationnel
GET /api/operationnel/trends/    # Tendances mensuelles

# Filtres disponibles
?annee=2025                      # Filtrer par année
?trimestre=2                     # Filtrer par trimestre
```

**Exemple de réponse (summary)** :
```json
{
  "total_collectes": 56,
  "taux_cloture_moyen": 78.5,
  "taux_recouvrement_moyen": 82.3,
  "total_demandes": 345,
  "total_approuvees": 298,
  "taux_approbation_moyen": 86.4,
  "total_factures": 1234,
  "total_payees": 1042
}
```

---

## 🎨 Pages Frontend

### 1. **Accueil** (`/`)
Vue d'ensemble avec 16 KPIs principaux :
- Performance financière (4 KPIs)
- Occupation des zones (4 KPIs)
- Portefeuille clients (4 KPIs)
- Performance opérationnelle (4 KPIs)

### 2. **Dashboard Financier** (`/financier`)
- KPIs : CA facturé, CA payé, Créances, Taux de paiement
- Graphique : Évolution mensuelle CA
- Graphique : Performance par zone
- Filtres : Année

### 3. **Dashboard Occupation** (`/occupation`)
- En développement (placeholder créé)
- KPIs : Lots totaux, disponibles, attribués, taux d'occupation
- Graphiques prévus : Carte des zones, distribution des lots

### 4. **Dashboard Clients** (`/clients`)
- En développement (placeholder créé)
- KPIs : Total clients, CA, créances, segmentation
- Graphiques prévus : Top clients, clients à risque

### 5. **Dashboard Opérationnel** (`/operationnel`)
- En développement (placeholder créé)
- KPIs : Collectes, attributions, facturation
- Graphiques prévus : Tendances mensuelles, efficacité

---

## ⚙️ Configuration

### Backend (Django)

**Fichier** : `backend/sigeti_bi/settings.py`

```python
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sigeti_node_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# CORS (autoriser React)
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite dev server
]
```

**Variables d'environnement** (.env) :
```env
DWH_DB_NAME=sigeti_node_db
DWH_DB_USER=postgres
DWH_DB_PASSWORD=postgres
DWH_DB_HOST=localhost
DWH_DB_PORT=5432
```

### Frontend (React)

**Fichier** : `frontend/vite.config.js`

```javascript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',  // Proxy vers Django
    },
  },
})
```

**API Client** : `frontend/src/services/api.js`

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

---

## 🔧 Développement

### Commandes Utiles

#### Backend Django

```powershell
# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Lancer le serveur
cd bi_app\backend
python manage.py runserver

# Créer un superuser (admin)
python manage.py createsuperuser

# Migrations (si nécessaire)
python manage.py makemigrations
python manage.py migrate

# Shell Django
python manage.py shell
```

#### Frontend React

```powershell
# Lancer le dev server
cd bi_app\frontend
npm run dev

# Build pour production
npm run build

# Preview du build
npm run preview

# Installer une nouvelle dépendance
npm install nom-du-package
```

### Ajouter un Nouveau Dashboard

1. **Créer la page React** :
```javascript
// frontend/src/pages/NouveauDashboard.jsx
export default function NouveauDashboard() {
  return <div>Mon dashboard</div>
}
```

2. **Ajouter la route** :
```javascript
// frontend/src/App.jsx
<Route path="/nouveau" element={<NouveauDashboard />} />
```

3. **Ajouter au menu** :
```javascript
// frontend/src/components/Layout.jsx
{ name: 'Nouveau', path: '/nouveau', icon: Icon }
```

### Ajouter un Nouvel Endpoint API

1. **Créer la vue** :
```python
# backend/api/views.py
class NouveauViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MonModele.objects.all()
    serializer_class = MonSerializer
```

2. **Enregistrer la route** :
```python
# backend/api/urls.py
router.register(r'nouveau', NouveauViewSet)
```

---

## 🐛 Troubleshooting

### Erreur: "Module not found: react"

**Solution** :
```powershell
cd bi_app\frontend
npm install
```

### Erreur: "ModuleNotFoundError: No module named 'django'"

**Solution** :
```powershell
.\venv\Scripts\Activate.ps1
cd bi_app\backend
pip install -r requirements.txt
```

### Erreur: "Connection refused" (API)

**Solution** :
- Vérifier que Django tourne sur http://localhost:8000
- Vérifier que PostgreSQL est démarré
- Tester : `curl http://localhost:8000/api/financier/`

### Erreur: "CORS policy" dans le navigateur

**Solution** :
- Vérifier que `django-cors-headers` est installé
- Vérifier `CORS_ALLOWED_ORIGINS` dans `settings.py`
- Redémarrer Django

### Page blanche React

**Solution** :
- Ouvrir la console navigateur (F12)
- Vérifier les erreurs JavaScript
- Vérifier que l'API répond : http://localhost:8000/api/

---

## 📚 Technologies Utilisées

### Backend
- **Django 5.0** - Framework web Python
- **Django REST Framework 3.14** - API REST
- **psycopg2-binary** - Driver PostgreSQL
- **django-cors-headers** - Gestion CORS
- **pandas** - Manipulation de données (optionnel)

### Frontend
- **React 18.2** - Library UI
- **Vite 5.0** - Build tool ultra-rapide
- **React Router 6.20** - Routing
- **TanStack Query 5.14** - Gestion état serveur
- **Recharts 2.10** - Graphiques
- **Tailwind CSS 3.3** - Styling
- **Lucide React** - Icons
- **Axios 1.6** - Client HTTP

---

## 🚀 Déploiement Production

### Backend Django

```powershell
# Build static files
python manage.py collectstatic

# Run with Gunicorn (Linux)
gunicorn sigeti_bi.wsgi:application --bind 0.0.0.0:8000
```

### Frontend React

```powershell
# Build pour production
npm run build

# Les fichiers sont dans dist/
# Servir avec nginx, Apache, ou autre serveur web
```

### Docker (Optionnel)

Créer un `docker-compose.yml` :
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
```

---

## 📞 Support

**Équipe Data SIGETI**  
📧 support-data@sigeti.ci  
📅 Dernière mise à jour : 13 novembre 2025  
🔗 GitHub : https://github.com/edoukou07/dbtprojets

---

## 📝 Roadmap

- [ ] Compléter les dashboards Occupation, Clients, Opérationnel
- [ ] Ajouter l'authentification utilisateur
- [ ] Implémenter les exports Excel/PDF
- [ ] Ajouter des alertes en temps réel
- [ ] Créer des rapports personnalisables
- [ ] Intégrer des filtres avancés
- [ ] Ajouter le mode sombre
- [ ] Optimiser les performances (cache, pagination)
- [ ] Tests automatisés (backend + frontend)
- [ ] Documentation API avec Swagger

---

**Version** : 1.0.0  
**Statut** : ✅ En développement actif
