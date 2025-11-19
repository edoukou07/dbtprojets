#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection

# Lire et exécuter le script SQL
with open('fix_mart_reserves.sql', 'r') as f:
    sql = f.read()

cursor = connection.cursor()
cursor.execute(sql)
connection.commit()
print('✓ Mart recalculée avec réserves incluses!')
