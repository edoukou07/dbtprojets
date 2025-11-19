#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection
c = connection.cursor()

# Count by statut
c.execute("SELECT statut::text, COUNT(*) FROM lots WHERE zone_industrielle_id IN (SELECT id FROM zones_industrielles WHERE libelle LIKE '%Yopougon%') GROUP BY statut::text")
print("By statut:", c.fetchall())

# Count with VALIDE demandes  
c.execute("SELECT COUNT(DISTINCT l.id) FROM lots l WHERE zone_industrielle_id IN (SELECT id FROM zones_industrielles WHERE libelle LIKE '%Yopougon%') AND EXISTS (SELECT 1 FROM demandes_attribution WHERE lot_id=l.id AND statut='VALIDE')")
print("With VALIDE demandes:", c.fetchone()[0])

# Total lots
c.execute("SELECT COUNT(*) FROM lots WHERE zone_industrielle_id IN (SELECT id FROM zones_industrielles WHERE libelle LIKE '%Yopougon%')")
print("Total lots:", c.fetchone()[0])
