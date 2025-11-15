# 🚀 Migration vers le Nouveau Système de Sécurité

## ⚠️ IMPORTANT: Changements Breaking

Le système de sécurité a été renforcé. **L'authentification est maintenant OBLIGATOIRE** pour accéder à l'API.

---

## 📋 Étapes de Migration

### 1. Backend - Mise à jour

```bash
cd bi_app/backend

# Installer les nouveaux packages
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Initialiser les rôles
python manage.py init_roles
```

### 2. Configuration Admin

#### Assigner les rôles aux utilisateurs existants

```bash
# Via Django admin (recommandé)
python manage.py runserver
# Aller sur http://localhost:8000/admin/
# Connexion: admin / admin123
# Aller dans Users → Sélectionner un utilisateur → Modifier le profil → Choisir le rôle
```

#### Ou via shell Django

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from api.models_auth import Role

# Promouvoir un utilisateur en Admin
user = User.objects.get(username='votre_username')
admin_role = Role.objects.get(name='Admin')
user.profile.role = admin_role
user.profile.save()
print(f'✓ {user.username} est maintenant {user.profile.role.name}')
```

### 3. Frontend - Mise à jour

#### Installer les dépendances

```bash
cd bi_app/frontend
npm install axios jwt-decode
```

#### Créer le service d'authentification

Copier le code depuis `docs/SECURITY_GUIDE.md` section "Service d'Authentification (React)"

Fichiers à créer:
- `src/services/auth.js` - Service d'authentification
- `src/services/axios.js` - Intercepteur Axios avec JWT
- `src/components/Login.jsx` - Composant de connexion
- `src/components/PrivateRoute.jsx` - Protection de routes

#### Mettre à jour App.jsx

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import PrivateRoute from './components/PrivateRoute';
import Dashboard from './pages/Dashboard';
import AuthService from './services/auth';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        } />
        
        <Route path="/admin" element={
          <PrivateRoute requiredRole="Admin">
            <AdminPanel />
          </PrivateRoute>
        } />
        
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
```

#### Mettre à jour les appels API

**Avant:**
```javascript
fetch('http://localhost:8000/api/zones/map/')
  .then(res => res.json())
```

**Après:**
```javascript
import axiosInstance from './services/axios';

axiosInstance.get('/zones/map/')
  .then(res => res.data)
```

---

## 🔑 Endpoints Modifiés

### Nouvelles routes JWT

| Route | Méthode | Description |
|-------|---------|-------------|
| `/api/auth/jwt/login/` | POST | Connexion JWT |
| `/api/auth/jwt/refresh/` | POST | Rafraîchir token |
| `/api/auth/jwt/register/` | POST | Inscription |
| `/api/auth/jwt/me/` | GET | Profil utilisateur |
| `/api/auth/jwt/logout/` | POST | Déconnexion |

### Routes protégées (authentification requise)

- ✅ `/api/zones/map/` - Carte des zones
- ✅ `/api/zones/<id>/map/` - Détails zone
- ✅ `/api/financier/` - Données financières
- ✅ `/api/occupation/` - Occupation zones
- ✅ `/api/clients/` - Portefeuille clients
- ✅ `/api/operationnel/` - KPI opérationnels
- ✅ `/api/alerts/` - Alertes
- ✅ `/api/monitoring/*` - Monitoring (Admin uniquement)

---

## 🧪 Tests de Migration

### Test 1: Backend fonctionne

```bash
cd bi_app/backend
python test_security.py
```

**Résultat attendu:**
```
Test 1: Sans token (devrait échouer)
Status: 401
Message: {'detail': "Informations d'authentification non fournies."}

Test 2: Avec token (devrait réussir)
Token obtenu: eyJ...
Status: 200
✅ Zones: 13 zones chargées
```

### Test 2: Admin accessible

```bash
# Démarrer le serveur
python manage.py runserver

# Dans un navigateur
http://localhost:8000/admin/
Username: admin
Password: admin123
```

### Test 3: Frontend se connecte

```bash
cd bi_app/frontend
npm run dev
```

