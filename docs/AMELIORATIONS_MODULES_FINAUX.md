# Plan d'Amélioration - Modules Avancés et Plan d'Implémentation

## 8. Nouveaux Modules

### 8.1 Module de Prévisions ML (Machine Learning)

```bash
pip install scikit-learn pandas numpy joblib
```

```python
# bi_app/backend/analytics/ml/forecasting.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import joblib
import os

class OccupationForecaster:
    """Modèle de prévision d'occupation basé sur ML"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = 'models/occupation_forecaster.joblib'
    
    def prepare_features(self, historical_data):
        """Préparer les features pour le ML"""
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Features temporelles
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        df['day_of_year'] = df['date'].dt.dayofyear
        
        # Features basées sur l'historique
        df['occupation_lag_1'] = df['occupation'].shift(1)
        df['occupation_lag_3'] = df['occupation'].shift(3)
        df['occupation_rolling_mean_3'] = df['occupation'].rolling(window=3).mean()
        df['occupation_rolling_std_3'] = df['occupation'].rolling(window=3).std()
        
        # Tendance
        df['trend'] = range(len(df))
        
        # Supprimer les NaN
        df = df.dropna()
        
        return df
    
    def train(self, historical_data):
        """Entraîner le modèle"""
        df = self.prepare_features(historical_data)
        
        feature_columns = [
            'month', 'quarter', 'year', 'day_of_year',
            'occupation_lag_1', 'occupation_lag_3',
            'occupation_rolling_mean_3', 'occupation_rolling_std_3',
            'trend'
        ]
        
        X = df[feature_columns]
        y = df['occupation']
        
        # Normaliser
        X_scaled = self.scaler.fit_transform(X)
        
        # Entraîner
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Sauvegarder
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': feature_columns
        }, self.model_path)
        
        # Calculer le score
        score = self.model.score(X_scaled, y)
        return {'status': 'success', 'r2_score': score}
    
    def predict(self, zone_name, periods=3):
        """Prédire N périodes futures"""
        if not self.is_trained:
            # Charger le modèle si disponible
            if os.path.exists(self.model_path):
                saved = joblib.load(self.model_path)
                self.model = saved['model']
                self.scaler = saved['scaler']
                self.is_trained = True
            else:
                raise Exception("Model not trained")
        
        # Récupérer les données historiques
        historical_data = self.get_historical_data(zone_name)
        df = self.prepare_features(historical_data)
        
        predictions = []
        last_row = df.iloc[-1]
        
        for i in range(1, periods + 1):
            # Créer les features pour la prédiction
            next_date = last_row['date'] + timedelta(days=30 * i)
            
            features = {
                'month': next_date.month,
                'quarter': (next_date.month - 1) // 3 + 1,
                'year': next_date.year,
                'day_of_year': next_date.timetuple().tm_yday,
                'occupation_lag_1': last_row['occupation'],
                'occupation_lag_3': df.iloc[-3]['occupation'] if len(df) >= 3 else last_row['occupation'],
                'occupation_rolling_mean_3': df.tail(3)['occupation'].mean(),
                'occupation_rolling_std_3': df.tail(3)['occupation'].std(),
                'trend': last_row['trend'] + i
            }
            
            X_pred = pd.DataFrame([features])
            X_pred_scaled = self.scaler.transform(X_pred)
            
            prediction = self.model.predict(X_pred_scaled)[0]
            
            predictions.append({
                'period': f"+{i} mois",
                'date': next_date.strftime('%Y-%m'),
                'predicted_occupation': round(max(0, min(100, prediction)), 2)
            })
        
        return predictions
    
    def get_historical_data(self, zone_name):
        """Récupérer les données historiques (à implémenter selon votre source)"""
        # Exemple - à adapter à votre base de données
        from analytics.models import OccupationHistory
        
        history = OccupationHistory.objects.filter(
            zone_name=zone_name
        ).order_by('date').values('date', 'occupation')
        
        return list(history)

# bi_app/backend/analytics/views_ml.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ml.forecasting import OccupationForecaster

@api_view(['POST'])
def train_forecast_model(request):
    """Entraîner le modèle de prévision"""
    zone_name = request.data.get('zone_name')
    historical_data = request.data.get('historical_data')
    
    forecaster = OccupationForecaster()
    result = forecaster.train(historical_data)
    
    return Response(result)

@api_view(['GET'])
def forecast_occupation(request):
    """Prédire l'occupation future"""
    zone_name = request.query_params.get('zone')
    periods = int(request.query_params.get('periods', 3))
    
    forecaster = OccupationForecaster()
    predictions = forecaster.predict(zone_name, periods)
    
    return Response({
        'zone': zone_name,
        'predictions': predictions
    })
```

