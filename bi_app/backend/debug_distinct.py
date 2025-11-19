import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')

import django
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum

print("=== AVEC DISTINCT ON TRIMESTRE ===")
qs_distinct = MartPerformanceFinanciere.objects.filter(annee=2025).distinct('annee', 'trimestre').order_by('annee', 'trimestre', '-mois')

data = list(qs_distinct.values('annee', 'mois', 'trimestre', 'montant_total_a_recouvrer', 'montant_total_recouvre', 'nombre_collectes', 'montant_total_facture'))

print(f"Lignes avec DISTINCT: {len(data)}")
for row in data:
    print("Trim {}: À recouvrer={:,.0f}, Recouvré={:,.0f}, Factures={:,.0f}".format(
        row['trimestre'], row['montant_total_a_recouvrer'], row['montant_total_recouvre'], row['montant_total_facture']
    ))

print("\n=== SOMME ===")
summary = qs_distinct.aggregate(
    montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
    montant_recouvre=Sum('montant_total_recouvre'),
    ca_total=Sum('montant_total_facture')
)
print("À recouvrer: {:,.0f}".format(summary['montant_a_recouvrer']))
print("Recouvré: {:,.0f}".format(summary['montant_recouvre']))
print("CA: {:,.0f}".format(summary['ca_total']))
print("Créances impayées (CA - Recouvré): {:,.0f}".format(summary['ca_total'] - summary['montant_recouvre']))
