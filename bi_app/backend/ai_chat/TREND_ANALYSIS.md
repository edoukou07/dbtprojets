# 📈 Analyse de Tendances - Documentation

## Vue d'ensemble

L'analyse de tendances permet au chatbot de détecter automatiquement les évolutions temporelles dans les données et de générer des insights sur les variations, les prévisions et la saisonnalité.

---

## 🎯 Fonctionnalités

### 1. **Détection Automatique**
- ✅ Détecte automatiquement les données temporelles (mois, année, trimestre)
- ✅ Identifie les champs numériques pertinents
- ✅ Analyse simple (série temporelle unique) ou groupée (par zone, client, etc.)

### 2. **Métriques Calculées**

#### Tendances Simples
- **Variation totale** : Évolution du début à la fin (%)
- **Variation moyenne** : Variation moyenne entre périodes consécutives (%)
- **Prévision** : Estimation de la prochaine période (moyenne mobile + tendance)
- **Volatilité** : Stabilité de la série (faible/modérée/élevée)
- **Points remarquables** : Valeurs min/max et leurs périodes

#### Tendances Groupées
- **Top 5 en hausse** : Entités avec meilleures progressions
- **Top 5 en baisse** : Entités avec plus fortes baisses
- **Variation moyenne globale** : Tendance d'ensemble
- **Distribution** : % d'entités en hausse/stable/baisse

### 3. **Détection de Saisonnalité**
- Analyse cyclique sur 12 mois
- Identification des mois forts et faibles
- Coefficient de variation saisonnier

### 4. **Classification des Tendances**

| Tendance | Variation Moyenne | Emoji | Couleur |
|----------|-------------------|-------|---------|
| Forte hausse | > +20% | 📈 | Vert foncé |
| Hausse | +5% à +20% | 📊 | Vert clair |
| Stable | -5% à +5% | ➡️ | Gris |
| Baisse | -20% à -5% | 📉 | Orange |
| Forte baisse | < -20% | 🔴 | Rouge |

---

## 🔍 Questions Supportées

### Tendances Simples
```
✅ "Tendance du CA"
✅ "Évolution du CA par mois"
✅ "Progression du CA en 2024"
✅ "Croissance du CA"
```

### Comparaisons
```
✅ "Comparer le CA entre les années"
✅ "Comparer avec le mois précédent"
✅ "CA 2024 vs 2025"
✅ "Différence entre 2024 et 2025"
```

### Tendances Groupées
```
✅ "Évolution par zone"
✅ "Tendance zones"
✅ "Progression zones"
✅ "Zones en croissance"
✅ "Zones en baisse"
```

---

## 💻 Architecture Technique

### 1. Module `trend_analysis.py`

#### Classe `TrendAnalyzer`
```python
class TrendAnalyzer:
    # Analyse une série temporelle
    analyze_time_series(data, time_field, value_field, entity_field=None)
    
    # Compare deux périodes spécifiques
    compare_periods(data, period_field, value_field, period1, period2)
```

#### Méthodes Internes
- `_analyze_single_trend()` : Analyse simple
- `_analyze_grouped_trends()` : Analyse groupée
- `_calculate_variation()` : Calcul de variation %
- `_calculate_average_variation()` : Variation moyenne
- `_classify_trend()` : Classification selon seuils
- `_detect_seasonality()` : Détection saisonnalité
- `_simple_forecast()` : Prévision par moyenne mobile
- `_calculate_volatility()` : Calcul volatilité
- `_generate_trend_insights()` : Génération insights
- `_generate_comparative_insights()` : Insights comparatifs

### 2. Intégration dans `chat_service.py`

```python
def __init__(self, query_engine):
    self.trend_analyzer = TrendAnalyzer()

def _analyze_trends_if_temporal(self, data, columns, category):
    # Détecte champs temporels
    # Détecte champs numériques
    # Lance analyse appropriée
    # Retourne résultat enrichi
```

### 3. Patterns dans `query_engine.py`

Nouveaux patterns ajoutés :
```python
QueryPattern(
    patterns=[
        "tendance", "évolution", "progression", "croissance",
        "tendance ca", "évolution ca"
    ],
    sql_template="""
        SELECT mois, 
               SUM(montant_total_facture) as ca_total
        FROM dwh_marts_financier.mart_performance_financiere
        WHERE annee = {annee}
        GROUP BY mois
        ORDER BY mois
    """,
    category="financier"
),
```

### 4. Affichage Frontend `ChatBot.jsx`

Composant d'analyse de tendances avec :
- Badge de tendance coloré
- Grille de métriques (4 KPIs)
- Top 5 hausse/baisse (si groupé)
- Liste d'insights
- Indicateur de saisonnalité

---

## 📊 Format de Réponse

### Tendance Simple
```json
{
  "trend_analysis": {
    "tendance": "hausse",
    "variation_totale_pct": 15.5,
    "variation_moyenne_pct": 2.3,
    "nb_periodes": 12,
    "valeur_initiale": 1000000,
    "valeur_finale": 1155000,
    "valeur_max": 1200000,
    "valeur_min": 950000,
    "periode_max": 11,
    "periode_min": 3,
    "moyenne": 1075000,
    "ecart_type": 85000,
    "prevision_prochaine_periode": 1180000,
    "volatilite": "modérée",
    "saisonnalite": {
      "detectee": true,
      "mois_fort": 11,
      "mois_faible": 3,
      "coefficient_variation": 18.5
    },
    "insights": [
      "📈 Tendance positive avec une progression de 15.5%.",
      "📅 Saisonnalité détectée : pic au mois 11, creux au mois 3",
      "✅ Volatilité faible - Performance stable et prévisible"
    ]
  }
}
```

