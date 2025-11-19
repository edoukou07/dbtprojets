#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection
c = connection.cursor()

# Detailed breakdown
c.execute("""
SELECT 
    l.id,
    l.numero,
    l.statut::text,
    COALESCE(COUNT(CASE WHEN da.statut='VALIDE' THEN 1 END), 0) as valide_cnt
FROM lots l
LEFT JOIN demandes_attribution da ON l.id = da.lot_id
WHERE l.zone_industrielle_id = (SELECT id FROM zones_industrielles WHERE libelle LIKE '%Yopougon%')
GROUP BY l.id, l.numero, l.statut::text
""")

print("Lot breakdown:")
dispo = attrib = reserve = 0
for lot_id, numero, statut, valide_cnt in c.fetchall():
    is_valide = valide_cnt > 0
    is_dispo = statut == 'disponible'
    
    if is_dispo and not is_valide:
        category = 'DISPONIBLE'
        dispo += 1
    elif is_valide:
        category = 'ATTRIBUE'
        attrib += 1
    else:
        category = 'RESERVE'
        reserve += 1
    
    print(f"  {lot_id:2d} {numero:8s} {statut:12s} VALIDE={valide_cnt} -> {category}")

print(f"\nTotals: Dispo={dispo}, Attribué={attrib}, Réserve={reserve}")
print(f"Check: {dispo} + {attrib} + {reserve} = {dispo+attrib+reserve}")
