#!/usr/bin/env python
import os, sys, django

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'bi_app', 'backend')
sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from sigeti_bi.models import MartPerformanceFinanciere
from django.db.models import Sum

print("=== ALL ROWS (2025) ===")
data = list(MartPerformanceFinanciere.objects.filter(annee=2025).values(
    'annee', 'mois', 'trimestre', 'montant_total_a_recouvrer', 'montant_total_recouvre'
).order_by('trimestre', 'mois'))

for row in data:
    print(f"  Année {row['annee']}, Mois {row['mois']}, Trim {row['trimestre']}: À recouvrer={row['montant_total_a_recouvrer']:,.0f}, Recouvré={row['montant_total_recouvre']:,.0f}")

print(f"\n=== TOTAL ROWS: {len(data)} ===")

print("\n=== DISTINCT per trimestre ===")
data_distinct = list(MartPerformanceFinanciere.objects.filter(annee=2025).distinct('annee', 'trimestre').order_by('trimestre').values('annee', 'trimestre', 'montant_total_a_recouvrer', 'montant_total_recouvre'))
for row in data_distinct:
    print(f"  Trimestre {row['trimestre']}: À recouvrer={row['montant_total_a_recouvrer']:,.0f}, Recouvré={row['montant_total_recouvre']:,.0f}")

print(f"\n=== DISTINCT ROWS: {len(data_distinct)} ===")

print("\n=== SUM of all (no distinct) ===")
sum_all = MartPerformanceFinanciere.objects.filter(annee=2025).aggregate(
    Sum('montant_total_a_recouvrer'),
    Sum('montant_total_recouvre')
)
print(f"  À recouvrer: {sum_all['montant_total_a_recouvrer__sum']:,.0f}")
print(f"  Recouvré: {sum_all['montant_total_recouvre__sum']:,.0f}")

print("\n=== SUM of distinct per trimestre ===")
sum_distinct = MartPerformanceFinanciere.objects.filter(annee=2025).distinct('annee', 'trimestre').aggregate(
    Sum('montant_total_a_recouvrer'),
    Sum('montant_total_recouvre')
)
print(f"  À recouvrer: {sum_distinct['montant_total_a_recouvrer__sum']:,.0f}")
print(f"  Recouvré: {sum_distinct['montant_total_recouvre__sum']:,.0f}")
