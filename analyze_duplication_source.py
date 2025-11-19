import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db import connection
from decimal import Decimal

def to_float(val):
    return float(val) if isinstance(val, Decimal) else (val or 0)

print("="*90)
print("TRAÇAGE DE LA DUPLICATION - ANALYSE DES CHAMPS")
print("="*90)

# 1. Vérifier la structure exacte des données brutes
print("\n1️⃣ CHAMPS DANS CHAQUE LIGNE DU MART:")
print("-"*90)

raw_row = MartPerformanceFinanciere.objects.first()
if raw_row:
    print("\nChamps disponibles:")
    for field in MartPerformanceFinanciere._meta.get_fields():
        if not field.many_to_one and not field.one_to_many:
            value = getattr(raw_row, field.name, None)
            if isinstance(value, Decimal):
                value = f"{to_float(value):,.0f}"
            print(f"  {field.name}: {value}")

# 2. Regarder toutes les lignes
print("\n2️⃣ TOUTES LES LIGNES (avec les champs pertinents):")
print("-"*90)

rows = list(MartPerformanceFinanciere.objects.all().order_by('mois').values(
    'mois', 'trimestre', 'montant_impaye', 'montant_total_a_recouvrer', 
    'montant_total_recouvre', 'nombre_collectes'
))

for idx, row in enumerate(rows, 1):
    print(f"\n  Ligne {idx}:")
    print(f"    Mois: {row['mois']}, Trim: {row['trimestre']}")
    print(f"    montant_impaye: {to_float(row['montant_impaye']):>15,.0f}")
    print(f"    montant_total_a_recouvrer: {to_float(row['montant_total_a_recouvrer']):>15,.0f}")
    print(f"    montant_total_recouvre: {to_float(row['montant_total_recouvre']):>15,.0f}")
    print(f"    nombre_collectes: {row['nombre_collectes']}")

# 3. Vérifier ce qui se passe dans l'aggregation API
print("\n" + "="*90)
print("3️⃣ SIMULATION DE L'AGRÉGATION API:")
print("="*90)

queryset = MartPerformanceFinanciere.objects.all()

# Factures
factures = queryset.aggregate(Sum('montant_impaye') for Sum in [__import__('django.db.models', fromlist=['Sum']).Sum])
from django.db.models import Sum
factures_sum = queryset.aggregate(ca_impaye=Sum('montant_impaye'))
print(f"\nFactures impayées (SUM): {to_float(factures_sum['ca_impaye']):>15,.0f}")

# Collectes groupées par trimestre
collectes = list(queryset.values('trimestre').annotate(
    montant=Sum('montant_total_a_recouvrer')
))
print(f"\nCollectes par trimestre:")
collectes_total = 0
for row in collectes:
    montant = to_float(row['montant'])
    collectes_total += montant
    print(f"  Trim {row['trimestre']}: {montant:>15,.0f}")

print(f"\n  Total collectes: {collectes_total:>15,.0f}")

print(f"\n" + "="*90)
print("RÉSULTAT FINAL POUR L'API:")
print("="*90)
print(f"\nFACTURES IMPAYÉES: {to_float(factures_sum['ca_impaye']):>15,.0f} (montant_impaye)")
print(f"COLLECTES À RECOUVRER: {collectes_total:>15,.0f} (montant_total_a_recouvrer)")
print(f"{'─'*60}")
print(f"MONTANT À RECOUVRER (CA_IMPAYE + COLLECTES): {to_float(factures_sum['ca_impaye']) + collectes_total:>15,.0f}")
print(f"                                               {(to_float(factures_sum['ca_impaye']) + collectes_total)/1e9:.2f} Md")

# Mais l'API affiche quoi?
print(f"\n" + "="*90)
print("❌ CE QUE L'API AFFICHE RÉELLEMENT:")
print("="*90)
print(f"\nL'API affiche 'montant_a_recouvrer' = {collectes_total:>15,.0f}")
print(f"                                      = {collectes_total/1e9:.2f} Md FCFA")
print(f"\nC'est SEULEMENT les collectes, PAS les factures impayées!")
print(f"Les factures impayées ({to_float(factures_sum['ca_impaye']):,.0f}) ne sont PAS additionnées!")
