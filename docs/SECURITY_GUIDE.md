# 🔒 Guide de Sécurité & Authentification SIGETI BI

## ✅ Implémentation Complète

### 1. Système d'Authentification JWT

#### Configuration
- **JWT Access Token**: Valide 1 heure
- **JWT Refresh Token**: Valide 7 jours
- **Rotation automatique**: Nouveau refresh token à chaque refresh
- **Blacklist**: Tokens révoqués après rotation
- **Rate Limiting**: Protection contre les attaques par force brute

#### Endpoints JWT

##### 🔑 Connexion
```http
POST /api/auth/jwt/login/
Content-Type: application/json

{
  "username": "votre_username",
  "password": "votre_password"
}
```

**Réponse:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@sigeti.com",
    "first_name": "Admin",
    "last_name": "SIGETI",
    "role": "Admin",
    "department": "IT"
  }
}
```

**Rate Limit**: 5 tentatives/minute par IP

##### 🔄 Rafraîchir le Token
```http
POST /api/auth/jwt/refresh/
Content-Type: application/json
{
  "refresh": "votre_refresh_token"
}
```

**Réponse:**
```json
{
  "access": "nouveau_access_token",
  "refresh": "nouveau_refresh_token"
}
```

##### 📝 Inscription
```http
POST /api/auth/jwt/register/
Content-Type: application/json

{
  "username": "nouveau_user",
  "email": "user@sigeti.com",
  "password": "motdepasse_securise",
  "first_name": "Prénom",
  "last_name": "Nom"
}
```

**Rate Limit**: 3 inscriptions/heure par IP

##### 🚪 Déconnexion
```http
POST /api/auth/jwt/logout/
Authorization: Bearer votre_access_token
Content-Type: application/json

{
  "refresh": "votre_refresh_token"
}
```

##### 👤 Profil Utilisateur
```http
GET /api/auth/jwt/me/
Authorization: Bearer votre_access_token
```

##### ✏️ Mise à jour Profil
```http
PUT /api/auth/jwt/profile/
Authorization: Bearer votre_access_token
Content-Type: application/json

{
  "first_name": "Nouveau Prénom",
  "department": "Finance",
  "phone": "+225 07 XX XX XX XX"
}
```

---

### 2. Système de Rôles

#### Rôles Disponibles

| Rôle | Permissions | Description |
|------|-------------|-------------|
| **Admin** | ✅ Lecture ✅ Écriture ✅ Suppression ✅ Gestion utilisateurs ✅ Logs | Administrateur système complet |
| **Gestionnaire** | ✅ Lecture ✅ Écriture ❌ Suppression | Peut consulter et modifier les données |
| **Lecteur** | ✅ Lecture ❌ Écriture ❌ Suppression | Accès en lecture seule |

#### Permissions Personnalisées

```python
from api.permissions import IsAdmin, IsGestionnaire, IsLecteur

# Dans vos views
@permission_classes([IsAdmin])  # Admin uniquement
@permission_classes([IsGestionnaire])  # Admin + Gestionnaire
@permission_classes([IsLecteur])  # Tous les rôles (lecture)
```

#### Gestion des Rôles via Django Admin

1. Accéder à `/admin/`
2. **Utilisateurs** → Sélectionner un utilisateur
3. **Profil** → Modifier le rôle
4. Sauvegarder

#### Commande de Gestion
```bash
# Initialiser les rôles (déjà fait)
python manage.py init_roles

# Créer un super admin
python manage.py createsuperuser
```

---

### 3. Rate Limiting

#### Limites Globales (REST Framework)
- **Utilisateurs anonymes**: 100 requêtes/heure
- **Utilisateurs authentifiés**: 1000 requêtes/heure

#### Limites Spécifiques (django-ratelimit)
- **Login**: 5 tentatives/minute par IP
- **Register**: 3 inscriptions/heure par IP
- **API Zones Map**: 100 requêtes/minute par utilisateur

#### Configuration
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}
```

---

### 4. Utilisation Depuis le Frontend

#### Installation
```bash
npm install axios jwt-decode
```

