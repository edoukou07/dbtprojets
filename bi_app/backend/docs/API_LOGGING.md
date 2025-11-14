# API Request Logging System

## 📋 Vue d'ensemble

Système complet de logging des requêtes API avec suivi des performances, erreurs, et analytics en temps réel.

### ✨ Fonctionnalités

- ✅ **Logging automatique** de toutes les requêtes API
- ✅ **Suivi des performances** (temps de réponse en millisecondes)
- ✅ **Tracking des erreurs** avec stack traces complètes
- ✅ **Détection des requêtes lentes** (>1 seconde)
- ✅ **Métriques en temps réel** via cache Redis
- ✅ **Suivi du cache** (HIT/MISS)
- ✅ **Rotation automatique** des fichiers logs (10MB max)
- ✅ **Formats multiples** (texte lisible + JSON)
- ✅ **Endpoints de monitoring** pour admin
- ✅ **Analytics avancés** (top endpoints, temps moyens, taux d'erreurs)

---

## 📊 Résultats des tests

```
✓ 44 requêtes loggées automatiquement
✓ Cache hit rate: 90%
✓ Formats: texte (6KB) + JSON (20KB)
✓ Erreurs 404 détectées et loggées
✓ Temps de réponse: 0-142ms
✓ Aucune erreur système
```

---

## 📂 Architecture

### Structure des fichiers

```
bi_app/backend/
├── logs/                                    # Répertoire auto-créé
│   ├── api_requests.log                    # Logs texte lisibles (10MB max, 10 backups)
│   ├── api_requests.json                   # Logs JSON parsables (10MB max, 5 backups)
│   ├── errors.log                          # Erreurs uniquement (10MB max, 10 backups)
│   └── slow_requests.log                   # Requêtes >1s (5MB max, 5 backups)
│
├── api/
│   ├── middleware.py                       # Middleware de logging
│   └── logging_views.py                    # Endpoints de monitoring
│
├── sigeti_bi/
│   └── settings.py                         # Configuration LOGGING
│
└── test_logging.py                         # Script de test
```

### Composants

1. **APIRequestLoggingMiddleware** (`api/middleware.py`)
   - Capture automatiquement toutes les requêtes `/api/*`
   - Calcule les temps de réponse
   - Détecte les requêtes lentes
   - Update les métriques Redis

2. **Logging Views** (`api/logging_views.py`)
   - 6 endpoints de monitoring (admin uniquement)
   - Lecture et analyse des logs
   - Métriques en temps réel

3. **Configuration LOGGING** (`sigeti_bi/settings.py`)
   - 4 rotating file handlers
   - 3 formatters (verbose, simple, JSON)
   - 4 loggers spécialisés

---

## 🔧 Configuration

### Settings Django

```python
# Répertoire des logs (auto-créé)
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Configuration LOGGING complète
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'verbose': {...},
        'simple': {...},
        'json': {...}
    },
    
    'handlers': {
        'api_file': {...},        # api_requests.log
        'api_json': {...},        # api_requests.json
        'error_file': {...},      # errors.log
        'slow_requests_file': {...}  # slow_requests.log
    },
    
    'loggers': {
        'api.requests': {...},
        'api.errors': {...},
        'django': {...}
    }
}
```

### Middleware

```python
# sigeti_bi/settings.py
MIDDLEWARE = [
    # ... autres middlewares
    'api.middleware.APIRequestLoggingMiddleware',  # À la fin
]
```

---

## 📝 Format des logs

### Format texte lisible (api_requests.log)

```
INFO 2025-11-14 18:26:34,983 middleware INFO - GET /api/occupation/summary/ - Status: 200 - Time: 142.67ms - User: AnonymousUser - Cache: MISS

WARNING 2025-11-14 18:26:35,195 middleware WARNING - GET /api/occupation/999999/ - Status: 404 - Time: 5.27ms - User: AnonymousUser - Cache: N/A
```

**Structure:**
- `LEVEL`: INFO, WARNING, ERROR
- `Timestamp`: Date et heure précise
- `Module`: middleware
- `Message`: Méthode, path, status, temps, user, cache

### Format JSON (api_requests.json)

```json
{
  "asctime": "2025-11-14 18:26:34,983",
  "levelname": "INFO",
  "name": "api.requests",
  "message": "INFO - GET /api/occupation/summary/ - Status: 200 - Time: 142.67ms",
  "data": {
    "method": "GET",
    "path": "/api/occupation/summary/",
    "query_params": {},
    "status_code": 200,
    "response_time_ms": 142.67,
    "user": "AnonymousUser",
    "user_id": null,
    "ip_address": "127.0.0.1",
    "user_agent": "python-requests/2.32.3",
    "cache_status": "MISS",
    "response_size_bytes": 156
  }
}
```

**Champs data:**
- `method`: GET, POST, PUT, PATCH, DELETE
- `path`: Chemin de l'endpoint
- `query_params`: Paramètres URL (dict)
- `status_code`: Code HTTP (200, 404, 500, etc.)
- `response_time_ms`: Temps de réponse en millisecondes
- `user`: Nom d'utilisateur (ou AnonymousUser)
- `user_id`: ID utilisateur (ou null)
- `ip_address`: IP client (X-Forwarded-For ou REMOTE_ADDR)
- `user_agent`: User-Agent du client
- `cache_status`: HIT, MISS, N/A
- `response_size_bytes`: Taille de la réponse

### Logs d'erreurs (errors.log)

```
ERROR 2025-11-14 18:30:15,234 middleware Exception in request processing
Traceback (most recent call last):
  File "api/middleware.py", line 45, in process_request
    ...
ValueError: Invalid data format
```

---

## 🔍 Endpoints de monitoring

Tous les endpoints requièrent **authentification admin** (`IsAdminUser`).

### 1. Métriques en temps réel

```bash
GET /api/monitoring/metrics/
```

**Réponse:**
```json
{
  "total_requests": 44,
  "total_errors": 0,
  "by_status": {
    "200": 40,
    "404": 4
  },
  "error_rate": 0.0,
  "cache_enabled": true
}
```

**Utilisation:**
- Dashboard de monitoring
- Alerting sur error_rate
- Vérification cache

---

### 2. Logs récents

```bash
GET /api/monitoring/logs/?limit=50&level=INFO&search=occupation
```

**Paramètres:**
- `limit`: Nombre de lignes (défaut: 50, max: 500)
- `level`: Filtre par niveau (INFO, WARNING, ERROR)
- `search`: Recherche texte

**Réponse:**
```json
{
  "logs": [
    "INFO 2025-11-14 18:26:34,983 middleware INFO - GET /api/occupation/summary/ ...",
    "..."
  ],
  "count": 10,
  "total_lines": 44
}
```

**Utilisation:**
- Debugging en temps réel
- Recherche d'endpoints spécifiques
- Analyse des patterns

---

### 3. Logs d'erreurs

```bash
GET /api/monitoring/errors/?limit=20
```

**Paramètres:**
- `limit`: Nombre d'erreurs (défaut: 20, max: 100)

**Réponse:**
```json
{
  "errors": [
    "ERROR 2025-11-14 18:30:15,234 middleware Exception in request processing\nTraceback...",
    "..."
  ],
  "count": 5,
  "total_errors": 5
}
```

**Utilisation:**
- Monitoring des erreurs
- Debugging d'exceptions
- Analyse des stack traces

---

### 4. Requêtes lentes

```bash
GET /api/monitoring/slow/?limit=20
```

**Paramètres:**
- `limit`: Nombre de requêtes (défaut: 20, max: 100)

**Réponse:**
```json
{
  "slow_requests": [
    "WARNING 2025-11-14 18:26:34,983 middleware Slow request: GET /api/heavy/operation/ - Time: 1534.23ms",
    "..."
  ],
  "count": 3,
  "total": 3
}
```

**Utilisation:**
- Identification des bottlenecks
- Optimisation des performances
- Monitoring des SLA

---

### 5. Analytics avancés

```bash
GET /api/monitoring/analytics/
```

**Réponse:**
```json
{
  "total_requests_analyzed": 1000,
  "avg_response_time_ms": 45.67,
  "cache_hit_rate": 85.5,
  "top_endpoints": [
    {
      "endpoint": "/api/occupation/summary/",
      "count": 250,
      "avg_time_ms": 12.34
    }
  ],
  "slowest_endpoints": [
    {
      "endpoint": "/api/heavy/operation/",
      "avg_time_ms": 1234.56,
      "count": 10
    }
  ],
  "status_distribution": {
    "200": 950,
    "404": 45,
    "500": 5
  },
  "errors_by_type": {
    "DoesNotExist": 30,
    "ValidationError": 10,
    "DatabaseError": 5
  }
}
```

**Utilisation:**
- Dashboard de performances
- Identification des endpoints à optimiser
- Analyse des patterns d'utilisation
- Reporting

---

### 6. Effacer les métriques

```bash
POST /api/monitoring/clear-metrics/
```

**Réponse:**
```json
{
  "message": "All metrics cleared successfully",
  "cleared_keys": 156
}
```

**Utilisation:**
- Reset après maintenance
- Nettoyage périodique
- Tests de charge

---

## 🚀 Utilisation

### Test manuel

```bash
# Tester le système
cd bi_app/backend
python test_logging.py

# Vérifier les logs
cat logs/api_requests.log
cat logs/api_requests.json
cat logs/errors.log
```

### Intégration dans le code

Le logging est **automatique** pour tous les endpoints `/api/*`. Aucune modification du code nécessaire.

```python
# Aucun code supplémentaire requis !
# Le middleware capture automatiquement:

@api_view(['GET'])
def my_endpoint(request):
    # Votre code ici
    return Response(data)

# Loggera automatiquement:
# - Temps de réponse
# - Status code
# - User
# - Cache status
# - Erreurs éventuelles
```

### Monitoring en production

```python
# Script de monitoring (exemple)
import requests

response = requests.get(
    'http://your-domain.com/api/monitoring/metrics/',
    headers={'Authorization': 'Token YOUR_ADMIN_TOKEN'}
)

metrics = response.json()

if metrics['error_rate'] > 5.0:
    send_alert(f"High error rate: {metrics['error_rate']}%")

if metrics['total_errors'] > 100:
    send_alert(f"Total errors: {metrics['total_errors']}")
```

---

## 📈 Métriques trackées

### Cache Redis

Le middleware maintient les compteurs suivants dans Redis:

```python
# Clés Redis
api_requests_total           # Total de requêtes
api_requests_errors          # Total d'erreurs
api_requests_status_200      # Requêtes par status code
api_requests_status_404
api_requests_status_500
# ... autres status codes

api_endpoint_/api/occupation/summary/  # Compteur par endpoint
api_endpoint_/api/clients/summary/
# ... autres endpoints
```

### Calculs automatiques

- **Error rate**: `(total_errors / total_requests) * 100`
- **Cache hit rate**: `(cache_hits / total_requests) * 100`
- **Avg response time**: Moyenne sur dernières 1000 requêtes
- **Top endpoints**: Classement par nombre de requêtes
- **Slowest endpoints**: Classement par temps de réponse moyen

---

## 🔒 Sécurité

### Permissions

```python
# Tous les endpoints de monitoring
@permission_classes([IsAdminUser])
def monitoring_endpoint(request):
    # Seuls les admins ont accès
    pass
```

### Données sensibles

Le middleware **n'enregistre PAS**:
- ❌ Mots de passe
- ❌ Tokens d'authentification
- ❌ Données sensibles dans les body (limite 1000 chars)
- ❌ Headers sensibles (Authorization, Cookie)

Le middleware **enregistre**:
- ✅ Méthode HTTP
- ✅ Path et query params
- ✅ Status code
- ✅ Temps de réponse
- ✅ User et IP
- ✅ User-Agent
- ✅ Aperçu du body (POST/PUT/PATCH)

---

## 🛠️ Maintenance

### Rotation des logs

Automatique via `RotatingFileHandler`:

```python
# Configuration
'api_file': {
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': LOGS_DIR / 'api_requests.log',
    'maxBytes': 10 * 1024 * 1024,  # 10 MB
    'backupCount': 10,              # 10 fichiers
    'formatter': 'verbose',
}
```

**Résultat:**
- `api_requests.log` (fichier actif)
- `api_requests.log.1` (backup 1)
- `api_requests.log.2` (backup 2)
- ... jusqu'à `api_requests.log.10`

### Nettoyage manuel

```bash
# Supprimer les vieux logs
rm logs/api_requests.log.*
rm logs/errors.log.*

# Vider les métriques cache
curl -X POST http://localhost:8000/api/monitoring/clear-metrics/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Monitoring de l'espace disque

```bash
# Vérifier la taille des logs
du -sh logs/
du -h logs/*

# Exemple sortie:
# 50M    logs/
# 10M    logs/api_requests.log
# 20M    logs/api_requests.json
# 5M     logs/errors.log
```

---

## 🐛 Troubleshooting

### Les logs ne sont pas créés

1. **Vérifier le middleware:**
   ```python
   # settings.py
   MIDDLEWARE = [
       # ...
       'api.middleware.APIRequestLoggingMiddleware',
   ]
   ```

2. **Vérifier les permissions:**
   ```bash
   # Le répertoire logs doit être writable
   chmod 755 logs/
   ```

3. **Vérifier les erreurs:**
   ```bash
   # Django logs
   python manage.py runserver
   # Chercher les erreurs de logging
   ```

### Les métriques sont vides

1. **Vérifier Redis:**
   ```python
   from django.core.cache import cache
   cache.set('test', 'value')
   print(cache.get('test'))  # Doit afficher 'value'
   ```

2. **Vérifier la configuration:**
   ```python
   # settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           # ...
       }
   }
   ```

### Les endpoints retournent 401

C'est **normal** ! Les endpoints de monitoring requièrent:
- ✅ Authentification admin
- ✅ Header `Authorization: Token YOUR_TOKEN`

```bash
# Créer un admin
python manage.py createsuperuser

# Obtenir le token
python manage.py drf_create_token your_admin_username

# Tester
curl http://localhost:8000/api/monitoring/metrics/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## 📊 Dashboard recommandé

### Grafana + Prometheus

Pour une visualisation avancée, intégrez avec Grafana:

1. **Exporter les métriques:**
   ```python
   # Créer un endpoint Prometheus
   from prometheus_client import Counter, Histogram
   
   request_count = Counter('api_requests_total', 'Total requests')
   request_duration = Histogram('api_request_duration_seconds', 'Request duration')
   ```

2. **Configurer Grafana:**
   - Source: Prometheus
   - Dashboards: API metrics, Error rates, Response times
   - Alerting: Error rate > 5%, Slow requests > 100/h

### ELK Stack (Elasticsearch, Logstash, Kibana)

Pour analyse des logs JSON:

1. **Logstash input:**
   ```conf
   input {
     file {
       path => "/path/to/logs/api_requests.json"
       codec => json
     }
   }
   ```

2. **Kibana visualizations:**
   - Time series: Requests per minute
   - Pie chart: Status code distribution
   - Table: Top endpoints
   - Heat map: Response times

---

## ✅ Checklist de déploiement

- [ ] Middleware activé dans `settings.py`
- [ ] Répertoire `logs/` créé avec permissions appropriées
- [ ] Redis configuré et accessible
- [ ] Endpoints de monitoring testés
- [ ] Authentification admin configurée
- [ ] Rotation des logs vérifiée
- [ ] Monitoring de l'espace disque configuré
- [ ] Alerting sur error_rate configuré
- [ ] Documentation partagée avec l'équipe
- [ ] Tests de charge effectués

---

## 📚 Ressources

- [Documentation Django Logging](https://docs.djangoproject.com/en/4.2/topics/logging/)
- [python-json-logger](https://github.com/madzak/python-json-logger)
- [Django Redis Cache](https://github.com/jazzband/django-redis)
- [RotatingFileHandler](https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler)

---

## 🎯 Prochaines améliorations

- [ ] Intégration Sentry pour alerting en temps réel
- [ ] Dashboard Grafana avec métriques Prometheus
- [ ] Export des logs vers S3/Azure Blob
- [ ] Analyse ML des patterns de requêtes
- [ ] Détection d'anomalies automatique
- [ ] Rate limiting basé sur les métriques
- [ ] A/B testing tracking
- [ ] User behavior analytics

---

**Créé le:** 14 Novembre 2025  
**Version:** 1.0  
**Auteur:** DWH_SIG Team  
**License:** MIT
