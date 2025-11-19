import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')

import django
django.setup()

from analytics.models import MartPerformanceFinanciere

print("=== DONNÉES MENSUELLES 2025 ===")
data = list(MartPerformanceFinanciere.objects.filter(annee=2025).order_by('mois').values(
    'annee', 'mois', 'montant_total_facture', 'montant_paye', 'montant_impaye', 'nombre_collectes'
))

print(f"Total lignes: {len(data)}")
print("\nDétails par mois:")
for row in data:
    if row['mois']:
        print("Mois {}: Factures={:,.0f}, Payé={:,.0f}, Impayé={:,.0f}, Collectes={}".format(
            row['mois'], row['montant_total_facture'] or 0, row['montant_paye'] or 0, 
            row['montant_impaye'] or 0, row['nombre_collectes'] or 0
        ))
    else:
        print("(Pas de mois): Factures={:,.0f}, Payé={:,.0f}, Impayé={:,.0f}, Collectes={}".format(
            row['montant_total_facture'] or 0, row['montant_paye'] or 0,
            row['montant_impaye'] or 0, row['nombre_collectes'] or 0
        ))
