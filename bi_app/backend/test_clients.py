import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPortefeuilleClients

# Tester la récupération des clients
print("Test de récupération des clients...")
clients = MartPortefeuilleClients.objects.all()
print(f"Nombre de clients trouvés: {clients.count()}")

if clients.count() > 0:
    print("\nPremiers 5 clients:")
    for client in clients[:5]:
        print(f"  - ID: {client.entreprise_id}, Raison sociale: {client.raison_sociale}")
else:
    print("\nAucun client trouvé!")
    print("\nVérification de la connexion à la base de données...")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM dwh_marts_clients.mart_portefeuille_clients")
        count = cursor.fetchone()[0]
        print(f"Nombre de lignes dans la table (requête directe): {count}")
        
        if count > 0:
            cursor.execute("SELECT entreprise_id, raison_sociale FROM dwh_marts_clients.mart_portefeuille_clients LIMIT 5")
            rows = cursor.fetchall()
            print("\nPremières lignes (requête directe):")
            for row in rows:
                print(f"  - ID: {row[0]}, Raison sociale: {row[1]}")
