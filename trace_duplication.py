import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum
from decimal import Decimal

def to_float(val):
    return float(val) if isinstance(val, Decimal) else (val or 0)

print("="*90)
print("TRAÇAGE DE LA SOURCE DE LA DUPLICATION")
print("="*90)

# 1. Regarder les données BRUTES du mart
print("\n1️⃣ DONNÉES BRUTES DU MART (toutes les lignes):")
print("-"*90)

raw_data = list(MartPerformanceFinanciere.objects.all().values(
    'annee', 'mois', 'trimestre', 'montant_impaye', 'montant_total_a_recouvrer'
).order_by('mois'))

for row in raw_data:
    impaye = to_float(row['montant_impaye'])
    a_recouvrer = to_float(row['montant_total_a_recouvrer'])
    print(f"  Mois {row['mois']} (Trim {row['trimestre']}): "
          f"impaye={impaye:>15,.0f} | a_recouvrer={a_recouvrer:>15,.0f}")

print(f"\n  SOMME RAW (sans groupage): {sum(to_float(r['montant_total_a_recouvrer']) for r in raw_data):>15,.0f}")

# 2. Vérifier ce que retourne .values('trimestre').annotate()
print("\n2️⃣ APRÈS .values('trimestre').annotate():")
print("-"*90)

grouped = list(MartPerformanceFinanciere.objects.values('trimestre').annotate(
    montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
))

for row in grouped:
    a_recouvrer = to_float(row['montant_a_recouvrer'])
    print(f"  Trim {row['trimestre']}: {a_recouvrer:>15,.0f}")

print(f"\n  SOMME APRÈS GROUPAGE: {sum(to_float(r['montant_a_recouvrer']) for r in grouped):>15,.0f}")

# 3. Vérifier si le problème est dans le calcul du mart lui-même
print("\n3️⃣ VÉRIFICATION: D'où vient la valeur 3,072,196,002 dans chaque ligne?")
print("-"*90)

print("\n📊 Données SQL du mart (SELECT * FROM mart_performance_financiere):")
import psycopg
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT 
            annee, mois, trimestre, 
            montant_total_a_recouvrer,
            nombre_collectes,
            montant_total_recouvre
        FROM public.mart_performance_financiere
        ORDER BY mois
    """)
    
    for row in cursor.fetchall():
        annee, mois, trimestre, a_recouvrer, n_collectes, recouvre = row
        print(f"  Mois {mois} (Trim {trimestre}): "
              f"a_recouvrer={to_float(a_recouvrer):>15,.0f} | "
              f"n_collectes={n_collectes} | recouvre={to_float(recouvre):>15,.0f}")

# 4. Vérifier les stages_factures et stageCOLLECTES avant le JOIN
print("\n4️⃣ VÉRIFICATION DES STAGES (avant LEFT JOIN):")
print("-"*90)

with connection.cursor() as cursor:
    # Factures aggregées
    cursor.execute("""
        SELECT annee, mois, trimestre, COUNT(*) as n_rows
        FROM (
            SELECT DISTINCT annee, mois, trimestre
            FROM public.mart_performance_financiere
        ) t
        GROUP BY annee, mois, trimestre
        ORDER BY mois
    """)
    
    print("📋 Factures groupées par (annee, mois, trimestre):")
    for row in cursor.fetchall():
        annee, mois, trimestre, n_rows = row
        print(f"  Mois {mois} (Trim {trimestre}): {n_rows} row(s)")

print("\n" + "="*90)
print("CONCLUSION")
print("="*90)
print(f"""
Le problème vient du calcul du champ 'montant_total_a_recouvrer' dans le mart.

Chaque ligne du mart contient la MÊME valeur (3,072,196,002) pour Trim 4, même si:
- Mois 10 a impaye = 2,599,928,003
- Mois 11 a impaye = 860,000

Cela signifie que 'montant_total_a_recouvrer' N'EST PAS des factures impayées
MAIS des collectes à recouvrer (données historiques).

La duplication se produit car:
- Factures: groupées par (annee, mois, trimestre) → 2 lignes pour Trim 4
- Collectes: groupées par (annee, trimestre) → 1 ligne pour Trim 4
- LEFT JOIN: chaque facture s'ajoute aux collectes → duplication

FLUX ACTUEL (INCORRECT):
  Mois 10: montant_impaye (2,6M) + montant_total_a_recouvrer (3,07M) = 5,67M
  Mois 11: montant_impaye (0,86M) + montant_total_a_recouvrer (3,07M) = 3,93M
  TOTAL = 5,67M + 3,93M = 9,6M ❌ MAIS L'API affiche 6,14M = SEULEMENT collectes

Cela signifie que l'API additionne SEULEMENT 'montant_total_a_recouvrer'
SANS ajouter 'montant_impaye', ce qui est faux!
""")
