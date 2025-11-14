# Plan d'Amélioration - Fonctionnalités Métier Avancées

## 3. Fonctionnalités Métier

### 3.1 Système de Prédictions et Alertes

#### Backend - Modèle de Prédiction Simple

```python
# bi_app/backend/analytics/predictions.py
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min
from .models import MartOccupationZones
import numpy as np

class OccupationPredictor:
    """Prédictions simples basées sur les tendances historiques"""
    
    @staticmethod
    def predict_next_month(zone_name, historical_data):
        """
        Prédiction simple: moyenne mobile avec pondération récente
        
        Args:
            zone_name: Nom de la zone
            historical_data: Liste de dicts [{'month': '2024-01', 'occupation': 75}, ...]
        
        Returns:
            dict avec prédiction et intervalle de confiance
        """
        if len(historical_data) < 3:
            return None
            
        # Extraire les valeurs d'occupation
        values = [d['occupation'] for d in historical_data[-6:]]  # 6 derniers mois
        
        # Moyenne mobile pondérée (poids plus élevés pour mois récents)
        weights = np.array([1, 1.2, 1.4, 1.6, 1.8, 2.0][-len(values):])
        weighted_avg = np.average(values, weights=weights)
        
        # Calculer la tendance (croissante/décroissante)
        if len(values) >= 3:
            recent_trend = (values[-1] - values[-3]) / 3
        else:
            recent_trend = 0
            
        # Prédiction
        prediction = weighted_avg + recent_trend
        
        # Intervalle de confiance basé sur la volatilité
        std_dev = np.std(values)
        confidence_interval = (
            max(0, prediction - std_dev * 1.96),  # -2 sigma
            min(100, prediction + std_dev * 1.96)  # +2 sigma
        )
        
        return {
            'zone': zone_name,
            'predicted_value': round(prediction, 2),
            'confidence_interval': {
                'lower': round(confidence_interval[0], 2),
                'upper': round(confidence_interval[1], 2)
            },
            'trend': 'increasing' if recent_trend > 0 else 'decreasing',
            'confidence_level': 'high' if std_dev < 5 else 'medium' if std_dev < 10 else 'low'
        }
    
    @staticmethod
    def detect_anomalies(zone_name, current_value, historical_data):
        """Détecte les valeurs anormales"""
        values = [d['occupation'] for d in historical_data[-12:]]
        mean = np.mean(values)
        std = np.std(values)
        
        # Valeur en dehors de 2 sigma = anomalie
        is_anomaly = abs(current_value - mean) > (2 * std)
        
        return {
            'is_anomaly': is_anomaly,
            'severity': 'high' if abs(current_value - mean) > (3 * std) else 'medium',
            'expected_range': (mean - 2*std, mean + 2*std),
            'current_value': current_value
        }

# bi_app/backend/analytics/alerts.py
from django.core.mail import send_mail
from django.conf import settings
from .models import Alert
from datetime import datetime

class AlertManager:
    """Gestion des alertes métier"""
    
    ALERT_TYPES = {
        'HIGH_OCCUPATION': {
            'threshold': 90,
            'severity': 'warning',
            'message': 'Zone proche de la saturation'
        },
        'CRITICAL_OCCUPATION': {
            'threshold': 95,
            'severity': 'critical',
            'message': 'Zone saturée - action urgente requise'
        },
        'LOW_PAYMENT_RATE': {
            'threshold': 70,
            'severity': 'warning',
            'message': 'Taux de paiement faible'
        },
        'HIGH_OVERDUE_INVOICES': {
            'threshold': 5,
            'severity': 'warning',
            'message': 'Nombre élevé de factures en retard'
        }
    }
    
    @classmethod
    def check_occupation_alerts(cls, zone_data):
        """Vérifier les alertes d'occupation"""
        alerts = []
        
        occupation = zone_data.get('taux_occupation_pct', 0)
        zone_name = zone_data.get('nom_zone')
        
        if occupation >= cls.ALERT_TYPES['CRITICAL_OCCUPATION']['threshold']:
            alerts.append(cls.create_alert(
                alert_type='CRITICAL_OCCUPATION',
                zone_name=zone_name,
                value=occupation
            ))
        elif occupation >= cls.ALERT_TYPES['HIGH_OCCUPATION']['threshold']:
            alerts.append(cls.create_alert(
                alert_type='HIGH_OCCUPATION',
                zone_name=zone_name,
                value=occupation
            ))
        
        return alerts
    
    @classmethod
    def create_alert(cls, alert_type, zone_name, value):
        """Créer une alerte"""
        config = cls.ALERT_TYPES[alert_type]
        
        alert = Alert.objects.create(
            type=alert_type,
            severity=config['severity'],
            entity_type='zone',
            entity_name=zone_name,
            message=f"{zone_name}: {config['message']} ({value}%)",
            value=value,
            threshold=config['threshold'],
            created_at=datetime.now()
        )
        
        # Envoyer notification si critique
        if config['severity'] == 'critical':
            cls.send_notification(alert)
        
        return alert
    
    @classmethod
    def send_notification(cls, alert):
        """Envoyer une notification par email"""
        subject = f"[SIGETI BI] Alerte {alert.severity.upper()}: {alert.entity_name}"
        message = f"""
        Alerte détectée:
        
        Type: {alert.type}
        Sévérité: {alert.severity}
        Entité: {alert.entity_name}
        Message: {alert.message}
        Valeur actuelle: {alert.value}
        Seuil: {alert.threshold}
        
        Consultez le tableau de bord pour plus de détails.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )

# bi_app/backend/analytics/models.py
from django.db import models

class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acquittée'),
        ('resolved', 'Résolue'),
    ]
    
    type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    entity_type = models.CharField(max_length=50)  # 'zone', 'client', etc.
    entity_name = models.CharField(max_length=200)
    message = models.TextField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    threshold = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'analytics_alerts'
        ordering = ['-created_at']
    
    def acknowledge(self):
        self.status = 'acknowledged'
        self.acknowledged_at = datetime.now()
        self.save()
    
    def resolve(self):
        self.status = 'resolved'
        self.resolved_at = datetime.now()
        self.save()

# bi_app/backend/analytics/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .predictions import OccupationPredictor
from .alerts import AlertManager

@api_view(['GET'])
def predictions_view(request):
    """Endpoint pour les prédictions"""
    zone_name = request.GET.get('zone')
    
    # Récupérer données historiques (à implémenter selon votre source)
    historical_data = get_historical_data(zone_name)
    
    prediction = OccupationPredictor.predict_next_month(zone_name, historical_data)
    
    return Response({
        'prediction': prediction,
        'historical_data': historical_data
    })

@api_view(['GET'])
def alerts_view(request):
    """Liste des alertes actives"""
    status = request.GET.get('status', 'active')
    severity = request.GET.get('severity')
    
    queryset = Alert.objects.filter(status=status)
    if severity:
        queryset = queryset.filter(severity=severity)
    
    alerts = queryset.values()
    
    return Response({
        'count': queryset.count(),
        'alerts': list(alerts)
    })

@api_view(['POST'])
def acknowledge_alert(request, alert_id):
    """Acquitter une alerte"""
    alert = Alert.objects.get(id=alert_id)
    alert.acknowledge()
    return Response({'status': 'acknowledged'})
```

