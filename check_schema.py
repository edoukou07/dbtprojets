#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Check the schema of lots table
print("=== Checking lots table schema ===")
cursor.execute('''
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'lots'
ORDER BY ordinal_position
''')
columns = cursor.fetchall()
for col, dtype in columns:
    print(f"  {col}: {dtype}")

print("\n=== Checking zones_industrielles table schema ===")
cursor.execute('''
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'zones_industrielles'
ORDER BY ordinal_position
''')
columns = cursor.fetchall()
for col, dtype in columns:
    print(f"  {col}: {dtype}")