#### Service d'Authentification (React)
```javascript
// src/services/auth.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

class AuthService {
  async login(username, password) {
    const response = await axios.post(`${API_URL}/auth/jwt/login/`, {
      username,
      password
    });
    
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  }
  
  logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    axios.post(`${API_URL}/auth/jwt/logout/`, {
      refresh: refreshToken
    }, {
      headers: { Authorization: `Bearer ${this.getAccessToken()}` }
    });
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }
  
  getAccessToken() {
    return localStorage.getItem('access_token');
  }
  
  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
  
  isAuthenticated() {
    return !!this.getAccessToken();
  }
}

export default new AuthService();
```

#### Intercepteur Axios
```javascript
// src/services/axios.js
import axios from 'axios';
import AuthService from './auth';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api'
});

// Ajouter le token à chaque requête
axiosInstance.interceptors.request.use(
  (config) => {
    const token = AuthService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Rafraîchir le token si expiré
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:8000/api/auth/jwt/refresh/',
          { refresh: refreshToken }
        );
        
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        AuthService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

#### Composant de Connexion (React)
```jsx
// src/components/Login.jsx
import React, { useState } from 'react';
import AuthService from '../services/auth';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      await AuthService.login(username, password);
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur de connexion');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h2>Connexion SIGETI BI</h2>
      
      {error && <div className="error">{error}</div>}
      
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      
      <button type="submit">Se connecter</button>
    </form>
  );
}
```

#### Protection de Routes (React Router)
```jsx
// src/components/PrivateRoute.jsx
import { Navigate } from 'react-router-dom';
import AuthService from '../services/auth';

export default function PrivateRoute({ children, requiredRole }) {
  const user = AuthService.getUser();
  
  if (!AuthService.isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
}

// Usage
<Route path="/admin" element={
  <PrivateRoute requiredRole="Admin">
    <AdminDashboard />
  </PrivateRoute>
} />
```

---

### 5. Tests de Sécurité

#### Test de Connexion
```bash
curl -X POST http://localhost:8000/api/auth/jwt/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### Test d'Accès Protégé
```bash
# Sans token (devrait échouer 401)
curl http://localhost:8000/api/zones/map/

# Avec token (devrait réussir)
curl http://localhost:8000/api/zones/map/ \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN"
```

#### Test de Rate Limiting
```bash
# Tester 6 connexions rapides (la 6ème devrait échouer)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/jwt/login/ \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"wrong"}'
done
```

---

### 6. Commandes Utiles

```bash
# Créer un utilisateur admin
python manage.py createsuperuser

# Initialiser les rôles
python manage.py init_roles

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Lancer le serveur
python manage.py runserver
```

---

### 7. Sécurité en Production

#### ⚠️ CRITIQUES À CHANGER

1. **SECRET_KEY**: Générer une nouvelle clé
   ```python
   # settings.py
   SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'votre-cle-super-secrete')
   ```

2. **DEBUG**: Désactiver en production
   ```python
   DEBUG = False
   ```

3. **ALLOWED_HOSTS**: Configurer les domaines
   ```python
   ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']
   ```

4. **CORS**: Restreindre les origines
   ```python
   CORS_ALLOWED_ORIGINS = [
       'https://votre-frontend.com',
   ]
   ```

5. **HTTPS**: Forcer HTTPS
   ```python
   SECURE_SSL_REDIRECT = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

---

### 8. Monitoring

#### Logs d'Authentification
- Les connexions sont enregistrées avec l'IP
- Accessible via `/api/monitoring/logs/` (Admin uniquement)

#### Métriques
- Nombre de connexions réussies/échouées
- Rate limiting déclenchés
- Tokens révoqués

---

## 🎯 Résumé

✅ **Fait:**
- JWT avec refresh tokens
- Rate limiting sur endpoints sensibles
- Système de rôles (Admin, Gestionnaire, Lecteur)
- Permissions personnalisées
- IsAuthenticated par défaut
- Blacklist tokens
- Admin Django configuré

⚠️ **À faire en production:**
- Changer SECRET_KEY
- DEBUG = False
- Configurer HTTPS
- Backup base de données
- Monitoring avancé

**Credentials par défaut (À CHANGER!):**
- Username: `admin`
- Password: `admin123`