#### Frontend - Composant Alertes

```jsx
// bi_app/frontend/src/components/AlertsPanel.jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, AlertCircle, Info, CheckCircle, X } from 'lucide-react'
import { alertsAPI } from '../services/api'

export default function AlertsPanel() {
  const queryClient = useQueryClient()
  
  const { data: alertsData, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsAPI.getAlerts({ status: 'active' }),
    refetchInterval: 30000, // Refresh toutes les 30 secondes
  })

  const acknowledgeMutation = useMutation({
    mutationFn: alertsAPI.acknowledgeAlert,
    onSuccess: () => {
      queryClient.invalidateQueries(['alerts'])
    }
  })

  const getIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertCircle className="w-5 h-5 text-red-500" />
      case 'warning': return <AlertTriangle className="w-5 h-5 text-orange-500" />
      default: return <Info className="w-5 h-5 text-blue-500" />
    }
  }

  const getBgColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-50 border-red-200'
      case 'warning': return 'bg-orange-50 border-orange-200'
      default: return 'bg-blue-50 border-blue-200'
    }
  }

  if (isLoading) return <div className="animate-pulse h-32 bg-gray-100 rounded-lg"></div>

  const alerts = alertsData?.alerts || []

  if (alerts.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
        <CheckCircle className="w-5 h-5 text-green-500" />
        <p className="text-green-700">Aucune alerte active</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Alertes Actives ({alerts.length})
        </h3>
      </div>

      {alerts.map(alert => (
        <div
          key={alert.id}
          className={`border rounded-lg p-4 ${getBgColor(alert.severity)}`}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3 flex-1">
              {getIcon(alert.severity)}
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-900">
                    {alert.entity_name}
                  </span>
                  <span className="px-2 py-0.5 bg-white rounded text-xs font-medium text-gray-600">
                    {alert.type}
                  </span>
                </div>
                
                <p className="text-sm text-gray-700">{alert.message}</p>
                
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-600">
                  <span>Valeur: {alert.value}%</span>
                  <span>Seuil: {alert.threshold}%</span>
                  <span>{new Date(alert.created_at).toLocaleDateString('fr-FR')}</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => acknowledgeMutation.mutate(alert.id)}
              className="p-1 hover:bg-white rounded transition-colors"
              title="Acquitter"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
```