1. Ouvrir http://localhost:5174/
2. Devrait rediriger vers /login
3. Se connecter avec admin/admin123
4. Devrait afficher le dashboard

---

## 📊 Rôles et Permissions

### Rôles Créés

| Rôle | Lecture | Écriture | Suppression | Admin |
|------|---------|----------|-------------|-------|
| **Admin** | ✅ | ✅ | ✅ | ✅ |
| **Gestionnaire** | ✅ | ✅ | ❌ | ❌ |
| **Lecteur** | ✅ | ❌ | ❌ | ❌ |

### Assignation par défaut

- Tous les utilisateurs existants: **Lecteur**
- Nouveaux utilisateurs: **Lecteur**
- À promouvoir manuellement: **Admin**, **Gestionnaire**

---

## 🔒 Rate Limiting

### Limites Actives

- **Login**: 5 tentatives/minute par IP
- **Register**: 3 inscriptions/heure par IP
- **API anonyme**: 100 requêtes/heure
- **API authentifié**: 1000 requêtes/heure
- **Zones Map**: 100 requêtes/minute par utilisateur

### Désactiver temporairement (dev uniquement)

```python
# settings.py
REST_FRAMEWORK = {
    # Commenter ces lignes:
    # 'DEFAULT_THROTTLE_CLASSES': [...],
    # 'DEFAULT_THROTTLE_RATES': {...},
}
```

---

## 🐛 Dépannage

### Erreur: "Informations d'authentification non fournies"

**Solution:** Ajouter le header Authorization
```javascript
headers: {
  'Authorization': `Bearer ${token}`
}
```

### Erreur: "Token has expired"

**Solution:** Rafraîchir le token
```javascript
POST /api/auth/jwt/refresh/
{ "refresh": "votre_refresh_token" }
```

### Erreur: "User has no profile"

**Solution:** Initialiser les rôles
```bash
python manage.py init_roles
```

### Frontend ne se connecte pas

**Solution:** Vérifier CORS dans settings.py
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:5174',
]
```

---

## 🎯 Checklist de Migration

### Backend
- [ ] `pip install -r requirements.txt`
- [ ] `python manage.py migrate`
- [ ] `python manage.py init_roles`
- [ ] `python test_security.py` passe
- [ ] Admin accessible sur /admin/
- [ ] Rôles assignés aux utilisateurs

### Frontend
- [ ] `npm install axios jwt-decode`
- [ ] Service auth.js créé
- [ ] Intercepteur axios.js créé
- [ ] Login.jsx créé
- [ ] PrivateRoute.jsx créé
- [ ] Routes protégées configurées
- [ ] Tous les appels API utilisent axiosInstance
- [ ] Tests de connexion réussis

### Production (avant déploiement)
- [ ] SECRET_KEY changée
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configuré
- [ ] HTTPS activé
- [ ] Password admin changé
- [ ] CORS restreint au domaine production

---

## 📞 Support

Si vous rencontrez des problèmes:

1. Vérifier les logs Django: `tail -f logs/dbt.log.5`
2. Vérifier la console navigateur (F12)
3. Tester avec curl (voir SECURITY_GUIDE.md)
4. Vérifier que Redis tourne (si utilisé pour cache)

---

## ✅ Validation Finale

```bash
# Test complet
cd bi_app/backend
python manage.py test

# Vérifier les migrations
python manage.py showmigrations

# Compter les utilisateurs par rôle
python manage.py shell -c "from api.models_auth import Role; [print(f'{r.name}: {r.users.count()}') for r in Role.objects.all()]"
```

**Résultat attendu:**
```
Admin: 1
Gestionnaire: 0
Lecteur: 5
```

---

## 🎉 Migration Terminée !

Votre API est maintenant sécurisée avec:
- ✅ JWT avec refresh tokens
- ✅ Rate limiting
- ✅ Système de rôles
- ✅ IsAuthenticated par défaut
- ✅ Token blacklist

**Prochaines étapes:** Voir `docs/SECURITY_GUIDE.md` pour l'utilisation avancée
