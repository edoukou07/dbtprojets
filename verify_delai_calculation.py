#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection
from datetime import timedelta

c = connection.cursor()

print("=== Vérifier les statuts de factures ===\n")
c.execute("SELECT DISTINCT statut FROM factures WHERE statut IS NOT NULL")
statuts = [row[0] for row in c.fetchall()]
print(f"Statuts disponibles: {statuts}\n")

# Calculer le délai moyen par SQL brut pour éviter les problèmes d'encodage
print("=== Calculer délai moyen (SQL) ===\n")
c.execute("""
SELECT 
    ROUND(AVG(EXTRACT(DAY FROM (date_paiement - date_creation)))) as delai_moyen_jours,
    COUNT(*) as nb_factures_payees
FROM factures
WHERE date_paiement IS NOT NULL
  AND date_creation IS NOT NULL
  AND date_paiement >= date_creation
""")

delai_moyen, nb = c.fetchone()
print(f"Délai moyen: {delai_moyen} jours ({nb} factures payées)")