```jsx
// bi_app/frontend/src/components/PredictionCard.jsx
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function PredictionCard({ prediction }) {
  if (!prediction) return null

  const { predicted_value, confidence_interval, trend, confidence_level } = prediction

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h4 className="text-sm font-medium text-gray-600">Prévision Prochaine Période</h4>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {predicted_value.toFixed(1)}%
          </p>
        </div>
        
        <div className={`p-2 rounded-lg ${trend === 'increasing' ? 'bg-orange-100' : 'bg-green-100'}`}>
          {trend === 'increasing' ? (
            <TrendingUp className="w-6 h-6 text-orange-600" />
          ) : (
            <TrendingDown className="w-6 h-6 text-green-600" />
          )}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Intervalle de confiance</span>
          <span className="font-medium">
            {confidence_interval.lower.toFixed(1)}% - {confidence_interval.upper.toFixed(1)}%
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Niveau de confiance</span>
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${
            confidence_level === 'high' ? 'bg-green-100 text-green-700' :
            confidence_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
            'bg-red-100 text-red-700'
          }`}>
            {confidence_level === 'high' ? 'Élevé' : 
             confidence_level === 'medium' ? 'Moyen' : 'Faible'}
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Tendance</span>
          <span className={`font-medium ${trend === 'increasing' ? 'text-orange-600' : 'text-green-600'}`}>
            {trend === 'increasing' ? 'Hausse' : 'Baisse'}
          </span>
        </div>
      </div>
    </div>
  )
}
```

### 3.2 Filtres Sauvegardés

```python
# bi_app/backend/analytics/models.py
class SavedFilter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_filters')
    name = models.CharField(max_length=100)
    page = models.CharField(max_length=50)  # 'occupation', 'clients', etc.
    filters = models.JSONField()  # {"search": "Zone A", "min_occupation": 50, ...}
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_saved_filters'
        unique_together = ['user', 'name', 'page']
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'un seul filtre par défaut par page
        if self.is_default:
            SavedFilter.objects.filter(
                user=self.user,
                page=self.page,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)

# bi_app/backend/analytics/views.py
from rest_framework import viewsets
from rest_framework.decorators import action

