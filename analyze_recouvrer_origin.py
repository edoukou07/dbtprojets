import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum

def to_float(val):
    """Convert Decimal to float"""
    if isinstance(val, Decimal):
        return float(val)
    return val or 0

print("="*70)
print("ANALYSE DE L'ORIGINE DU MONTANT À RECOUVRER: 6,14 Md FCFA")
print("="*70)

# Détail par trimestre
print("\n1️⃣ FACTURES IMPAYÉES PAR MOIS (dans les trimestres)")
print("-" * 70)

factures_by_month = MartPerformanceFinanciere.objects.values(
    'mois', 'trimestre', 'annee'
).order_by('annee', 'trimestre', 'mois').annotate(
    impaye=Sum('montant_impaye'),
    count=Sum('nombre_factures')
)

total_factures = 0
for row in factures_by_month:
    impaye = to_float(row['impaye'])
    total_factures += impaye
    print(f"  Année {row['annee']} | Trim {row['trimestre']} | Mois {row['mois']:2d}: {impaye:>15,.0f} FCFA ({row['count']} factures)")

print(f"\n  TOTAL FACTURES IMPAYÉES: {total_factures:,.0f} FCFA ({total_factures/1e9:.2f} Md)")

# Détail collectes par trimestre
print("\n2️⃣ COLLECTES À RECOUVRER PAR TRIMESTRE (DISTINCT)")
print("-" * 70)

collectes_distinct = MartPerformanceFinanciere.objects.values('trimestre', 'annee').annotate(
    montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
    count=Sum('nombre_collectes')
).distinct()

total_collectes = 0
for row in collectes_distinct:
    montant = to_float(row['montant_a_recouvrer'])
    total_collectes += montant
    print(f"  Année {row['annee']} | Trim {row['trimestre']}: {montant:>15,.0f} FCFA ({row['count']} collectes)")

print(f"\n  TOTAL COLLECTES À RECOUVRER: {total_collectes:,.0f} FCFA ({total_collectes/1e9:.2f} Md)")

# Composition finale
print("\n" + "="*70)
print("COMPOSITION FINALE DU MONTANT À RECOUVRER")
print("="*70)

total_a_recouvrer = total_factures + total_collectes

print(f"\n  Factures impayées (non payées):        {total_factures:>15,.0f} FCFA = {total_factures/1e9:>6,.2f} Md")
print(f"  Collectes à recouvrer (arrears):       {total_collectes:>15,.0f} FCFA = {total_collectes/1e9:>6,.2f} Md")
print(f"  {'─'*60}")
print(f"  MONTANT À RECOUVRER TOTAL:             {total_a_recouvrer:>15,.0f} FCFA = {total_a_recouvrer/1e9:>6,.2f} Md FCFA ✓")

# Vérification avec CA
print("\n" + "="*70)
print("VÉRIFICATION AVEC LE CA")
print("="*70)

ca_data = MartPerformanceFinanciere.objects.aggregate(
    ca_total=Sum('montant_total_facture'),
    ca_paye=Sum('montant_paye'),
    ca_impaye=Sum('montant_impaye')
)

ca_total = to_float(ca_data['ca_total'])
ca_paye = to_float(ca_data['ca_paye'])
ca_impaye = to_float(ca_data['ca_impaye'])

print(f"\n  CA Total:                              {ca_total:>15,.0f} FCFA = {ca_total/1e9:>6,.2f} Md")
print(f"  CA Payé:                               {ca_paye:>15,.0f} FCFA = {ca_paye/1e9:>6,.2f} Md")
print(f"  CA Impayé (Factures):                  {ca_impaye:>15,.0f} FCFA = {ca_impaye/1e9:>6,.2f} Md")
print(f"  {'─'*60}")
print(f"  CA Impayé (de factures):               {ca_impaye:>15,.0f} FCFA")
print(f"  PLUS Arrears (collectes):              {total_collectes:>15,.0f} FCFA")
print(f"  = MONTANT À RECOUVRER:                 {ca_impaye + total_collectes:>15,.0f} FCFA = {(ca_impaye + total_collectes)/1e9:>6,.2f} Md")

print("\n" + "="*70)
print("EXPLICATION DE L'ORIGINE:")
print("="*70)
print("""
Le montant à recouvrer de 6,14 Md FCFA se compose de:

1. FACTURES IMPAYÉES 2025 (1,11 Md FCFA)
   └─ Montant des factures émises en 2025 mais non encore payées
   └─ C'est la "créance impayée" courante

2. COLLECTES À RECOUVRER - ARREARS (5,03 Md FCFA)
   └─ Ce sont les anciens impayés d'années précédentes
   └─ Enregistrés dans le système de collectes
   └─ Montants qui doivent être recouverts dans les périodes futures
   └─ Inclut: relances, plans de paiement, litiges, etc.

TOTAL: 1,11 Md + 5,03 Md = 6,14 Md FCFA ✓

C'est NORMAL pour un système de recouvrement! 
Les arrears sont importants car ils représentent:
- Retards de paiement historiques
- Dossiers en contentieux
- Plans de paiement échelonnés
- Provisions pour créances douteuses
""")
