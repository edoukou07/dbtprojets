import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum

def to_float(val):
    return float(val) if isinstance(val, Decimal) else (val or 0)

print("="*80)
print("VÉRIFICATION DIRECTE DANS LE MART")
print("="*80)

# Regarder toutes les lignes brutes du mart
print("\n📋 TOUTES LES LIGNES DU MART:")
print("-"*80)
rows = list(MartPerformanceFinanciere.objects.all().values(
    'annee', 'mois', 'trimestre', 'nombre_factures', 'montant_impaye', 
    'nombre_collectes', 'montant_total_a_recouvrer'
).order_by('annee', 'trimestre', 'mois'))

for idx, row in enumerate(rows, 1):
    impaye = to_float(row['montant_impaye'])
    a_recouvrer = to_float(row['montant_total_a_recouvrer'])
    print(f"{idx}. Année {row['annee']} | Trim {row['trimestre']} | Mois {row['mois']:2d} | "
          f"Factures: {row['nombre_factures']} | Impayé: {impaye:>15,.0f} | "
          f"À Recouvrer: {a_recouvrer:>15,.0f}")

# Sommes brutes
print("\n"+"="*80)
print("SOMMES BRUTES (Sans déduplication):")
print("="*80)

totals = MartPerformanceFinanciere.objects.aggregate(
    total_factures=Sum('nombre_factures'),
    total_impaye=Sum('montant_impaye'),
    total_collectes=Sum('nombre_collectes'),
    total_a_recouvrer=Sum('montant_total_a_recouvrer')
)

impaye_total = to_float(totals['total_impaye'])
a_recouvrer_total = to_float(totals['total_a_recouvrer'])

print(f"\nMontant impayé (brut):        {impaye_total:>15,.0f} FCFA")
print(f"Montant à recouvrer (brut):   {a_recouvrer_total:>15,.0f} FCFA")

# Déduplication manuellement
print("\n" + "="*80)
print("APRÈS DÉDUPLICATION (1 ligne = 1 trimestre):")
print("="*80)

distinct_trimestres = {}
for row in rows:
    key = (row['annee'], row['trimestre'])
    if key not in distinct_trimestres:
        distinct_trimestres[key] = {
            'montant_impaye': 0,
            'montant_a_recouvrer': 0
        }
    distinct_trimestres[key]['montant_impaye'] += to_float(row['montant_impaye'])
    distinct_trimestres[key]['montant_a_recouvrer'] += to_float(row['montant_total_a_recouvrer'])

impaye_dedupe = 0
a_recouvrer_dedupe = 0

for (annee, trim), values in sorted(distinct_trimestres.items()):
    impaye_dedupe += values['montant_impaye']
    a_recouvrer_dedupe += values['montant_a_recouvrer']
    print(f"Année {annee} | Trim {trim}: "
          f"Impayé={values['montant_impaye']:>15,.0f} | "
          f"À Recouvrer={values['montant_a_recouvrer']:>15,.0f}")

print(f"\nAPRÈS déduplication:")
print(f"  Montant impayé:      {impaye_dedupe:>15,.0f} FCFA")
print(f"  Montant à recouvrer: {a_recouvrer_dedupe:>15,.0f} FCFA")
print(f"  TOTAL À RECOUVRER:   {impaye_dedupe + a_recouvrer_dedupe:>15,.0f} FCFA = {(impaye_dedupe + a_recouvrer_dedupe)/1e9:.2f} Md ✓")
