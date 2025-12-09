# Configuration du Serveur SMTP

## Vue d'ensemble

Ce guide explique comment configurer un serveur SMTP (Simple Mail Transfer Protocol) pour permettre à l'application d'envoyer des emails automatiquement (rapports, notifications, etc.).

---

## Option 1 : Gmail (Recommandé pour le développement)

### Étapes :

#### 1. Vérifier la sécurité du compte
- Allez sur https://myaccount.google.com/security
- Vérifiez que votre numéro de téléphone est confirmé
- Activez "Vérification en 2 étapes" si ce n'est pas déjà fait

#### 2. Générer un mot de passe d'application

⚠️ **Important** : Si vous recevez l'erreur "Le paramètre que vous recherchez n'est pas disponible pour votre compte", c'est que :
- Vous n'avez pas de compte Google professionnel (Workspace), ou
- 2FA n'est pas complètement activée

**Solution alternative** : Utiliser un mot de passe spécifique à l'application

##### Procédure :
1. Allez sur https://myaccount.google.com/apppasswords
   - Si la page vous redirige vers la sécurité : 2FA n'est pas complètement activée
2. Sélectionnez "Courrier" et "Windows"
3. Générez un mot de passe unique (16 caractères avec espaces)
4. Copiez le mot de passe complet

**Si ça ne fonctionne toujours pas** : Voir "[Alternative](#alternative--mots-de-passe-moins-sécurisés)" ci-dessous

#### 3. Configurer le fichier `.env`

Copiez d'abord le modèle `bi_app/backend/env.example` :

```bash
cd bi_app/backend
copy env.example .env  # PowerShell
# ou
cp env.example .env    # bash
```

Puis renseignez vos identifiants SMTP :

```bash
# Fichier: bi_app/backend/.env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=votre-email@gmail.com
```

#### 4. Redémarrer l'application
```bash
python manage.py runserver
```

---

## Alternative 1 : Outlook ou SendGrid (Recommandé)

Si Gmail refuse l'accès, la meilleure solution est d'utiliser **Outlook** ou **SendGrid** qui sont plus permissifs :

### Option A : Outlook (gratuit, facile)

```bash
# Fichier: bi_app/backend/.env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@outlook.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
DEFAULT_FROM_EMAIL=votre-email@outlook.com
```

### Option B : SendGrid (gratuit, professionnel)

Voir la section "Option 3 : SendGrid" ci-dessous

---

## Alternative 2 : Créer un compte Google dédié

Si vous voulez absolument utiliser Gmail :

1. **Créer un nouveau compte Gmail** dédié à l'application (ex: `sigeti-bi-app@gmail.com`)
2. Vérifier le numéro de téléphone
3. Activer 2FA
4. Générer un mot de passe d'application
5. Utiliser ce compte dans `.env`

**Avantage** : Complet isolement, meilleure sécurité

---

## Alternative 3 : Mots de passe moins sécurisés (Déconseillé)

⚠️ **Google a supprimé cette option pour la plupart des comptes** (raison de votre erreur).

Si votre compte est ancien, essayez quand même :

1. Allez sur https://myaccount.google.com/lesssecureapps
2. Si la page dit "Ce paramètre n'est pas disponible" → **Utilisez Alternative 1 ou 2 à la place**
3. Si c'est actif, vous pouvez :

```bash
# Fichier: bi_app/backend/.env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-gmail
DEFAULT_FROM_EMAIL=votre-email@gmail.com
```

---

## Option 2 : Outlook / Office365

### Configuration

```bash
# Fichier: bi_app/backend/.env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@outlook.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
DEFAULT_FROM_EMAIL=votre-email@outlook.com
```

---

## Option 3 : SendGrid (Production recommandée)

SendGrid est un service d'envoi d'emails fiable et scalable.

### Étapes :

#### 1. Créer un compte SendGrid
- Allez sur https://sendgrid.com
- Créez un compte gratuit (100 emails/jour)

