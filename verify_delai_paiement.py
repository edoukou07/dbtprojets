#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection
from datetime import datetime, timedelta

c = connection.cursor()

print("=== VÉRIFICATION: Délai Moyen de Paiement ===\n")

# Calculer le délai moyen de paiement
c.execute("""
SELECT 
    ROUND(AVG(EXTRACT(DAY FROM (date_paiement - date_creation)))) as delai_moyen,
    MIN(EXTRACT(DAY FROM (date_paiement - date_creation))) as delai_min,
    MAX(EXTRACT(DAY FROM (date_paiement - date_creation))) as delai_max,
    COUNT(*) as nb_factures_payees
FROM factures
WHERE date_paiement IS NOT NULL
AND date_creation IS NOT NULL
""")

result = c.fetchone()
delai_moyen, delai_min, delai_max, nb_factures = result

print(f"Délai moyen de paiement: {delai_moyen} jours")
print(f"  - Minimum: {delai_min} jours")
print(f"  - Maximum: {delai_max} jours")
print(f"  - Nombre de factures payées: {nb_factures}\n")

# Vérifier par client
print("=== Délai moyen par CLIENT ===\n")
c.execute("""
SELECT 
    e.nom_entreprise,
    ROUND(AVG(EXTRACT(DAY FROM (f.date_paiement - f.date_creation)))) as delai_moyen,
    COUNT(*) as nb_factures
FROM factures f
JOIN entreprises e ON f.entreprise_id = e.id
WHERE f.date_paiement IS NOT NULL
AND f.date_creation IS NOT NULL
GROUP BY e.id, e.nom_entreprise
ORDER BY delai_moyen DESC
LIMIT 10
""")

print("Top 10 clients par délai moyen:\n")
for client, delai, nb in c.fetchall():
    print(f"  {client}: {delai} jours ({nb} factures)")

# Vérifier la distribution des délais
print("\n=== Distribution des délais ===\n")
c.execute("""
SELECT 
    CASE 
        WHEN EXTRACT(DAY FROM (date_paiement - date_creation)) <= 7 THEN '0-7 jours'
        WHEN EXTRACT(DAY FROM (date_paiement - date_creation)) <= 14 THEN '8-14 jours'
        WHEN EXTRACT(DAY FROM (date_paiement - date_creation)) <= 21 THEN '15-21 jours'
        WHEN EXTRACT(DAY FROM (date_paiement - date_creation)) <= 30 THEN '22-30 jours'
        ELSE '>30 jours'
    END as categorie_delai,
    COUNT(*) as nb_factures,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM factures WHERE date_paiement IS NOT NULL), 1) as pourcentage
FROM factures
WHERE date_paiement IS NOT NULL
AND date_creation IS NOT NULL
GROUP BY categorie_delai
ORDER BY 
    CASE 
        WHEN categorie_delai = '0-7 jours' THEN 1
        WHEN categorie_delai = '8-14 jours' THEN 2
        WHEN categorie_delai = '15-21 jours' THEN 3
        WHEN categorie_delai = '22-30 jours' THEN 4
        ELSE 5
    END
""")

for categorie, nb, pct in c.fetchall():
    print(f"  {categorie}: {nb} factures ({pct}%)")
