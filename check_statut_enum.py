#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Vérifier les valeurs réelles des statuts
cursor.execute('''
SELECT DISTINCT statut::text
FROM lots
ORDER BY statut::text
''')

results = cursor.fetchall()
print('Statuts disponibles dans lots:')
for (statut,) in results:
    print(f'  {statut!r}')
