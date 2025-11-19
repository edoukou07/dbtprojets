import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum
from decimal import Decimal

def to_float(val):
    return float(val) if isinstance(val, Decimal) else (val or 0)

print("="*80)
print("TEST API ENDPOINT (backend logic avec déduplication)")
print("="*80)

# 1. Somme DIRECTE des factures impayées (pas de groupby distinct)
factures_agg = MartPerformanceFinanciere.objects.aggregate(
    montant_a_recouvrer_factures=Sum('montant_impaye')
)

# 2. Somme des collectes avec groupby DISTINCT par trimestre
collectes_data = list(MartPerformanceFinanciere.objects.values('trimestre').annotate(
    montant=Sum('montant_total_a_recouvrer'),
).distinct())

montant_a_recouvrer_factures = to_float(factures_agg['montant_a_recouvrer_factures'])
montant_a_recouvrer_collectes = sum(to_float(row['montant']) for row in collectes_data)

print(f"\nFactures impayées (somme directe):  {montant_a_recouvrer_factures:>15,.0f} FCFA")
print(f"Collectes à recouvrer (DISTINCT):   {montant_a_recouvrer_collectes:>15,.0f} FCFA")
print(f"{'─'*80}")
print(f"TOTAL AFFICHE AU DASHBOARD:         {montant_a_recouvrer_factures + montant_a_recouvrer_collectes:>15,.0f} FCFA")
print(f"En milliards:                       {(montant_a_recouvrer_factures + montant_a_recouvrer_collectes)/1e9:>15,.2f} Md FCFA")

print(f"\nDétail des collectes distinctes:")
for row in collectes_data:
    trimestre = row['trimestre']
    montant = to_float(row['montant'])
    print(f"  Trim {trimestre}: {montant:>15,.0f} FCFA")

print("\n" + "="*80)
print("COMPARAISON:")
print("="*80)
print(f"Avant déduplication (RAW mart): 6,144,392,004 FCFA = 6.14 Md")
print(f"Après déduplication (API):      {montant_a_recouvrer_collectes:>15,.0f} FCFA = {montant_a_recouvrer_collectes/1e9:.2f} Md")
print(f"\nLe dashboard doit afficher:     {montant_a_recouvrer_factures + montant_a_recouvrer_collectes:>15,.0f} FCFA")
