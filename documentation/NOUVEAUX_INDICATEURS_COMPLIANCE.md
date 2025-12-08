# 📊 Nouveaux Indicateurs Compliance - Phase 1

## Date: 30 Novembre 2025
## Objectif: Enrichissement des dashboards Compliance avec dimensions entreprise

---

## 🎯 Résumé des Améliorations

Les marts de compliance ont été enrichis avec 4 nouvelles dimensions critiques permettant des analyses plus fines:

- ✅ **raison_sociale** - Nom de l'entreprise
- ✅ **forme_juridique** - Type juridique (SARL, EURL, etc.)
- ✅ **libelle_domaine** - Domaine d'activité détaillé
- ✅ **categorie_domaine** - Catégorie agrégée (INDUSTRIE, SERVICES, TECH, AGRICULTURE, BTP, AUTRE)

---

## 📡 Nouveaux Endpoints API

### 1. Conventions par Domaine d'Activité

#### Domaines Détaillés
```http
GET /api/compliance-compliance/conventions_by_domaine/?annee=2025
```

**Response Example:**
```json
[
  {
    "categorie_domaine": "INDUSTRIE",
    "libelle_domaine": "Fabrication de matériaux composites",
    "records_count": 15,
    "total_conventions": 45,
    "conventions_approved": 38,
    "conventions_rejected": 5,
    "avg_validation_pct": 84.44,
    "avg_rejection_pct": 11.11,
    "avg_processing_days": 12.5
  }
]
```

#### Catégories Agrégées
```http
GET /api/compliance-compliance/conventions_by_categorie_domaine/?annee=2025
```

**Response Example:**
```json
[
  {
    "categorie_domaine": "INDUSTRIE",
    "records_count": 25,
    "total_conventions": 120,
    "conventions_approved": 105,
    "conventions_rejected": 10,
    "conventions_in_progress": 5,
    "avg_validation_pct": 87.5,
    "avg_rejection_pct": 8.33,
    "avg_processing_days": 10.2,
    "max_processing_days": 45.0
  }
]
```

---

### 2. Conventions par Forme Juridique

```http
GET /api/compliance-compliance/conventions_by_forme_juridique/?annee=2025
```

**Response Example:**
```json
[
  {
    "forme_juridique": "SARL",
    "records_count": 35,
    "total_conventions": 150,
    "conventions_approved": 130,
    "conventions_rejected": 15,
    "conventions_in_progress": 5,
    "avg_validation_pct": 86.67,
    "avg_rejection_pct": 10.0,
    "avg_processing_days": 11.3
  },
  {
    "forme_juridique": "EURL",
    "records_count": 20,
    "total_conventions": 80,
    "conventions_approved": 70,
    "conventions_rejected": 8,
    "conventions_in_progress": 2,
    "avg_validation_pct": 87.5,
    "avg_rejection_pct": 10.0,
    "avg_processing_days": 9.8
  }
]
```

---

### 3. Conventions par Entreprise

```http
GET /api/compliance-compliance/conventions_by_entreprise/?annee=2025&limit=50
```

**Query Parameters:**
- `annee` (optional): Année de filtrage (défaut: année courante)
- `limit` (optional): Nombre max d'entreprises (défaut: 50)

**Response Example:**
```json
[
  {
    "raison_sociale": "ACME Industries SARL",
    "forme_juridique": "SARL",
    "categorie_domaine": "INDUSTRIE",
    "records_count": 8,
    "total_conventions": 25,
    "conventions_approved": 22,
    "conventions_rejected": 2,
    "conventions_in_progress": 1,
    "avg_validation_pct": 88.0,
    "avg_processing_days": 8.5
  }
]
```

---

### 4. Délais d'Approbation par Domaine

```http
GET /api/compliance-compliance/approval_delays_by_domaine/?annee=2025
```

**Response Example:**
```json
[
  {
    "categorie_domaine": "SERVICES",
    "libelle_domaine": "Services informatiques",
    "records_count": 12,
    "total_conventions": 35,
    "avg_approval_days": 9.5,
    "median_approval_days": 8.0,
    "max_approval_days": 28.0,
    "avg_waiting_days": 2.3
  }
]
```

---

### 5. Délais d'Approbation par Forme Juridique

```http
GET /api/compliance-compliance/approval_delays_by_forme_juridique/?annee=2025
```

**Response Example:**
```json
[
  {
    "forme_juridique": "SARL",
    "records_count": 40,
    "total_conventions": 180,
    "avg_approval_days": 10.2,
    "median_approval_days": 9.0,
    "max_approval_days": 45.0,
    "avg_waiting_days": 2.5
  }
]
```

---

## 📊 Cas d'Usage - Visualisations Suggérées

### Dashboard 1: Performance par Secteur

```javascript
// Exemple React/Chart.js
import { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';

function SectorPerformanceChart() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/compliance-compliance/conventions_by_categorie_domaine/?annee=2025')
      .then(res => res.json())
      .then(data => {
        setData({
          labels: data.map(d => d.categorie_domaine),
          datasets: [
            {
              label: 'Taux de Validation (%)',
              data: data.map(d => d.avg_validation_pct),
              backgroundColor: 'rgba(75, 192, 192, 0.6)'
            },
            {
              label: 'Taux de Rejet (%)',
              data: data.map(d => d.avg_rejection_pct),
              backgroundColor: 'rgba(255, 99, 132, 0.6)'
            }
          ]
        });
      });
  }, []);
  
  return data ? <Bar data={data} /> : <p>Chargement...</p>;
}
```

