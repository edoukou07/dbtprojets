import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
import django
django.setup()
from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum

totals = MartPerformanceFinanciere.objects.aggregate(
    total_facture=Sum('montant_total_facture'),
    total_paye=Sum('montant_paye'),
    total_impaye=Sum('montant_impaye')
)

print('=' * 60)
print('CALCUL CORRIGÉ - CRÉANCES RESTANTES')
print('=' * 60)
print()
print(f'Total Facturé: {totals["total_facture"]:,.0f} FCFA')
print(f'Total Payé: {totals["total_paye"]:,.0f} FCFA')
print(f'Total Impayé (DB): {totals["total_impaye"]:,.0f} FCFA')
print()
calculated = (totals["total_facture"] or 0) - (totals["total_paye"] or 0)
print(f'Créances Restantes (Facturé - Payé): {calculated:,.0f} FCFA')
print()
print(f'✅ Match? {totals["total_impaye"] == calculated}')
print()
print('Cela correspond au montant qui devrait être affiché à l\'écran')
