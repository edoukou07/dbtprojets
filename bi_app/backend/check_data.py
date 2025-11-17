import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
import django
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum

print("=" * 60)
print("INVESTIGATION DES DONNÉES FINANCIÈRES")
print("=" * 60)

# Totaux généraux
totals = MartPerformanceFinanciere.objects.aggregate(
    total_creances=Sum('montant_impaye'),
    montant_recouvre=Sum('montant_total_recouvre'),
    montant_paye=Sum('montant_paye'),
    total_factures=Sum('montant_total_facture')
)

print("\nTOTAUX GLOBAUX:")
print(f"  Total Facturé: {totals['total_factures']:,.0f} FCFA")
print(f"  Total Payé: {totals['montant_paye']:,.0f} FCFA")
print(f"  Total Créances (impayé): {totals['total_creances']:,.0f} FCFA")
print(f"  Montant Recouvré: {totals['montant_recouvre']:,.0f} FCFA")
print(f"  ⚠️  Créances Restantes: {(totals['total_creances'] or 0) - (totals['montant_recouvre'] or 0):,.0f} FCFA")

# Vérifier s'il y a des lignes avec montant_total_recouvre > montant_impaye
problematic = MartPerformanceFinanciere.objects.filter(
    montant_total_recouvre__gt=0
).values('nom_zone', 'montant_impaye', 'montant_total_recouvre').order_by('-montant_total_recouvre')[:10]

print("\n\nTOP 10 ZONES AVEC PLUS DE RECOUVREMENT:")
for i, ligne in enumerate(problematic, 1):
    difference = ligne['montant_total_recouvre'] - ligne['montant_impaye']
    print(f"{i}. {ligne['nom_zone']}")
    print(f"   Créances: {ligne['montant_impaye']:,.0f}")
    print(f"   Recouvré: {ligne['montant_total_recouvre']:,.0f}")
    print(f"   Différence: {difference:,.0f}")
    if difference > 0:
        print(f"   ⚠️  ALERTE: Recouvrement > Créances!")
    print()

# Vérifier la structure des données
print("\n\nEXEMPLE DE LIGNE (Première):")
first = MartPerformanceFinanciere.objects.first()
if first:
    print(f"  ID: {first.id}")
    print(f"  Zone: {first.nom_zone}")
    print(f"  Montant Total Facture: {first.montant_total_facture:,.0f}")
    print(f"  Montant Payé: {first.montant_paye:,.0f}")
    print(f"  Montant Impayé (Créances): {first.montant_impaye:,.0f}")
    print(f"  Montant Total Recouvré: {first.montant_total_recouvre:,.0f}")
    print(f"  Taux Paiement: {first.taux_paiement_pct}%")

print("\n" + "=" * 60)
