# Configuration de l'envoi automatique des rapports

Le système d'envoi automatique des rapports nécessite que le management command `send_scheduled_reports` soit exécuté périodiquement.

## Configuration automatique

### Sur Linux/Mac (avec cron)

1. Ouvrez votre crontab :
```bash
crontab -e
```

2. Ajoutez cette ligne pour exécuter la commande toutes les minutes :
```bash
* * * * * cd /chemin/vers/bi_app/backend && python manage.py send_scheduled_reports
```

3. Ou utilisez le script fourni :
```bash
* * * * * /chemin/vers/bi_app/backend/send_reports.sh
```

### Sur Windows (avec Task Scheduler)

1. Ouvrez le Planificateur de tâches (Task Scheduler)
2. Créez une tâche de base
3. Définissez le déclencheur : "Répéter la tâche toutes les 1 minute"
4. Définissez l'action : "Démarrer un programme"
   - Programme : `python`
   - Arguments : `manage.py send_scheduled_reports`
   - Dossier de départ : `C:\chemin\vers\bi_app\backend`
5. Ou utilisez le script batch fourni : `send_reports.bat`

### Alternative : Utiliser un service système

Vous pouvez aussi créer un service système qui exécute la commande en boucle :

```python
# Exemple avec un script Python qui tourne en continu
import time
import subprocess
import os

os.chdir('/chemin/vers/bi_app/backend')

while True:
    subprocess.run(['python', 'manage.py', 'send_scheduled_reports'])
    time.sleep(60)  # Attendre 1 minute avant la prochaine vérification
```

## Test manuel

Pour tester manuellement l'envoi des rapports :

```bash
cd bi_app/backend
python manage.py send_scheduled_reports
```

Pour voir quels rapports seraient envoyés sans les envoyer réellement :

```bash
python manage.py send_scheduled_reports --dry-run
```

## Vérification

Pour vérifier que le scheduler fonctionne :

1. Planifiez un rapport avec une date/heure dans le futur
2. Attendez que l'heure arrive
3. Vérifiez que le rapport a été marqué comme "envoyé" dans l'interface
4. Vérifiez que l'email a bien été reçu

## Notes importantes

- Le management command vérifie tous les rapports dont `scheduled_at <= maintenant` et `sent = False`
- Les PDFs doivent avoir été générés et stockés lors de la planification
- Si les PDFs ne sont pas disponibles, le système utilisera la génération backend comme fallback
- Les rapports sont marqués comme envoyés même en cas d'erreur pour éviter les tentatives infinies

