# 🚀 Quick Start - Authentification SIGETI BI

## Installation en 3 étapes

### 1️⃣ Backend (Django)
```powershell
cd bi_app\backend
.\setup_auth.ps1
python manage.py migrate
```

### 2️⃣ Frontend (React)
```powershell
# Déjà installé si vous avez exécuté setup.ps1
cd bi_app\frontend
npm install
```

### 3️⃣ Démarrer l'application
```powershell
cd ..\..
.\bi_app\start.ps1
```

## 🔑 Se connecter

1. Ouvrez http://localhost:5173
2. Utilisez un compte de test :
   - **Admin** : admin@sigeti.ci / admin123
   - **Finance** : finance@sigeti.ci / finance123
   - **Ops** : ops@sigeti.ci / ops123

## ✅ Tester l'API

```powershell
# Login
curl -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"admin@sigeti.ci\",\"password\":\"admin123\"}'

# Retourne un token : 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

# Utiliser le token
curl http://localhost:8000/api/financier/ `
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

## 📖 Documentation complète

Voir [AUTHENTICATION.md](./AUTHENTICATION.md) pour tous les détails.