#### 2. Générer une clé API
- Accédez à Settings > API Keys
- Créez une nouvelle clé API
- Copiez la clé (stockez-la en sécurité)

#### 3. Configurer le fichier `.env`

```bash
# Fichier: bi_app/backend/.env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=votre-cle-api-sendgrid
DEFAULT_FROM_EMAIL=votre-email@votre-domaine.com
```

---

## Option 4 : Development (Console Backend)

Pour le développement, les emails s'affichent dans la console au lieu d'être envoyés.

```bash
# Fichier: bi_app/backend/.env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Sortie dans la console :**
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: SIGETI - Report: Rapport Financier
From: noreply@sigeti-bi.local
To: admin@example.com

Report Rapport Financier for dashboard financier attached.
```

---

## Option 5 : Testing (Fichier Backend)

Pour les tests, les emails sont sauvegardés dans un fichier.

```bash
# Fichier: bi_app/backend/.env
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/app-messages
```

Les emails seront sauvegardés dans `/tmp/app-messages/`

---

## Vérification de la Configuration

### 1. Vérifier les paramètres

```python
# Dans l'interpréteur Django shell
python manage.py shell

>>> from django.conf import settings
>>> print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
>>> print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
>>> print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
>>> print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
>>> print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
```

### 2. Tester l'envoi d'email

```python
# Dans l'interpréteur Django shell
python manage.py shell

>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test Email',
...     'Ceci est un email de test.',
...     'noreply@sigeti-bi.local',
...     ['destinataire@example.com'],
...     fail_silently=False,
... )
```

### 3. Tester via l'API

1. Accédez à `http://localhost:5173/report-config`
2. Créez une programmation de rapport
3. Cliquez sur "Envoyer maintenant"
4. Vérifiez la réception de l'email

---

## Troubleshooting

### Email n'est pas envoyé

**Vérification :**
1. Vérifiez les logs Django pour les erreurs
2. Vérifiez les paramètres du fichier `.env`
3. Vérifiez la connexion internet
4. Vérifiez les paramètres SMTP auprès du fournisseur

### Erreur d'authentification

**Solutions :**
- Gmail : Vérifiez que 2FA est activé et qu'un mot de passe d'application est généré
- Outlook : Vérifiez le mot de passe
- SendGrid : Vérifiez la clé API

### Erreur de port

**Solutions :**
- Gmail/Outlook : Utiliser le port 587 avec TLS
- SendGrid : Utiliser le port 587 avec TLS
- Autres serveurs : Vérifier avec le fournisseur

### Certificat SSL/TLS invalide

**Solutions :**
- Vérifier que `EMAIL_USE_TLS=True`
- Ajouter à `.env` : `EMAIL_USE_SSL=False` (sauf pour certains services)

---

## Paramètres Environment Variables

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `EMAIL_BACKEND` | Backend d'envoi d'email | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | Adresse du serveur SMTP | `smtp.gmail.com` |
| `EMAIL_PORT` | Port SMTP | `587` |
| `EMAIL_USE_TLS` | Utiliser TLS/SSL | `True` |
| `EMAIL_HOST_USER` | Nom d'utilisateur SMTP | `votre-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Mot de passe SMTP | `xxxx xxxx xxxx xxxx` |
| `DEFAULT_FROM_EMAIL` | Email par défaut | `noreply@sigeti-bi.local` |

---

## Sécurité

⚠️ **Important :**
- **Ne commitez JAMAIS** le fichier `.env` dans Git
- Le fichier `.env` est listée dans `.gitignore` (à vérifier)
- Utilisez des variables d'environnement en production
- Utilisez des mots de passe d'application, pas le mot de passe du compte
- Pour SendGrid, utilisez une clé API avec permissions limitées

---

## Support

Pour toute question ou problème, consultez :
- Django Email Documentation: https://docs.djangoproject.com/en/stable/topics/email/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- SendGrid Documentation: https://sendgrid.com/docs/