### Tendance Groupée
```json
{
  "trend_analysis": {
    "nb_entites": 15,
    "variation_moyenne_globale": 8.2,
    "top_5_hausse": [
      {"entite": "Zone A", "variation_pct": 25.3, "tendance": "forte_hausse"},
      {"entite": "Zone B", "variation_pct": 18.7, "tendance": "hausse"}
    ],
    "top_5_baisse": [
      {"entite": "Zone X", "variation_pct": -15.2, "tendance": "baisse"}
    ],
    "insights": [
      "🏆 Meilleure performance : Zone A (+25.3%)",
      "⚠️ Performance la plus faible : Zone X (-15.2%)",
      "📊 Écart de performance : 40.5 points de pourcentage",
      "📈 67% des entités sont en hausse"
    ]
  }
}
```

---

## 🧪 Tests

### Script de Test
```bash
python test_trends.py
```

Tests inclus :
1. ✅ Évolution mensuelle CA 2024 (tendance simple)
2. ✅ Évolution CA par zone 2024 (tendances groupées)
3. ✅ Comparaison annuelle CA

### Résultats Attendus
- Détection automatique des champs temporels
- Calcul des variations
- Classification de tendance
- Génération d'insights
- Prévisions

---

## 🎨 Interface Utilisateur

### Affichage

**Encadré violet/bleu dégradé** avec :

1. **En-tête** : "📈 Analyse de Tendance"

2. **Badge de tendance** : 
   - Forte hausse : Vert foncé
   - Hausse : Vert clair
   - Stable : Gris
   - Baisse : Orange
   - Forte baisse : Rouge

3. **Grille 2x2 de métriques** :
   - Variation totale
   - Variation moyenne
   - Prévision
   - Volatilité

4. **Insights** (liste à puces)

5. **Saisonnalité** (si détectée, encadré violet)

6. **Top 5 hausse/baisse** (si groupé)
   - Encadré vert pour hausses
   - Encadré rouge pour baisses

---

## 🔧 Configuration

### Seuils de Classification
```python
SEUILS_VARIATION = {
    'forte_hausse': 20.0,      # > +20%
    'hausse': 5.0,             # > +5%
    'stable': -5.0,            # entre -5% et +5%
    'baisse': -20.0,           # < -5%
    'forte_baisse': -100.0     # < -20%
}
```

### Détection de Saisonnalité
- **Minimum** : 12 périodes (1 an)
- **Seuil CV** : 15% (coefficient de variation)
- **Cycle** : 12 mois (annuel)

### Prévision
- **Méthode** : Moyenne mobile (3 dernières périodes)
- **Ajustement** : Tendance récente appliquée
- **Contrainte** : Valeurs >= 0 uniquement

---

## 💡 Cas d'Usage

### 1. Analyse Performance Mensuelle
**Question** : "Évolution du CA par mois en 2024"

**Résultat** :
- Tendance : Hausse (+12.5%)
- Prévision mois prochain : 850M FCFA
- Insight : "Saisonnalité détectée avec pic en novembre"

### 2. Comparaison Zones
**Question** : "Évolution du CA par zone"

**Résultat** :
- Top 5 en hausse : Zone Industrielle (+28%), Zone Nord (+22%)
- Top 5 en baisse : Zone Sud (-8%)
- Insight : "60% des zones en croissance"

### 3. Analyse Annuelle
**Question** : "Comparer le CA 2023 vs 2024"

**Résultat** :
- Variation : +18.7%
- Tendance : Forte hausse
- Insight : "Excellente performance ! Croissance de 18.7%"

---

## 📈 Améliorations Futures

### Court Terme
- [ ] Support de plus de champs temporels (semaine, trimestre)
- [ ] Comparaison période N vs N-1 automatique
- [ ] Détection de ruptures (changements brusques)

### Moyen Terme
- [ ] Prévisions avancées (régression linéaire, ARIMA)
- [ ] Détection d'outliers temporels
- [ ] Analyse de corrélations entre séries

### Long Terme
- [ ] Machine Learning pour prévisions
- [ ] Détection automatique d'événements (pics, creux)
- [ ] Recommandations d'actions basées sur tendances

---

## 🐛 Dépannage

### Problème : "Aucune analyse de tendance disponible"

**Causes** :
1. Moins de 2 points de données
2. Aucun champ temporel détecté
3. Aucun champ numérique trouvé

**Solutions** :
1. Vérifier que la requête retourne plusieurs lignes
2. S'assurer qu'il y a un champ mois/annee/date
3. Vérifier que les valeurs numériques existent

### Problème : Saisonnalité non détectée

**Causes** :
1. Moins de 12 périodes
2. Coefficient de variation < 15%

**Solutions** :
1. Requêter au moins 1 an de données
2. Les variations peuvent être trop faibles

---

## 📚 Références

### Code Source
- `bi_app/backend/ai_chat/trend_analysis.py` - Module principal
- `bi_app/backend/ai_chat/chat_service.py` - Intégration
- `bi_app/backend/ai_chat/query_engine.py` - Patterns SQL
- `bi_app/frontend/src/components/ChatBot.jsx` - Interface

### Tests
- `bi_app/backend/test_trends.py` - Tests complets
- `bi_app/backend/test_trend_quick.py` - Test rapide

### Documentation
- `TREND_ANALYSIS.md` - Ce fichier
- `NLP_IMPROVEMENTS.md` - Améliorations NLP

---

**Version** : 1.0  
**Date** : 16 novembre 2025  
**Auteur** : AI Assistant  
**Statut** : ✅ Implémenté et testé
