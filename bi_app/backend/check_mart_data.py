#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')

import django
django.setup()

from sigeti_bi.models import MartPerformanceFinanciere
from django.db.models import Sum

print("=== ALL ROWS (2025) ===")
data = list(MartPerformanceFinanciere.objects.filter(annee=2025).values(
    'annee', 'mois', 'trimestre', 'montant_total_a_recouvrer', 'montant_total_recouvre'
).order_by('trimestre', 'mois'))

for row in data:
    print("  Année {}, Mois {}, Trim {}: À recouvrer={:,.0f}, Recouvré={:,.0f}".format(
        row['annee'], row['mois'], row['trimestre'], 
        row['montant_total_a_recouvrer'], row['montant_total_recouvre']
    ))

print("\nTOTAL ROWS: {}".format(len(data)))

print("\n=== DISTINCT per trimestre ===")
data_distinct = list(MartPerformanceFinanciere.objects.filter(annee=2025).distinct('annee', 'trimestre').order_by('trimestre').values('annee', 'trimestre', 'montant_total_a_recouvrer', 'montant_total_recouvre'))
for row in data_distinct:
    print("  Trimestre {}: À recouvrer={:,.0f}, Recouvré={:,.0f}".format(
        row['trimestre'], row['montant_total_a_recouvrer'], row['montant_total_recouvre']
    ))

print("\nDISTINCT ROWS: {}".format(len(data_distinct)))