---

### Dashboard 2: Délais par Forme Juridique

```javascript
// Heatmap délais par forme juridique
function DelaysHeatmap() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/compliance-compliance/approval_delays_by_forme_juridique/?annee=2025')
      .then(res => res.json())
      .then(setData);
  }, []);
  
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Forme Juridique</th>
          <th>Délai Moyen</th>
          <th>Délai Médian</th>
          <th>Délai Max</th>
        </tr>
      </thead>
      <tbody>
        {data.map(row => (
          <tr key={row.forme_juridique}>
            <td>{row.forme_juridique}</td>
            <td className={getColorClass(row.avg_approval_days)}>
              {row.avg_approval_days} jours
            </td>
            <td>{row.median_approval_days} jours</td>
            <td>{row.max_approval_days} jours</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function getColorClass(days) {
  if (days <= 5) return 'bg-success';
  if (days <= 10) return 'bg-warning';
  return 'bg-danger';
}
```

---

### Dashboard 3: Top Entreprises

```javascript
// Tableau des top entreprises
function TopEnterprisesTable() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/compliance-compliance/conventions_by_entreprise/?annee=2025&limit=20')
      .then(res => res.json())
      .then(setData);
  }, []);
  
  return (
    <div className="table-responsive">
      <table className="table table-striped">
        <thead>
          <tr>
            <th>Entreprise</th>
            <th>Forme Juridique</th>
            <th>Secteur</th>
            <th>Conventions</th>
            <th>Validées</th>
            <th>Taux Validation</th>
            <th>Délai Moyen</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              <td>{row.raison_sociale}</td>
              <td><span className="badge">{row.forme_juridique}</span></td>
              <td><span className="badge badge-info">{row.categorie_domaine}</span></td>
              <td>{row.total_conventions}</td>
              <td>{row.conventions_approved}</td>
              <td>
                <span className={`badge ${row.avg_validation_pct > 80 ? 'badge-success' : 'badge-warning'}`}>
                  {row.avg_validation_pct}%
                </span>
              </td>
              <td>{row.avg_processing_days} j</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 🔄 Migration Frontend

### Étape 1: Mettre à jour les appels API existants

Les endpoints existants continuent de fonctionner normalement. Aucune modification requise.

### Étape 2: Ajouter les nouveaux widgets

Créer de nouveaux composants pour exploiter les dimensions entreprise:
- Widget "Performance par Secteur"
- Widget "Délais par Forme Juridique"
- Widget "Top Entreprises"

### Étape 3: Enrichir les dashboards existants

Ajouter des filtres supplémentaires:
```javascript
<select onChange={e => setCategorieDomaine(e.target.value)}>
  <option value="">Tous les secteurs</option>
  <option value="INDUSTRIE">Industrie</option>
  <option value="SERVICES">Services</option>
  <option value="TECH">Technologie</option>
  <option value="AGRICULTURE">Agriculture</option>
  <option value="BTP">BTP</option>
  <option value="AUTRE">Autre</option>
</select>
```

---

## ⚠️ Notes Importantes

### Limitations Phase 1

Les colonnes suivantes n'ont **pas** pu être ajoutées car absentes de la table source:
- ❌ `montant_convention` - Nécessite ALTER TABLE
- ❌ `date_limite_reponse` - Nécessite ALTER TABLE
- ❌ `raison_rejet` - Nécessite ALTER TABLE
- ❌ `approuve_par` - Nécessite ALTER TABLE
- ❌ `entreprise_id` (FK vers entreprises) - Nécessite modèle relationnel
- ❌ `zone_industrielle_id` (FK vers zones) - Nécessite modèle relationnel

### Prochaines Phases

**Phase 2** (si colonnes ajoutées au backend):
- Segmentation par tranche de montant
- Analyse % respect SLA (délais réglementaires)
- Corrélation montant vs taux de validation
- Analyse causes de rejet
- Analyse géographique par zone industrielle

---

## 🧪 Tests

Pour tester les nouveaux endpoints:

```bash
cd bi_app/backend
python test_new_compliance_endpoints.py
```

Ou via curl:
```bash
curl "http://localhost:8000/api/compliance-compliance/conventions_by_domaine/?annee=2025"
curl "http://localhost:8000/api/compliance-compliance/conventions_by_forme_juridique/?annee=2025"
```

---

## 📞 Support

Pour toute question ou support:
- **Documentation technique**: `/docs/COMPLIANCE_DASHBOARD.md`
- **Analyse initiale**: `/ANALYSE_DIMENSIONS_COMPLIANCE.md`
- **Code backend**: `/bi_app/backend/api/compliance_compliance_views.py`
- **Modèles dbt**: `/models/marts/compliance/`

---

**Dernière mise à jour**: 30 Novembre 2025
