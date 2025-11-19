import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum
from decimal import Decimal

def to_float(val):
    return float(val) if isinstance(val, Decimal) else (val or 0)

print("="*80)
print("TEST ENDPOINT: top_zones_performance")
print("="*80)

# Simuler la logique de l'endpoint
queryset = MartPerformanceFinanciere.objects.all()
annee = 2025
limit = 5

if annee:
    queryset = queryset.filter(annee=annee)

print(f"\nFiltrage: annee={annee}")
print(f"Nombre de lignes dans le mart: {queryset.count()}")

# Top zones par CA
print("\n📊 TOP ZONES PAR CA:")
print("-"*80)

top_ca = list(queryset.values('nom_zone').annotate(
    ca_total=Sum('montant_total_facture'),
    ca_paye=Sum('montant_paye'),
).order_by('-ca_total')[:limit])

if top_ca:
    for idx, item in enumerate(top_ca, 1):
        ca_total = to_float(item['ca_total'])
        ca_paye = to_float(item['ca_paye'])
        taux = (ca_paye / ca_total * 100) if ca_total else 0
        print(f"{idx}. {item['nom_zone']:30s} | CA: {ca_total:>15,.0f} | Payé: {ca_paye:>15,.0f} | Taux: {taux:>6.2f}%")
else:
    print("❌ AUCUNE DONNÉE RETOURNÉE!")

# Top zones par taux de paiement
print("\n✅ TOP PAYEURS:")
print("-"*80)

top_paiement = list(queryset.values('nom_zone').annotate(
    ca_total=Sum('montant_total_facture'),
    ca_paye=Sum('montant_paye'),
).order_by('nom_zone'))

for item in top_paiement:
    item['taux_paiement'] = round((item['ca_paye'] or 0) / (item['ca_total'] or 1) * 100, 2) if item['ca_total'] else 0

top_paiement = sorted(top_paiement, key=lambda x: x['taux_paiement'], reverse=True)[:limit]

if top_paiement:
    for idx, item in enumerate(top_paiement, 1):
        print(f"{idx}. {item['nom_zone']:30s} | Taux: {item['taux_paiement']:>6.2f}%")
else:
    print("❌ AUCUNE DONNÉE RETOURNÉE!")

# Zones à risque
print("\n⚠️  ZONES À RISQUE:")
print("-"*80)

zones_risque = list(queryset.values('nom_zone').annotate(
    ca_total=Sum('montant_total_facture'),
    ca_paye=Sum('montant_paye'),
    ca_impaye=Sum('montant_impaye'),
).order_by('nom_zone'))

for item in zones_risque:
    item['taux_paiement'] = round((item['ca_paye'] or 0) / (item['ca_total'] or 1) * 100, 2) if item['ca_total'] else 0

zones_risque = [z for z in zones_risque if z['taux_paiement'] < 70]
zones_risque = sorted(zones_risque, key=lambda x: x['taux_paiement'])

if zones_risque:
    for idx, item in enumerate(zones_risque, 1):
        print(f"{idx}. {item['nom_zone']:30s} | Taux: {item['taux_paiement']:>6.2f}%")
else:
    print("❌ AUCUNE ZONE À RISQUE OU AUCUNE DONNÉE!")

print("\n" + "="*80)
print(f"RÉSUMÉ: {len(top_ca)} zones top | {len(top_paiement)} meilleurs payeurs | {len(zones_risque)} zones risque")
