# 🔐 Guide de Résolution des Erreurs d'Authentification

## ✅ Problèmes Résolus

### 1. Erreurs 401 (Unauthorized) ❌ → ✅ CORRIGÉ
**Cause:** Les requêtes API n'incluaient pas le token d'authentification

**Solution appliquée:**
- Ajout d'intercepteurs Axios dans `frontend/src/services/api.js`
- Le token est automatiquement ajouté à chaque requête avec `Authorization: Token <token>`
- Redirection automatique vers `/login` si le token expire (401)

### 2. Warning React Router v7 ⚠️ → ✅ CORRIGÉ
**Cause:** React Router v6 émettait un warning sur la future API v7

**Solution appliquée:**
- Ajout des flags `future` dans `frontend/src/main.jsx`:
  - `v7_relativeSplatPath: true`
  - `v7_startTransition: true`

## 🔑 Utilisateurs de Test Disponibles

Les utilisateurs suivants ont été créés avec leurs tokens:

| Email | Mot de passe | Rôle | Token |
|-------|--------------|------|-------|
| admin@sigeti.ci | admin123 | Administrateur | 48458d98c536a896979c723309cf83e7ce5259f9 |
| finance@sigeti.ci | finance123 | Directeur Financier | 78619add9ab7187af55b3f43102f5604f40ee7ab |
| ops@sigeti.ci | ops123 | Directeur Opérations | 445d1d4e263c8a748e2438959c027e1442e1c360 |
| direction@sigeti.ci | direction123 | Directeur Général | ddd20bdfbcda501b467a48cc9ae070df39bef961 |

## 🚀 Comment Tester

### 1. Démarrer le Backend
```powershell
cd bi_app\backend
..\..\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Démarrer le Frontend
```powershell
cd bi_app\frontend
npm run dev
```

### 3. Se Connecter
1. Ouvrir http://localhost:5173
2. Utiliser un des comptes ci-dessus (ex: admin@sigeti.ci / admin123)
3. Les requêtes API devraient maintenant fonctionner ✅

## 🔧 Modifications Apportées

### `frontend/src/services/api.js`
```javascript
// Intercepteur pour ajouter le token à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  }
);

// Intercepteur pour gérer les erreurs 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### `frontend/src/main.jsx`
```jsx
<BrowserRouter future={{ 
  v7_relativeSplatPath: true, 
  v7_startTransition: true 
}}>
  <App />
</BrowserRouter>
```

## 🧪 Test Manuel avec curl

Pour tester l'API directement:
```bash
# Test sans authentification (devrait retourner 401)
curl http://localhost:8000/api/financier/summary/

# Test avec authentification (devrait fonctionner)
curl -H "Authorization: Token 48458d98c536a896979c723309cf83e7ce5259f9" \
     http://localhost:8000/api/financier/summary/
```

## 📝 Notes Importantes

1. **Token Format**: Django REST Framework utilise le format `Token <key>`, pas `Bearer <key>`
2. **CORS**: Le backend autorise déjà `http://localhost:5173` (Vite)
3. **Session**: Les tokens sont stockés dans `localStorage` et persistent entre les rechargements
4. **Sécurité**: En production, utilisez HTTPS et des tokens JWT avec expiration

## ⚠️ Problèmes Résiduels

L'erreur suivante peut être ignorée (liée à une extension browser):
```
content-all.js:1 Uncaught (in promise) Error: Could not establish connection
ab.reasonlabsapi.com/sub/sdk: ERR_HTTP2_PROTOCOL_ERROR
```
Ces erreurs proviennent d'extensions Chrome/Edge et n'affectent pas votre application.

## 🎯 Prochaines Étapes

1. ✅ Se connecter avec un compte de test
2. ✅ Vérifier que les dashboards chargent les données
3. 📊 Tester les différentes pages (Financier, Occupation, Clients, Opérationnel)
4. 🔄 Tester la déconnexion et reconnexion
