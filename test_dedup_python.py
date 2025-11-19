import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum, Avg
from decimal import Decimal

def to_float(val):
    return float(val) if isinstance(val, Decimal) else (val or 0)

print("="*80)
print("TEST DÉDUPLICATION AVEC LOGIC PYTHON")
print("="*80)

queryset = MartPerformanceFinanciere.objects.all()

# Somme des factures
factures_summary = queryset.aggregate(
    ca_impaye=Sum('montant_impaye'),
)

# Déduplication manuelle en Python
collectes_raw = queryset.values('trimestre').annotate(
    montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
)

print("\n📋 Avant déduplication (RAW):")
for row in collectes_raw:
    print(f"   Trim {row['trimestre']}: {to_float(row['montant_a_recouvrer']):>15,.0f} FCFA")

# Deduplicate
collectes_by_trimestre_dict = {}
for row in collectes_raw:
    trimestre = row['trimestre']
    if trimestre not in collectes_by_trimestre_dict:
        collectes_by_trimestre_dict[trimestre] = row

collectes_list = list(collectes_by_trimestre_dict.values())

print("\n✅ Après déduplication (DICT):")
for row in collectes_list:
    print(f"   Trim {row['trimestre']}: {to_float(row['montant_a_recouvrer']):>15,.0f} FCFA")

# Sommes finales
ca_impaye = to_float(factures_summary['ca_impaye'])
montant_a_recouvrer = sum(to_float(row['montant_a_recouvrer']) for row in collectes_list)

print("\n" + "="*80)
print("RÉSULTAT FINAL (Affichage au Dashboard):")
print("="*80)
print(f"\nFactures impayées:              {ca_impaye:>15,.0f} FCFA")
print(f"Collectes à recouvrer (DEDUPE): {montant_a_recouvrer:>15,.0f} FCFA")
print(f"─────────────────────────────────────────────")
print(f"Montant À Recouvrer TOTAL:      {ca_impaye + montant_a_recouvrer:>15,.0f} FCFA")
print(f"En milliards:                   {(ca_impaye + montant_a_recouvrer)/1e9:>15,.2f} Md FCFA ✓")
