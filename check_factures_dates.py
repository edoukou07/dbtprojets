#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection

c = connection.cursor()

print("=== Vérification des dates de factures ===\n")

c.execute("""
SELECT 
    numero_facture,
    date_creation,
    date_paiement,
    EXTRACT(DAY FROM (date_paiement - date_creation)) as delai_jours,
    statut
FROM factures
WHERE date_paiement IS NOT NULL
ORDER BY numero_facture
LIMIT 20
""")

print("Numéro | Date Création | Date Paiement | Délai (jours) | Statut")
print("-" * 70)
for numero, date_create, date_paiement, delai, statut in c.fetchall():
    print(f"{numero:20s} | {str(date_create)[:10]} | {str(date_paiement)[:10]} | {delai:13.0f} | {statut}")

print("\n=== Statistiques ===\n")
c.execute("""
SELECT 
    COUNT(*) as total_factures,
    COUNT(CASE WHEN date_paiement IS NOT NULL THEN 1 END) as factures_payees,
    COUNT(CASE WHEN date_paiement = date_creation THEN 1 END) as payees_meme_jour,
    COUNT(CASE WHEN date_paiement IS NULL THEN 1 END) as factures_impayees
FROM factures
""")

total, payees, meme_jour, impayees = c.fetchone()
print(f"Total factures: {total}")
print(f"Factures payées: {payees}")
print(f"  - Payées le même jour: {meme_jour}")
print(f"Factures impayées: {impayees}")
