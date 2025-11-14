# Plan d'Amélioration - Sécurité et Tests

## 6. Sécurité et Gouvernance

### 6.1 Authentification 2FA (Two-Factor Authentication)

```bash
pip install django-otp qrcode
```

```python
# bi_app/backend/sigeti_bi/settings.py
INSTALLED_APPS = [
    # ... apps existantes
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

MIDDLEWARE = [
    # ... middleware existants
    'django_otp.middleware.OTPMiddleware',
]

# bi_app/backend/analytics/models.py
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    two_factor_enabled = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Administrateur'),
        ('manager', 'Gestionnaire'),
        ('viewer', 'Visualiseur'),
    ], default='viewer')
    
    class Meta:
        db_table = 'user_profiles'

# bi_app/backend/analytics/views_auth.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import user_has_device
import qrcode
import io
import base64

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Activer l'authentification à deux facteurs"""
    user = request.user
    
    # Créer ou récupérer le device TOTP
    device, created = TOTPDevice.objects.get_or_create(
        user=user,
        name='default'
    )
    
    # Générer le QR code
    url = device.config_url
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return Response({
        'qr_code': f'data:image/png;base64,{qr_code}',
        'secret': device.key,
        'url': url
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """Vérifier le code 2FA"""
    token = request.data.get('token')
    user = request.user
    
    device = TOTPDevice.objects.filter(user=user, name='default').first()
    
    if device and device.verify_token(token):
        device.confirmed = True
        device.save()
        
        # Mettre à jour le profil
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.two_factor_enabled = True
        profile.save()
        
        return Response({'status': 'success', 'message': '2FA activé'})
    
    return Response({'status': 'error', 'message': 'Code invalide'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """Désactiver 2FA"""
    user = request.user
    TOTPDevice.objects.filter(user=user).delete()
    
    profile = user.profile
    profile.two_factor_enabled = False
    profile.save()
    
    return Response({'status': 'success', 'message': '2FA désactivé'})
```

```jsx
// bi_app/frontend/src/pages/Settings2FA.jsx
import { useState } from 'react'
import { Shield, Smartphone, Check, X } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { authAPI } from '../services/api'

export default function Settings2FA() {
  const [step, setStep] = useState(1) // 1: Setup, 2: Verify
  const [verificationCode, setVerificationCode] = useState('')

  const { data: qrData, mutate: enable2FA, isLoading } = useMutation({
    mutationFn: authAPI.enable2FA,
    onSuccess: () => setStep(2)
  })

  const verifyMutation = useMutation({
    mutationFn: authAPI.verify2FA,
    onSuccess: () => {
      alert('2FA activé avec succès!')
      setStep(1)
    },
    onError: () => {
      alert('Code invalide. Veuillez réessayer.')
    }
  })

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-sm border p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-blue-100 rounded-lg">
            <Shield className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Authentification à Deux Facteurs
            </h2>
            <p className="text-gray-600">
              Renforcez la sécurité de votre compte
            </p>
          </div>
        </div>

        {step === 1 && (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">
                Pourquoi activer la 2FA?
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Protection contre les accès non autorisés</li>
                <li>✓ Sécurité renforcée même si votre mot de passe est compromis</li>
                <li>✓ Conformité avec les standards de sécurité</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Étape 1: Installer une application d'authentification
              </h4>
              <p className="text-sm text-gray-600 mb-3">
                Téléchargez une application comme Google Authenticator, Microsoft Authenticator, ou Authy.
              </p>
            </div>

            <button
              onClick={() => enable2FA()}
              disabled={isLoading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Smartphone className="w-5 h-5" />
              {isLoading ? 'Génération...' : 'Générer le QR Code'}
            </button>
          </div>
        )}

        {step === 2 && qrData && (
          <div className="space-y-6">
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">
                Étape 2: Scanner le QR Code
              </h4>
              <div className="flex justify-center mb-4">
                <img 
                  src={qrData.qr_code} 
                  alt="QR Code 2FA"
                  className="border-4 border-gray-200 rounded-lg"
                />
              </div>
              <p className="text-center text-sm text-gray-600 mb-2">
                Ou entrez manuellement cette clé:
              </p>
              <div className="bg-gray-100 p-3 rounded-lg text-center font-mono text-sm break-all">
                {qrData.secret}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Étape 3: Entrez le code de vérification
              </h4>
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="000000"
                maxLength={6}
                className="w-full px-4 py-3 border rounded-lg text-center text-2xl font-mono tracking-wider"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setStep(1)
                  setVerificationCode('')
                }}
                className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={() => verifyMutation.mutate({ token: verificationCode })}
                disabled={verificationCode.length !== 6 || verifyMutation.isLoading}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Check className="w-5 h-5" />
                Vérifier et Activer
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
```

