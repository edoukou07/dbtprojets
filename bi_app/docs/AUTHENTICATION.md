# 🔐 Système d'Authentification SIGETI BI

## Vue d'ensemble

Le système d'authentification de SIGETI BI utilise une architecture moderne avec :
- **Backend** : Django REST Framework + Token Authentication
- **Frontend** : React + Context API pour la gestion d'état
- **Sécurité** : Routes protégées, tokens JWT, sessions sécurisées

---

## 📁 Fichiers créés

### Frontend (React)

1. **`src/pages/Login.jsx`**
   - Page de connexion moderne avec design split-screen
   - Formulaire responsive avec validation
   - Affichage des erreurs
   - Animation de chargement

2. **`src/contexts/AuthContext.jsx`**
   - Gestion globale de l'état d'authentification
   - Fonctions `login()` et `logout()`
   - Persistance dans localStorage
   - Hook `useAuth()` pour accès facile

3. **`src/components/ProtectedRoute.jsx`**
   - Composant pour protéger les routes
   - Redirection automatique vers `/login` si non authentifié
   - Écran de chargement pendant la vérification

### Backend (Django)

4. **`api/views.py`** (modifié)
   - Ajout de 3 endpoints d'authentification :
     - `POST /api/auth/login/` - Connexion
     - `POST /api/auth/logout/` - Déconnexion
     - `GET /api/auth/user/` - Informations utilisateur

5. **`api/urls.py`** (modifié)
   - Routes d'authentification ajoutées

6. **`sigeti_bi/settings.py`** (modifié)
   - Ajout de `rest_framework.authtoken`
   - Configuration de TokenAuthentication
   - Permissions par défaut : `IsAuthenticated`

7. **`create_test_users.py`**
   - Script pour créer des utilisateurs de démonstration

8. **`setup_auth.ps1`**
   - Script PowerShell pour installer les dépendances et créer les utilisateurs

---

## 🚀 Installation

### Étape 1 : Installer les dépendances backend

```powershell
cd bi_app\backend
.\setup_auth.ps1
```

Ce script va :
- ✅ Installer `djangorestframework-authtoken`
- ✅ Créer 4 utilisateurs de test

### Étape 2 : Appliquer les migrations Django

```powershell
python manage.py migrate
```

### Étape 3 : Redémarrer les serveurs

```powershell
# Depuis la racine du projet
cd ..\..
.\bi_app\start.ps1
```

---

## 👥 Comptes de test

| Rôle | Email | Mot de passe | Permissions |
|------|-------|--------------|-------------|
| **Administrateur** | admin@sigeti.ci | admin123 | Superuser, Staff |
| **Finance** | finance@sigeti.ci | finance123 | Utilisateur standard |
| **Opérations** | ops@sigeti.ci | ops123 | Utilisateur standard |
| **Direction** | direction@sigeti.ci | direction123 | Utilisateur standard |

---

## 🔌 API Endpoints

### Authentification

#### 1. Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "admin@sigeti.ci",
  "password": "admin123"
}
```

**Réponse (200 OK)** :
```json
{
  "success": true,
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@sigeti.ci",
    "first_name": "Admin",
    "last_name": "SIGETI",
    "is_staff": true
  }
}
```

**Erreur (401 Unauthorized)** :
```json
{
  "error": "Email ou mot de passe incorrect"
}
```

#### 2. Logout
```http
POST /api/auth/logout/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Réponse (200 OK)** :
```json
{
  "success": true
}
```

#### 3. Informations utilisateur courant
```http
GET /api/auth/user/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Réponse (200 OK)** :
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@sigeti.ci",
  "first_name": "Admin",
  "last_name": "SIGETI",
  "is_staff": true
}
```

---

## 🔐 Flux d'authentification

### 1. Login
```
Utilisateur
  │
  ├─→ Saisit email/password dans Login.jsx
  │
  ├─→ POST /api/auth/login/
  │
  ├─→ Django vérifie les credentials
  │
  ├─→ Retourne token + user data
  │
  ├─→ React stocke dans localStorage
  │     - localStorage.setItem('token', token)
  │     - localStorage.setItem('user', JSON.stringify(user))
  │
  └─→ Redirection vers /dashboard
```

### 2. Accès aux routes protégées
```
Utilisateur
  │
  ├─→ Tente d'accéder à /dashboard
  │
  ├─→ ProtectedRoute.jsx vérifie isAuthenticated
  │
  ├─→ Si OK : Affiche le composant
  │
  └─→ Si KO : Redirige vers /login
```

### 3. Appels API authentifiés
```jsx
// Exemple dans les composants React
const token = localStorage.getItem('token');

fetch('http://localhost:8000/api/financier/', {
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
})
```

