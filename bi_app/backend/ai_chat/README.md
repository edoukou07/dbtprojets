# Configuration du Chatbot IA SIGETI

## Vue d'ensemble

Le chatbot IA permet d'interroger la base de données SIGETI en langage naturel. Il utilise une approche hybride :

1. **Moteur basé sur des règles** (gratuit) - 30+ modèles de questions prédéfinies
2. **Moteur IA OpenAI** (optionnel, payant) - Génération SQL intelligente pour questions complexes

## Installation

### 1. Backend - Installer les dépendances

```powershell
cd bi_app\backend
pip install -r requirements.txt
```

**Note** : Le package `openai` est optionnel. Sans clé API, seul le moteur basé sur règles sera utilisé.

### 2. Configuration OpenAI (Optionnel)

Pour activer le moteur IA OpenAI, créez un fichier `.env` dans `bi_app/backend/` :

```
OPENAI_API_KEY=sk-votre-clé-api-ici
```

**Obtenir une clé API** :
1. Allez sur https://platform.openai.com/api-keys
2. Créez un compte ou connectez-vous
3. Générez une nouvelle clé API
4. Copiez la clé dans le fichier `.env`

**Coût estimé** : ~$0.01-0.03 par question (GPT-4)

### 3. Démarrer l'application

```powershell
# Backend
cd bi_app\backend
python manage.py runserver

# Frontend (nouveau terminal)
cd bi_app\frontend
npm run dev
```

## Utilisation

### Accéder au Chatbot

1. Connectez-vous à l'application : http://localhost:5173
2. Cliquez sur **"Assistant IA"** dans la sidebar
3. Posez vos questions en langage naturel

### Questions Supportées (Moteur Règles)

#### Financier
- "Quel est le chiffre d'affaires total ?"
- "Montre moi l'évolution du CA mensuel"
- "Quel est le taux de recouvrement ?"
- "Combien de créances impayées ?"

#### Occupation des Zones
- "Quel est le taux d'occupation par zone ?"
- "Combien de parcelles sont disponibles ?"
- "Liste les zones industrielles"
- "Quelles sont les zones les plus performantes ?"

#### Clients
- "Combien d'entreprises clientes ?"
- "Qui sont les top 10 clients ?"
- "Répartition des clients par secteur"

#### Général
- "Résumé général"
- "Dashboard complet"
- "Factures du mois en cours"
- "Quels sont les problèmes/alertes ?"

### Mode Avancé (avec OpenAI)

Si la clé API OpenAI est configurée, le chatbot peut répondre à des questions plus complexes :

- "Compare le CA des 3 derniers mois"
- "Quelles zones ont plus de 5 entreprises actives ?"
- "Quel client a le plus de factures impayées ?"
- "Tendance d'occupation des zones depuis janvier"

**Basculer les modes** :
- Cliquez sur le bouton "Mode Règles" / "Mode IA" dans l'en-tête du chatbot
- Mode Règles : Rapide, gratuit, questions prédéfinies
- Mode IA : Plus flexible, payant, questions ouvertes

## Fonctionnalités

### Visualisations Automatiques

Le chatbot suggère des visualisations basées sur les données :

- **KPI Cards** : Métriques clés (CA total, taux d'occupation, etc.)
- **Tableaux** : Listes de données (clients, zones, factures)
- **Graphiques** : Tendances temporelles, comparaisons

### Sécurité

- **Authentification JWT** : Seuls les utilisateurs connectés peuvent utiliser le chatbot
- **Validation SQL** : Seules les requêtes SELECT sont autorisées
- **Limite de résultats** : Maximum 100 lignes par requête
- **Timeout** : Requêtes limitées à 30 secondes

## Architecture

```
bi_app/backend/ai_chat/
├── __init__.py           # Module initialization
├── urls.py              # Routes API
├── views.py             # Endpoints API
├── query_engine.py      # Moteurs de requêtes (Rules + OpenAI)
└── chat_service.py      # Exécution SQL et formatage
```

### Endpoints API

- `POST /api/ai/chat/` - Envoyer un message au chatbot
- `GET /api/ai/capabilities/` - Obtenir les capacités du chatbot
- `GET /api/ai/suggestions/` - Obtenir des suggestions de questions
- `POST /api/ai/configure/` - Configurer la clé OpenAI (admin uniquement)

## Développement

### Ajouter de Nouvelles Questions (Règles)

Éditez `bi_app/backend/ai_chat/query_engine.py` et ajoutez un `QueryPattern` :

```python
QueryPattern(
    pattern=r"votre question pattern",
    category="financier",  # ou occupation, clients, zones, general
    sql_template="""
        SELECT ...
        FROM ...
        WHERE ...
    """,
    description="Description de la question"
)
```

### Tester le Chatbot

1. **Sans OpenAI** : Testez avec des questions prédéfinies
2. **Avec OpenAI** : Ajoutez une clé API et testez des questions complexes
3. **Vérifiez les logs** : `bi_app/backend/logs/` pour debug

## Dépannage

### Problème : "Mode IA" désactivé
**Solution** : Vérifiez que `OPENAI_API_KEY` est défini dans `.env`

### Problème : Erreur "Question non comprise"
**Solution** : Essayez de reformuler ou utilisez une question suggérée

### Problème : Erreur de connexion base de données
**Solution** : Vérifiez que PostgreSQL est démarré et accessible

### Problème : Erreur OpenAI API
**Solutions** :
- Vérifiez que la clé API est valide
- Vérifiez votre solde OpenAI
- Consultez les logs pour plus de détails

## Limites

### Moteur Règles
- ✅ Gratuit et rapide
- ✅ Questions prédéfinies très précises
- ❌ Limité aux patterns définis (30+ questions)
- ❌ Ne comprend pas les variations de formulation

### Moteur OpenAI
- ✅ Comprend le langage naturel
- ✅ Génère du SQL pour questions complexes
- ✅ Très flexible
- ❌ Payant (~$0.01-0.03 par question)
- ❌ Nécessite une connexion internet
- ❌ Peut parfois générer du SQL incorrect

## Support

Pour toute question ou problème :
1. Consultez les logs : `bi_app/backend/logs/`
2. Vérifiez la configuration : `.env`, `settings.py`
3. Testez les endpoints API avec Postman/curl

## Roadmap

- [ ] Support pour plus de types de visualisations
- [ ] Historique des conversations
- [ ] Export des résultats (CSV, Excel)
- [ ] Amélioration des suggestions contextuelles
- [ ] Support multilingue (EN, FR)