### 6.2 RBAC (Role-Based Access Control)

```python
# bi_app/backend/analytics/permissions.py
from rest_framework import permissions

class RoleBasedPermission(permissions.BasePermission):
    """Permission basée sur les rôles utilisateur"""
    
    # Définir les rôles et leurs permissions
    ROLE_PERMISSIONS = {
        'admin': ['view', 'create', 'update', 'delete', 'export'],
        'manager': ['view', 'create', 'update', 'export'],
        'viewer': ['view'],
    }
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Récupérer le rôle de l'utilisateur
        try:
            user_role = request.user.profile.role
        except:
            user_role = 'viewer'  # Par défaut
        
        # Déterminer l'action requise
        if request.method == 'GET':
            required_action = 'view'
        elif request.method == 'POST':
            required_action = 'create'
        elif request.method in ['PUT', 'PATCH']:
            required_action = 'update'
        elif request.method == 'DELETE':
            required_action = 'delete'
        else:
            required_action = 'view'
        
        # Vérifier si le rôle a la permission
        allowed_actions = self.ROLE_PERMISSIONS.get(user_role, [])
        return required_action in allowed_actions

class CanExportData(permissions.BasePermission):
    """Permission pour exporter des données"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            user_role = request.user.profile.role
            return user_role in ['admin', 'manager']
        except:
            return False

# Utilisation dans les vues
from rest_framework import viewsets
from .permissions import RoleBasedPermission, CanExportData

class OccupationViewSet(viewsets.ModelViewSet):
    permission_classes = [RoleBasedPermission]
    queryset = MartOccupationZones.objects.all()
    serializer_class = OccupationZoneSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[CanExportData])
    def export(self, request):
        """Export réservé aux admins et managers"""
        # Logique d'export
        pass
```

### 6.3 Audit Logs

```python
# bi_app/backend/analytics/models.py
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('read', 'Lecture'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('export', 'Export'),
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50)  # 'zone', 'client', etc.
    resource_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.resource_type} - {self.timestamp}"

# bi_app/backend/analytics/middleware.py
from .models import AuditLog

class AuditMiddleware:
    """Middleware pour logger automatiquement les actions"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Logger certaines actions
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.log_action(request, response)
        
        return response
    
    def log_action(self, request, response):
        if response.status_code < 400:  # Seulement les succès
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            
            AuditLog.objects.create(
                user=request.user,
                action=action_map.get(request.method, 'read'),
                resource_type=self.get_resource_type(request.path),
                details={
                    'path': request.path,
                    'method': request.method,
                    'status': response.status_code
                },
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
    
    @staticmethod
    def get_resource_type(path):
        """Extraire le type de ressource du chemin"""
        if 'occupation' in path:
            return 'occupation'
        elif 'client' in path:
            return 'client'
        return 'unknown'
    
    @staticmethod
    def get_client_ip(request):
        """Obtenir l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Ajouter dans settings.py
MIDDLEWARE = [
    # ... autres middleware
    'analytics.middleware.AuditMiddleware',
]
```