### 4. Logout
```
Utilisateur
  │
  ├─→ Clique sur bouton déconnexion (Layout.jsx)
  │
  ├─→ POST /api/auth/logout/
  │
  ├─→ Django supprime le token
  │
  ├─→ React supprime localStorage
  │     - localStorage.removeItem('token')
  │     - localStorage.removeItem('user')
  │
  └─→ Redirection vers /login
```

---

## 🎨 Page de connexion - Caractéristiques

### Design
- ✅ Split-screen moderne (info à gauche, formulaire à droite)
- ✅ Gradient bleu/violet professionnel
- ✅ Animations fluides (hover, focus, loading)
- ✅ Responsive (mobile, tablette, desktop)
- ✅ Mode sombre du fond avec effets glassmorphism

### UX
- ✅ Affichage/masquage du mot de passe (icône œil)
- ✅ Messages d'erreur clairs et contextuels
- ✅ Loading spinner pendant la connexion
- ✅ Champs pré-remplis suggérés pour la démo
- ✅ Case "Se souvenir de moi"
- ✅ Lien "Mot de passe oublié"

### Sécurité
- ✅ Validation côté client (email requis, format)
- ✅ Validation côté serveur (Django)
- ✅ Protection CSRF (Django)
- ✅ HTTPS recommandé en production
- ✅ Token expiré automatiquement à la déconnexion

---

## 🛡️ Protection des routes

### Routes publiques
- `/login` - Page de connexion

### Routes protégées (nécessitent authentification)
- `/dashboard` - Accueil
- `/financier` - Dashboard financier
- `/occupation` - Dashboard occupation
- `/clients` - Dashboard clients
- `/operationnel` - Dashboard opérationnel

### Comportement
- ✅ Utilisateur non connecté → Redirige vers `/login`
- ✅ Utilisateur connecté → Accès autorisé
- ✅ Token invalide/expiré → Déconnexion automatique
- ✅ Persistance de la session (localStorage)

---

## 🔧 Personnalisation

### Ajouter un nouvel utilisateur manuellement

```python
# Dans Django shell
python manage.py shell

from django.contrib.auth.models import User

user = User.objects.create_user(
    username='nouveau',
    email='nouveau@sigeti.ci',
    password='motdepasse123',
    first_name='Prénom',
    last_name='Nom'
)
```

### Modifier la durée de validité du token

```python
# Dans settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# Token n'expire jamais par défaut
# Pour expiration automatique, utiliser JWT :
# pip install djangorestframework-simplejwt
```

### Changer le design de la page de connexion

Modifiez `src/pages/Login.jsx` :
- Couleurs : `from-blue-600 to-purple-600`
- Logo : Remplacez `<Building2 />` par votre logo
- Texte : Modifiez les titres et descriptions

---

## 📊 Statistiques de sécurité

### Endpoints protégés
- ✅ Tous les endpoints `/api/*` nécessitent authentification
- ❌ Exception : `/api/auth/login/` (AllowAny)

### Permissions par rôle (à implémenter)

```python
# Exemple de permissions personnalisées
class IsFinanceUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Finance').exists()

# Dans les views
class FinancialViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsFinanceUser]
```

---

## 🚨 Troubleshooting

### Erreur : "Token not provided"
```
Solution : Vérifier que le header Authorization est présent
fetch(url, {
  headers: { 'Authorization': `Token ${token}` }
})
```

### Erreur : "Invalid token"
```
Solution : 
1. Vérifier que le token existe dans la DB
2. Supprimer localStorage et se reconnecter
3. Vérifier que rest_framework.authtoken est dans INSTALLED_APPS
```

### Erreur : "CORS policy"
```
Solution : Vérifier CORS_ALLOWED_ORIGINS dans settings.py
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']
```

### Utilisateurs de test non créés
```
Solution :
cd bi_app\backend
python manage.py shell < create_test_users.py
```

---

## ✅ Checklist de production

Avant de déployer en production :

- [ ] Changer `SECRET_KEY` dans settings.py
- [ ] Mettre `DEBUG = False`
- [ ] Configurer ALLOWED_HOSTS
- [ ] Utiliser HTTPS
- [ ] Configurer JWT avec expiration
- [ ] Implémenter refresh token
- [ ] Ajouter rate limiting (django-ratelimit)
- [ ] Configurer logging des authentifications
- [ ] Activer 2FA (two-factor authentication)
- [ ] Mettre en place password reset
- [ ] Configurer email pour notifications
- [ ] Audit des permissions par rôle

---

## 📚 Ressources

- [Django REST Framework - Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [React Router - Protected Routes](https://reactrouter.com/en/main/start/tutorial)
- [Django Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)

---

**Version** : 1.0  
**Date** : 13 novembre 2025  
**Équipe** : SIGETI BI Development Team
