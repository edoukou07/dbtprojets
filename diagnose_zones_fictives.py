import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection

print("="*80)
print("DIAGNOSTIC: Factures avec/sans zones réelles")
print("="*80)

cursor = connection.cursor()

# Requête pour vérifier les zones
cursor.execute("""
SELECT nom_zone, COUNT(*) as nombre_factures, SUM(montant_total_facture) as ca_total
FROM "dwh_marts_financier"."mart_performance_financiere"
WHERE annee = 2025
GROUP BY nom_zone
ORDER BY ca_total DESC
""")

print("\nZones dans le mart:")
print("-"*80)
results = cursor.fetchall()
for zone, count, ca in results:
    print(f"  {zone:40s} | {count:3d} factures | CA: {ca:>15,.0f} FCFA")

# Vérifier combien de factures ont une demande_attribution
print("\n" + "="*80)
print("Vérification: Factures avec demande_attribution")
print("="*80)

cursor.execute("""
SELECT 
    COUNT(*) as total_factures,
    COUNT(CASE WHEN demande_attribution_id IS NOT NULL THEN 1 END) as avec_demande,
    COUNT(CASE WHEN demande_attribution_id IS NULL THEN 1 END) as sans_demande
FROM "dwh_facts"."fait_factures"
WHERE extract(year from date_creation) = 2025
""")

total, avec, sans = cursor.fetchone()
print(f"\nTotal factures 2025:       {total}")
print(f"Avec demande_attribution:  {avec} ({100*avec/total:.1f}%)")
print(f"Sans demande_attribution:  {sans} ({100*sans/total:.1f}%)")

# Vérifier combien de demandes_attribution ont un lot
print("\n" + "="*80)
print("Vérification: Demandes avec lot")
print("="*80)

cursor.execute("""
SELECT 
    COUNT(*) as total_demandes,
    COUNT(CASE WHEN lot_id IS NOT NULL THEN 1 END) as avec_lot,
    COUNT(CASE WHEN lot_id IS NULL THEN 1 END) as sans_lot
FROM "sigeti_node_db".public.demandes_attribution
""")

total_dem, avec_lot, sans_lot = cursor.fetchone()
print(f"\nTotal demandes_attribution:  {total_dem}")
print(f"Avec lot_id:                 {avec_lot} ({100*avec_lot/total_dem:.1f}%)")
print(f"Sans lot_id:                 {sans_lot} ({100*sans_lot/total_dem:.1f}%)")

# Vérifier combien de lots ont une zone
print("\n" + "="*80)
print("Vérification: Lots avec zone")
print("="*80)

cursor.execute("""
SELECT 
    COUNT(*) as total_lots,
    COUNT(CASE WHEN zone_industrielle_id IS NOT NULL THEN 1 END) as avec_zone,
    COUNT(CASE WHEN zone_industrielle_id IS NULL THEN 1 END) as sans_zone
FROM "sigeti_node_db".public.lots
""")

total_lots, avec_zone, sans_zone = cursor.fetchone()
print(f"\nTotal lots:                 {total_lots}")
print(f"Avec zone_industrielle_id:  {avec_zone} ({100*avec_zone/total_lots:.1f}%)")
print(f"Sans zone_industrielle_id:  {sans_zone} ({100*sans_zone/total_lots:.1f}%)")

# Lister les vraies zones
print("\n" + "="*80)
print("Vraies zones dans la base de données:")
print("="*80)

cursor.execute("""
SELECT id, libelle
FROM "sigeti_node_db".public.zones_industrielles
ORDER BY id
""")

zones = cursor.fetchall()
if zones:
    for zone_id, libelle in zones:
        print(f"  ID {zone_id}: {libelle}")
else:
    print("  AUCUNE ZONE TROUVÉE!")