```jsx
// bi_app/frontend/src/pages/AuditLogs.jsx
import { useQuery } from '@tanstack/react-query'
import { Clock, User, Eye, Edit, Trash2, Download } from 'lucide-react'
import { auditAPI } from '../services/api'

export default function AuditLogs() {
  const [filters, setFilters] = useState({
    action: '',
    user: '',
    startDate: '',
    endDate: ''
  })

  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit-logs', filters],
    queryFn: () => auditAPI.getLogs(filters)
  })

  const getActionIcon = (action) => {
    switch (action) {
      case 'read': return <Eye className="w-4 h-4 text-blue-500" />
      case 'create': case 'update': return <Edit className="w-4 h-4 text-green-500" />
      case 'delete': return <Trash2 className="w-4 h-4 text-red-500" />
      case 'export': return <Download className="w-4 h-4 text-purple-500" />
      default: return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Journal d'Audit</h1>

      {/* Filtres */}
      <div className="bg-white rounded-xl shadow-sm border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.action}
            onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="">Toutes les actions</option>
            <option value="create">Création</option>
            <option value="read">Lecture</option>
            <option value="update">Modification</option>
            <option value="delete">Suppression</option>
            <option value="export">Export</option>
          </select>

          <input
            type="text"
            value={filters.user}
            onChange={(e) => setFilters({ ...filters, user: e.target.value })}
            placeholder="Utilisateur..."
            className="px-3 py-2 border rounded-lg"
          />

          <input
            type="date"
            value={filters.startDate}
            onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
            className="px-3 py-2 border rounded-lg"
          />

          <input
            type="date"
            value={filters.endDate}
            onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
            className="px-3 py-2 border rounded-lg"
          />
        </div>
      </div>

      {/* Table des logs */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <tr>
              <th className="px-4 py-3 text-left">Date/Heure</th>
              <th className="px-4 py-3 text-left">Utilisateur</th>
              <th className="px-4 py-3 text-left">Action</th>
              <th className="px-4 py-3 text-left">Ressource</th>
              <th className="px-4 py-3 text-left">IP</th>
              <th className="px-4 py-3 text-left">Détails</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {logs?.results.map(log => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm">
                  {new Date(log.timestamp).toLocaleString('fr-FR')}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-gray-400" />
                    <span className="font-medium">{log.user || 'Système'}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    {getActionIcon(log.action)}
                    <span className="capitalize">{log.action}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                    {log.resource_type}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600 font-mono">
                  {log.ip_address}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {log.details?.path}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

---

## 7. Tests Automatisés

### 7.1 Configuration Pytest

```bash
pip install pytest pytest-django pytest-cov factory-boy faker
```

```python
# bi_app/backend/pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = sigeti_bi.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --reuse-db
    --cov=analytics
    --cov-report=html
    --cov-report=term-missing
    --verbose

# bi_app/backend/analytics/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from analytics.models import MartOccupationZones, Alert
from faker import Faker

fake = Faker('fr_FR')

class ZoneFactory(DjangoModelFactory):
    class Meta:
        model = MartOccupationZones
    
    nom_zone = factory.LazyAttribute(lambda _: f"Zone {fake.city()}")
    code_zone = factory.Sequence(lambda n: f"Z{n:03d}")
    taux_occupation_pct = factory.LazyAttribute(lambda _: fake.random_int(0, 100))
    nombre_total_lots = factory.LazyAttribute(lambda _: fake.random_int(10, 100))
    lots_attribues = factory.LazyAttribute(lambda obj: fake.random_int(0, obj.nombre_total_lots))
    superficie_totale = factory.LazyAttribute(lambda _: fake.random_int(10000, 500000))

class AlertFactory(DjangoModelFactory):
    class Meta:
        model = Alert
    
    type = 'HIGH_OCCUPATION'
    severity = 'warning'
    entity_type = 'zone'
    entity_name = factory.LazyAttribute(lambda _: f"Zone {fake.city()}")
    message = factory.LazyAttribute(lambda obj: f"{obj.entity_name}: Occupation élevée")
    value = factory.LazyAttribute(lambda _: fake.random_int(70, 100))
    threshold = 90
    status = 'active'
```

```python
# bi_app/backend/analytics/tests/test_views.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .factories import ZoneFactory, AlertFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestOccupationAPI:
    
    def test_get_zones_list(self, authenticated_client):
        """Test récupération liste des zones"""
        # Créer des zones de test
        ZoneFactory.create_batch(5)
        
        response = authenticated_client.get('/api/occupation/zones/')
        
        assert response.status_code == 200
        assert len(response.data) == 5
    
    def test_get_zone_detail(self, authenticated_client):
        """Test récupération détails d'une zone"""
        zone = ZoneFactory.create(nom_zone="Zone Test")
        
        response = authenticated_client.get(f'/api/occupation/zones/{zone.id}/')
        
        assert response.status_code == 200
        assert response.data['nom_zone'] == "Zone Test"
    
    def test_filter_zones_by_occupation(self, authenticated_client):
        """Test filtrage par taux d'occupation"""
        ZoneFactory.create(taux_occupation_pct=50)
        ZoneFactory.create(taux_occupation_pct=90)
        
        response = authenticated_client.get('/api/occupation/zones/?min_occupation=80')
        
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['taux_occupation_pct'] >= 80
    
    def test_unauthorized_access(self, api_client):
        """Test accès non autorisé"""
        response = api_client.get('/api/occupation/zones/')
        
        assert response.status_code == 401

