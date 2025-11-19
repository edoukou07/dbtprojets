#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection

c = connection.cursor()

print("=== Vérifier le champ delai_moyen_paiement dans la table entreprises ===\n")

# D'abord, vérifier si la colonne existe
c.execute("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'entreprises' AND column_name LIKE '%delai%'
""")

cols = c.fetchall()
if cols:
    print(f"Colonnes trouvées: {cols}\n")
else:
    print("⚠️ Aucune colonne 'delai' trouvée dans la table entreprises\n")

# Vérifier les valeurs actuelles
c.execute("""
SELECT nom_entreprise, delai_moyen_paiement
FROM entreprises
WHERE delai_moyen_paiement IS NOT NULL
LIMIT 10
""")

print("Valeurs de delai_moyen_paiement:")
for nom, delai in c.fetchall():
    print(f"  {nom}: {delai}")

# Vérifier la moyenne
c.execute("""
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN delai_moyen_paiement IS NOT NULL THEN 1 END) as avec_delai,
    AVG(delai_moyen_paiement) as moyenne
FROM entreprises
""")

total, avec_delai, moyenne = c.fetchone()
print(f"\nStatistiques:")
print(f"  Total entreprises: {total}")
print(f"  Avec delai_moyen_paiement: {avec_delai}")
print(f"  Moyenne: {moyenne}")