```jsx
// bi_app/frontend/src/components/ForecastChart.jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, ComposedChart } from 'recharts'
import { ChartContainer } from './charts/BaseChart'
import { TrendingUp, Brain } from 'lucide-react'

export default function ForecastChart({ historicalData, predictions }) {
  // Combiner données historiques et prévisions
  const chartData = [
    ...historicalData.map(d => ({ ...d, type: 'historical' })),
    ...predictions.map(d => ({ 
      date: d.date, 
      occupation: d.predicted_occupation,
      type: 'forecast'
    }))
  ]

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold text-gray-900">
          Prévisions d'Occupation (Machine Learning)
        </h3>
      </div>

      <ChartContainer height={300}>
        <ComposedChart data={chartData}>
          <defs>
            <linearGradient id="historicalGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />

          <Area
            type="monotone"
            dataKey="occupation"
            stroke="#3b82f6"
            fill="url(#historicalGradient)"
            name="Données historiques"
            connectNulls
          />

          <Line
            type="monotone"
            dataKey="occupation"
            stroke="#8b5cf6"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 4, fill: '#8b5cf6' }}
            name="Prévisions ML"
          />
        </ComposedChart>
      </ChartContainer>

      <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
        <p className="text-sm text-purple-800">
          <strong>Note:</strong> Les prévisions sont générées par un modèle de Machine Learning 
          (Random Forest) entraîné sur l'historique des données. La précision augmente avec 
          plus de données historiques.
        </p>
      </div>
    </div>
  )
}
```

### 8.2 Module Géospatial (Cartes Interactives)

```bash
npm install leaflet react-leaflet
```

```jsx
// bi_app/frontend/src/components/ZoneMap.jsx
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import { MapPin } from 'lucide-react'
import 'leaflet/dist/leaflet.css'

export default function ZoneMap({ zones }) {
  // Centre de la carte (à adapter à votre région)
  const center = [5.316667, -4.033333] // Abidjan

  const getColorByOccupation = (occupation) => {
    if (occupation >= 90) return '#ef4444' // red
    if (occupation >= 70) return '#f59e0b' // orange
    if (occupation >= 50) return '#10b981' // green
    return '#3b82f6' // blue
  }

  const getRadiusBySuperficie = (superficie) => {
    // Rayon proportionnel à la superficie
    return Math.sqrt(superficie) / 10
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <MapPin className="w-5 h-5 text-blue-600" />
        Carte des Zones Industrielles
      </h3>

      <MapContainer
        center={center}
        zoom={11}
        style={{ height: '500px', borderRadius: '0.5rem' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        {zones.map(zone => (
          zone.latitude && zone.longitude && (
            <Circle
              key={zone.id}
              center={[zone.latitude, zone.longitude]}
              radius={getRadiusBySuperficie(zone.superficie_totale)}
              pathOptions={{
                fillColor: getColorByOccupation(zone.taux_occupation_pct),
                fillOpacity: 0.4,
                color: getColorByOccupation(zone.taux_occupation_pct),
                weight: 2
              }}
            >
              <Popup>
                <div className="p-2">
                  <h4 className="font-bold text-gray-900">{zone.nom_zone}</h4>
                  <div className="mt-2 space-y-1 text-sm">
                    <p>
                      <strong>Occupation:</strong> {zone.taux_occupation_pct}%
                    </p>
                    <p>
                      <strong>Lots totaux:</strong> {zone.nombre_total_lots}
                    </p>
                    <p>
                      <strong>Superficie:</strong> {zone.superficie_totale.toLocaleString()} m²
                    </p>
                  </div>
                  <a
                    href={`/occupation/zone/${zone.nom_zone}`}
                    className="mt-2 inline-block px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                  >
                    Voir détails
                  </a>
                </div>
              </Popup>
            </Circle>
          )
        ))}
      </MapContainer>

      {/* Légende */}
      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-500"></div>
          <span>&lt; 50%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-green-500"></div>
          <span>50-69%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-orange-500"></div>
          <span>70-89%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-red-500"></div>
          <span>≥ 90%</span>
        </div>
      </div>

      <p className="mt-2 text-xs text-gray-500 text-center">
        Taille des cercles proportionnelle à la superficie de la zone
      </p>
    </div>
  )
}
```

### 8.3 Module Collaboration (Commentaires & Partage)

