#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    ORDER BY table_name
""")

tables = [row[0] for row in cursor.fetchall()]
mart_tables = [t for t in tables if 'mart' in t.lower()]

print("MART TABLES IN DATABASE:")
print("=" * 50)
for table in sorted(mart_tables):
    print(f"  - {table}")

if not mart_tables:
    print("  No mart tables found!")
    print("\n  All tables:")
    for table in sorted(tables)[:30]:
        print(f"  - {table}")
