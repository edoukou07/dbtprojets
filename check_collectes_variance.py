import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from decimal import Decimal

def to_float(val):
    return float(val) if isinstance(val, Decimal) else (val or 0)

print("="*80)
print("VÉRIFICATION: Les collectes changent-elles par mois?")
print("="*80)

# Voir chaque ligne du mart avec tous les champs
rows = MartPerformanceFinanciere.objects.all().values(
    'annee', 'mois', 'trimestre', 
    'montant_total_recouvre',
    'montant_total_a_recouvrer',
    'nombre_collectes'
).order_by('annee', 'trimestre', 'mois')

print("\n📋 DÉTAIL PAR MOIS - CHAMPS COLLECTES:")
print("-"*80)

prev_montant = None
is_same = True

for row in rows:
    montant = to_float(row['montant_total_a_recouvrer'])
    recouvre = to_float(row['montant_total_recouvre'])
    nb_collectes = row['nombre_collectes']
    
    print(f"Année {row['annee']} | Trim {row['trimestre']} | Mois {row['mois']:2d}:")
    print(f"  → Montant À Recouvrer: {montant:>15,.0f} FCFA")
    print(f"  → Montant Recouvré:   {recouvre:>15,.0f} FCFA") 
    print(f"  → Nombre collectes:   {nb_collectes}")
    
    if prev_montant is not None and montant != prev_montant:
        is_same = False
        print(f"  ⚠️  CHANGEMENT! (Mois précédent: {prev_montant:,.0f})")
    
    prev_montant = montant
    print()

print("="*80)
if is_same:
    print("✅ DIAGNOSTIC: Les COLLECTES sont IDENTIQUES chaque mois")
    print("   → C'est une DUPLICATION (pas une vraie variance)")
    print("   → Chaque mois hérôt la MÊME valeur du LEFT JOIN sur trimestre")
else:
    print("✅ DIAGNOSTIC: Les COLLECTES VARIENT par mois")
    print("   → C'est une INFORMATION LÉGITIME")
    print("   → Chaque mois a vraiment des collectes différentes")