```python
# bi_app/backend/analytics/models.py
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entity_type = models.CharField(max_length=50)  # 'zone', 'dashboard', etc.
    entity_id = models.CharField(max_length=100)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']

class SharedDashboard(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_dashboards')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    config = models.JSONField()  # Configuration du dashboard
    share_token = models.CharField(max_length=100, unique=True)
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, blank=True, related_name='dashboards_shared_with_me')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shared_dashboards'
```

```jsx
// bi_app/frontend/src/components/CommentSection.jsx
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MessageSquare, Send, Trash2, Edit2 } from 'lucide-react'
import { commentsAPI } from '../services/api'

export default function CommentSection({ entityType, entityId }) {
  const [newComment, setNewComment] = useState('')
  const [replyTo, setReplyTo] = useState(null)
  const queryClient = useQueryClient()

  const { data: comments, isLoading } = useQuery({
    queryKey: ['comments', entityType, entityId],
    queryFn: () => commentsAPI.getComments(entityType, entityId)
  })

  const addCommentMutation = useMutation({
    mutationFn: commentsAPI.addComment,
    onSuccess: () => {
      queryClient.invalidateQueries(['comments', entityType, entityId])
      setNewComment('')
      setReplyTo(null)
    }
  })

  const deleteCommentMutation = useMutation({
    mutationFn: commentsAPI.deleteComment,
    onSuccess: () => {
      queryClient.invalidateQueries(['comments', entityType, entityId])
    }
  })

  const handleSubmit = () => {
    if (newComment.trim()) {
      addCommentMutation.mutate({
        entityType,
        entityId,
        content: newComment,
        parentId: replyTo
      })
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-blue-600" />
        Commentaires ({comments?.length || 0})
      </h3>

      {/* Formulaire nouveau commentaire */}
      <div className="mb-6">
        {replyTo && (
          <div className="mb-2 p-2 bg-blue-50 rounded flex items-center justify-between">
            <span className="text-sm text-blue-700">
              Répondre à {comments.find(c => c.id === replyTo)?.user}
            </span>
            <button onClick={() => setReplyTo(null)} className="text-blue-600 hover:text-blue-800">
              Annuler
            </button>
          </div>
        )}
        
        <div className="flex gap-2">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Ajouter un commentaire..."
            className="flex-1 px-3 py-2 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
          <button
            onClick={handleSubmit}
            disabled={!newComment.trim() || addCommentMutation.isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 h-fit"
          >
            <Send className="w-4 h-4" />
            Envoyer
          </button>
        </div>
      </div>

      {/* Liste des commentaires */}
      <div className="space-y-4">
        {comments?.filter(c => !c.parent).map(comment => (
          <div key={comment.id} className="border-l-2 border-gray-200 pl-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-900">{comment.user}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(comment.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <p className="text-gray-700">{comment.content}</p>
                
                <button
                  onClick={() => setReplyTo(comment.id)}
                  className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  Répondre
                </button>
              </div>

              <button
                onClick={() => deleteCommentMutation.mutate(comment.id)}
                className="p-1 hover:bg-red-100 rounded"
              >
                <Trash2 className="w-4 h-4 text-red-500" />
              </button>
            </div>

            {/* Réponses */}
            {comment.replies?.map(reply => (
              <div key={reply.id} className="mt-3 ml-6 pl-4 border-l-2 border-gray-100">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-gray-800">{reply.user}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(reply.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">{reply.content}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 9. Plan d'Implémentation Prioritaire

### Phase 1: Performance & Stabilité (2-3 semaines)

**Semaine 1: Cache & Pagination**
- Jour 1-2: Installer et configurer Redis
- Jour 3-4: Implémenter cache backend (views, services)
- Jour 5-7: Pagination côté serveur + tests

**Semaine 2: Optimisation Database**
- Jour 1-2: Créer indexes database
- Jour 3-4: Optimiser requêtes ORM
- Jour 5-7: Tests de performance, monitoring

**Semaine 3: Frontend Performance**
- Jour 1-3: Code splitting, lazy loading
- Jour 4-5: Skeleton loaders
- Jour 6-7: Tests et optimisation

**Livrables:**
- ✅ Cache Redis opérationnel
- ✅ Pagination serveur sur toutes les listes
- ✅ Indexes database
- ✅ Code splitting
- ✅ Temps de chargement < 2s

### Phase 2: Visualisations Avancées (2 semaines)

**Semaine 4-5: Charts Recharts**
- Installer Recharts
- Graphiques de tendance (LineChart, AreaChart)
- Comparaisons (BarChart groupé)
- Treemap pour superficies
- Heatmap calendrier
- Tests et responsive

**Livrables:**
- ✅ 5+ types de charts avancés
- ✅ Page Analytics dédiée
- ✅ Exports charts en image

### Phase 3: Fonctionnalités Métier (3 semaines)

**Semaine 6: Alertes & Prédictions**
- Modèle Alert backend
- Système de vérification automatique
- Interface alertes frontend
- Prédictions simples (moyenne mobile)

**Semaine 7: Filtres & Exports**
- Système filtres sauvegardés
- Export Excel multi-feuilles
- Export PDF amélioré
- Templates personnalisables

**Semaine 8: Tests & Polish**
- Tests unitaires backend (80% coverage)
- Tests frontend composants
- Fix bugs
- Documentation

**Livrables:**
- ✅ Système d'alertes opérationnel
- ✅ Filtres sauvegardés
- ✅ Exports avancés
- ✅ Tests automatisés

### Phase 4: UX & Architecture (2 semaines)

**Semaine 9: UX**
- Dark mode
- Raccourcis clavier
- Recherche globale
- Skeleton loaders everywhere

**Semaine 10: Backend Architecture**
- Celery pour tâches async
- Tâches périodiques (cache refresh, alertes)
- Logs audit
- Monitoring

**Livrables:**
- ✅ Dark mode complet
- ✅ Raccourcis clavier
- ✅ Celery opérationnel
- ✅ Audit logs

### Phase 5: Sécurité (1-2 semaines)

**Semaine 11-12:**
- 2FA authentication
- RBAC (roles & permissions)
- Encryption données sensibles
- Security audit
- Pen testing basique

**Livrables:**
- ✅ 2FA activable
- ✅ RBAC complet
- ✅ Audit de sécurité

### Phase 6: Modules Avancés (optionnel - 3-4 semaines)

**Semaine 13-14: ML & Prévisions**
- Modèle Random Forest
- Entraînement automatique
- API prévisions
- Interface prévisions

**Semaine 15-16: Géospatial & Collaboration**
- Cartes Leaflet
- Géolocalisation zones
- Système commentaires
- Dashboards partagés

**Livrables:**
- ✅ Prévisions ML
- ✅ Carte interactive
- ✅ Collaboration

---

## 10. Quick Wins (Impact élevé, effort faible)

### Quick Win 1: Dark Mode (2h)
```bash
# Temps: 2 heures
# Impact: UX moderne, accessibilité
```

### Quick Win 2: Recharts Integration (2h)
```bash
# Temps: 2 heures
# Impact: Visualisations professionnelles
```

### Quick Win 3: Redis Cache (3h)
```bash
# Temps: 3 heures
# Impact: Performance x3-5
```

### Quick Win 4: Excel Export (4h)
```bash
# Temps: 4 heures
# Impact: Feature métier critique
```

### Quick Win 5: Alertes Simples (3h)
```bash
# Temps: 3 heures
# Impact: Proactivité
```

### Quick Win 6: Filtres Sauvegardés (4h)
```bash
# Temps: 4 heures
# Impact: Productivité utilisateurs
```

### Quick Win 7: Skeleton Loaders (1h)
```bash
# Temps: 1 heure
# Impact: Perception performance
```

### Quick Win 8: Tests Automatisés (6h setup)
```bash
# Temps: 6 heures
# Impact: Qualité, maintenabilité
```

---

## Métriques de Succès

### Performance
- ✅ Temps de chargement initial < 2s
- ✅ Taux de cache hit > 80%
- ✅ Requêtes API < 500ms (p95)

### Qualité
- ✅ Code coverage tests > 80%
- ✅ 0 erreurs critiques production
- ✅ Lighthouse score > 90

### Adoption
- ✅ 90% utilisateurs adoptent dark mode
- ✅ Alertes réduisent incidents 50%
- ✅ Export utilisé quotidiennement

### Sécurité
- ✅ 100% utilisateurs admins avec 2FA
- ✅ Audit logs complets
- ✅ 0 vulnérabilités critiques

---

## Prochaines Étapes Recommandées

1. **Cette semaine (Quick Wins):**
   - Installer Redis et implémenter cache
   - Ajouter dark mode
   - Créer 2-3 charts Recharts

2. **Ce mois:**
   - Compléter Phase 1 (Performance)
   - Débuter Phase 2 (Visualisations)
   - Setup tests automatisés

3. **Ce trimestre:**
   - Phases 1-4 complètes
   - Système alertes production
   - Architecture Celery

4. **Cette année:**
   - Toutes phases complétées
   - ML en production
   - Plateforme complète et scalable

**Prêt à démarrer?** Choisissez une phase ou un quick win pour commencer! 🚀
