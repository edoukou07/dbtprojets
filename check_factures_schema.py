#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.db import connection

c = connection.cursor()

print("=== Schema table factures ===\n")
c.execute("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'factures'
ORDER BY ordinal_position
""")

for col, dtype in c.fetchall():
    print(f"  {col}: {dtype}")