@pytest.mark.django_db
class TestAlerts:
    
    def test_check_occupation_alerts(self):
        """Test génération d'alertes"""
        from analytics.alerts import AlertManager
        
        zone_data = {
            'nom_zone': 'Zone Test',
            'taux_occupation_pct': 95
        }
        
        alerts = AlertManager.check_occupation_alerts(zone_data)
        
        assert len(alerts) > 0
        assert alerts[0].severity == 'critical'
    
    def test_alert_creation(self, authenticated_client):
        """Test création d'alerte"""
        alert = AlertFactory.create()
        
        response = authenticated_client.get(f'/api/alerts/{alert.id}/')
        
        assert response.status_code == 200
        assert response.data['status'] == 'active'
    
    def test_acknowledge_alert(self, authenticated_client):
        """Test acquittement d'alerte"""
        alert = AlertFactory.create()
        
        response = authenticated_client.post(f'/api/alerts/{alert.id}/acknowledge/')
        
        assert response.status_code == 200
        alert.refresh_from_db()
        assert alert.status == 'acknowledged'
```

```python
# bi_app/backend/analytics/tests/test_predictions.py
import pytest
from analytics.predictions import OccupationPredictor

class TestPredictions:
    
    def test_predict_next_month(self):
        """Test prédiction mois prochain"""
        historical_data = [
            {'month': '2024-01', 'occupation': 70},
            {'month': '2024-02', 'occupation': 72},
            {'month': '2024-03', 'occupation': 75},
            {'month': '2024-04', 'occupation': 78},
            {'month': '2024-05', 'occupation': 80},
            {'month': '2024-06', 'occupation': 82},
        ]
        
        prediction = OccupationPredictor.predict_next_month('Zone Test', historical_data)
        
        assert prediction is not None
        assert 'predicted_value' in prediction
        assert prediction['predicted_value'] > 80  # Tendance à la hausse
        assert prediction['trend'] == 'increasing'
    
    def test_detect_anomalies(self):
        """Test détection d'anomalies"""
        historical_data = [
            {'occupation': 70}, {'occupation': 72}, {'occupation': 71},
            {'occupation': 73}, {'occupation': 72}, {'occupation': 74},
        ]
        
        # Valeur normale
        normal_result = OccupationPredictor.detect_anomalies('Zone Test', 73, historical_data)
        assert not normal_result['is_anomaly']
        
        # Valeur anormale
        anomaly_result = OccupationPredictor.detect_anomalies('Zone Test', 95, historical_data)
        assert anomaly_result['is_anomaly']
        assert anomaly_result['severity'] == 'high'
```

### 7.2 Tests Frontend avec Vitest

```bash
cd bi_app/frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

```js
// bi_app/frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'src/tests/']
    }
  }
})

// bi_app/frontend/src/tests/setup.js
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

afterEach(() => {
  cleanup()
})

// bi_app/frontend/package.json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

```jsx
// bi_app/frontend/src/tests/components/StatsCard.test.jsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatsCard from '../../components/StatsCard'
import { TrendingUp } from 'lucide-react'

describe('StatsCard', () => {
  it('renders with correct values', () => {
    render(
      <StatsCard 
        title="Taux d'Occupation"
        value="75%"
        subtitle="↑ 5% ce mois"
        icon={TrendingUp}
      />
    )
    
    expect(screen.getByText("Taux d'Occupation")).toBeInTheDocument()
    expect(screen.getByText("75%")).toBeInTheDocument()
    expect(screen.getByText("↑ 5% ce mois")).toBeInTheDocument()
  })
  
  it('displays loading state', () => {
    render(<StatsCard title="Test" value="100" loading={true} />)
    
    expect(screen.queryByText("100")).not.toBeInTheDocument()
  })
})
```

```bash
# Lancer les tests backend
cd bi_app/backend
pytest

# Lancer les tests frontend
cd bi_app/frontend
npm run test

# Générer le rapport de couverture
pytest --cov-report=html
npm run test:coverage
```

---

Suite dans AMELIORATIONS_MODULES_FINAUX.md
