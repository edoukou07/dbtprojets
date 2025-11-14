import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartOccupationZones
from django.db import connection

print("="*70)
print("ANALYSE DES DONNÉES GÉOGRAPHIQUES")
print("="*70)

# Vérifier les champs des zones
print("\n1. CHAMPS zones_industrielles (table source):")
print("-"*70)
with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'zones_industrielles' ORDER BY ordinal_position")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]}")

# Vérifier les champs d'occupation
print("\n2. CHAMPS MartOccupationZones:")
print("-"*70)
for field in MartOccupationZones._meta.fields:
    print(f"  {field.name}: {field.get_internal_type()}")

# Vérifier les données dans les zones
print("\n3. DONNÉES DES ZONES:")
print("-"*70)
zones = MartOccupationZones.objects.all()
print(f"Nombre de zones: {zones.count()}")

if zones.count() > 0:
    print("\nPremières zones:")
    for zone in zones[:5]:
        print(f"  - ID: {zone.zone_id}, Nom: {zone.nom_zone}, Taux occupation: {zone.taux_occupation_pct}%")

# Vérifier la table source
print("\n4. VÉRIFICATION TABLE SOURCE zones_industrielles:")
print("-"*70)
with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'zones_industrielles' ORDER BY ordinal_position")
    columns = cursor.fetchall()
    print("Colonnes disponibles:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    print("\nDonnées exemple:")
    cursor.execute("SELECT * FROM public.zones_industrielles LIMIT 3")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")

# Vérifier la table lots pour les coordonnées
print("\n5. VÉRIFICATION TABLE LOTS (coordonnées):")
print("-"*70)
with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'lots' AND column_name IN ('coordonnees', 'polygon', 'latitude', 'longitude') ORDER BY ordinal_position")
    columns = cursor.fetchall()
    if columns:
        print("Colonnes géographiques trouvées:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        cursor.execute("SELECT id, numero, coordonnees, polygon FROM public.lots WHERE coordonnees IS NOT NULL LIMIT 3")
        rows = cursor.fetchall()
        print("\nExemple de coordonnées:")
        for row in rows:
            print(f"  Lot {row[1]}: coordonnees={row[2]}, polygon={row[3]}")
    else:
        print("Aucune colonne géographique trouvée dans lots")

print("\n" + "="*70)
print("FIN DE L'ANALYSE")
print("="*70)