class SavedFilterViewSet(viewsets.ModelViewSet):
    serializer_class = SavedFilterSerializer
    
    def get_queryset(self):
        return SavedFilter.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_page(self, request):
        """Récupérer les filtres pour une page spécifique"""
        page = request.query_params.get('page')
        filters = self.get_queryset().filter(page=page)
        serializer = self.get_serializer(filters, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Définir un filtre comme par défaut"""
        filter_obj = self.get_object()
        filter_obj.is_default = True
        filter_obj.save()
        return Response({'status': 'default set'})
```

```jsx
// bi_app/frontend/src/hooks/useSavedFilters.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { filtersAPI } from '../services/api'

export function useSavedFilters(page) {
  const queryClient = useQueryClient()

  const { data: savedFilters } = useQuery({
    queryKey: ['saved-filters', page],
    queryFn: () => filtersAPI.getByPage(page)
  })

  const saveMutation = useMutation({
    mutationFn: filtersAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['saved-filters', page])
    }
  })

  const deleteMutation = useMutation({
    mutationFn: filtersAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['saved-filters', page])
    }
  })

  const setDefaultMutation = useMutation({
    mutationFn: filtersAPI.setDefault,
    onSuccess: () => {
      queryClient.invalidateQueries(['saved-filters', page])
    }
  })

  const saveCurrentFilters = (name, filters) => {
    saveMutation.mutate({ name, page, filters })
  }

  const deleteFilter = (filterId) => {
    deleteMutation.mutate(filterId)
  }

  const setDefault = (filterId) => {
    setDefaultMutation.mutate(filterId)
  }

  const getDefaultFilter = () => {
    return savedFilters?.find(f => f.is_default)
  }

  return {
    savedFilters: savedFilters || [],
    saveCurrentFilters,
    deleteFilter,
    setDefault,
    getDefaultFilter,
    isSaving: saveMutation.isLoading
  }
}
```

```jsx
// bi_app/frontend/src/components/SavedFiltersDropdown.jsx
import { useState } from 'react'
import { Save, Star, Trash2, MoreVertical } from 'lucide-react'
import { useSavedFilters } from '../hooks/useSavedFilters'

export default function SavedFiltersDropdown({ page, currentFilters, onApplyFilter }) {
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [filterName, setFilterName] = useState('')
  
  const { savedFilters, saveCurrentFilters, deleteFilter, setDefault } = useSavedFilters(page)

  const handleSave = () => {
    if (filterName.trim()) {
      saveCurrentFilters(filterName, currentFilters)
      setFilterName('')
      setShowSaveDialog(false)
    }
  }

  return (
    <div className="relative">
      {/* Bouton d'ouverture */}
      <button
        onClick={() => setShowSaveDialog(true)}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
      >
        <Save className="w-4 h-4" />
        Filtres sauvegardés
      </button>

      {/* Dialog de sauvegarde */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Gérer les filtres sauvegardés
            </h3>

            {/* Sauvegarder nouveau filtre */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nouveau filtre
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={filterName}
                  onChange={(e) => setFilterName(e.target.value)}
                  placeholder="Nom du filtre..."
                  className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Sauvegarder
                </button>
              </div>
            </div>

            {/* Liste des filtres sauvegardés */}
            <div className="space-y-2 mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filtres sauvegardés ({savedFilters.length})
              </label>
              
              {savedFilters.length === 0 ? (
                <p className="text-sm text-gray-500 italic">Aucun filtre sauvegardé</p>
              ) : (
                <div className="max-h-60 overflow-y-auto space-y-2">
                  {savedFilters.map(filter => (
                    <div
                      key={filter.id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                    >
                      <button
                        onClick={() => {
                          onApplyFilter(filter.filters)
                          setShowSaveDialog(false)
                        }}
                        className="flex-1 text-left flex items-center gap-2"
                      >
                        {filter.is_default && (
                          <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        )}
                        <span className="font-medium text-gray-900">{filter.name}</span>
                      </button>

                      <div className="flex items-center gap-1">
                        {!filter.is_default && (
                          <button
                            onClick={() => setDefault(filter.id)}
                            className="p-1 hover:bg-gray-200 rounded"
                            title="Définir par défaut"
                          >
                            <Star className="w-4 h-4 text-gray-400" />
                          </button>
                        )}
                        <button
                          onClick={() => deleteFilter(filter.id)}
                          className="p-1 hover:bg-red-100 rounded"
                          title="Supprimer"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Bouton fermer */}
            <button
              onClick={() => setShowSaveDialog(false)}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
```

### 3.3 Export Excel Avancé

```bash
npm install xlsx file-saver
```

```jsx
// bi_app/frontend/src/utils/exportExcel.js
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

export const exportToExcel = (data, fileName, options = {}) => {
  const {
    sheetName = 'Données',
    multiSheets = false,
    includeCharts = false,
    formatting = true
  } = options

  // Créer un nouveau classeur
  const workbook = XLSX.utils.book_new()

  if (multiSheets && Array.isArray(data)) {
    // Plusieurs feuilles
    data.forEach((sheet, index) => {
      const worksheet = XLSX.utils.json_to_sheet(sheet.data)
      
      if (formatting) {
        applyFormatting(worksheet, sheet.data)
      }
      
      XLSX.utils.book_append_sheet(
        workbook,
        worksheet,
        sheet.name || `Feuille${index + 1}`
      )
    })
  } else {
    // Une seule feuille
    const worksheet = XLSX.utils.json_to_sheet(data)
    
    if (formatting) {
      applyFormatting(worksheet, data)
    }
    
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
  }

  // Générer le fichier
  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([excelBuffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  })
  
  saveAs(blob, `${fileName}_${new Date().toISOString().split('T')[0]}.xlsx`)
}

const applyFormatting = (worksheet, data) => {
  if (!data || data.length === 0) return

  const range = XLSX.utils.decode_range(worksheet['!ref'])
  
  // Largeur des colonnes
  const colWidths = Object.keys(data[0]).map(key => ({
    wch: Math.max(
      key.length,
      ...data.map(row => String(row[key] || '').length)
    ) + 2
  }))
  worksheet['!cols'] = colWidths

  // Style de l'en-tête (ligne 1)
  for (let col = range.s.c; col <= range.e.c; col++) {
    const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col })
    if (!worksheet[cellAddress]) continue
    
    worksheet[cellAddress].s = {
      font: { bold: true, color: { rgb: 'FFFFFF' } },
      fill: { fgColor: { rgb: '3B82F6' } },
      alignment: { horizontal: 'center', vertical: 'center' }
    }
  }
}

// Fonction spécialisée pour export zones
export const exportZonesToExcel = (zones) => {
  const formattedData = zones.map(zone => ({
    'Zone': zone.nom_zone,
    'Taux d\'Occupation (%)': zone.taux_occupation_pct,
    'Lots Total': zone.nombre_total_lots,
    'Lots Attribués': zone.lots_attribues,
    'Lots Disponibles': zone.lots_disponibles,
    'Superficie Totale (m²)': zone.superficie_totale,
    'Superficie Attribuée (m²)': zone.superficie_attribuee,
    'Superficie Disponible (m²)': zone.superficie_disponible
  }))

  exportToExcel(formattedData, 'zones_occupation', {
    sheetName: 'Zones Industrielles',
    formatting: true
  })
}

// Export multi-feuilles
export const exportDashboardToExcel = (dashboardData) => {
  const sheets = [
    {
      name: 'Résumé',
      data: [dashboardData.summary]
    },
    {
      name: 'Zones',
      data: dashboardData.zones.map(z => ({
        'Zone': z.nom_zone,
        'Occupation': z.taux_occupation_pct,
        'Lots': z.nombre_total_lots
      }))
    },
    {
      name: 'Top 5 Plus Occupées',
      data: dashboardData.topZones.plus_occupees
    },
    {
      name: 'Top 5 Moins Occupées',
      data: dashboardData.topZones.moins_occupees
    }
  ]

  exportToExcel(sheets, 'dashboard_complet', {
    multiSheets: true,
    formatting: true
  })
}
```

```jsx
// Bouton d'export dans le composant
import { Download } from 'lucide-react'
import { exportZonesToExcel, exportDashboardToExcel } from '../utils/exportExcel'

export default function Occupation() {
  // ... code existant

  const handleExportAll = () => {
    exportDashboardToExcel({
      summary: summaryData,
      zones: allZonesData,
      topZones: topZones
    })
  }

  return (
    <div>
      {/* Bouton export */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => exportZonesToExcel(allZonesData)}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Exporter en Excel
        </button>
        
        <button
          onClick={handleExportAll}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export Complet (Multi-feuilles)
        </button>
      </div>

      {/* Reste du composant */}
    </div>
  )
}
```

---

**Suite dans AMELIORATIONS_UX_ARCHITECTURE.md**
