#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

# Read and execute SQL
with open('create_mart_tables.sql', 'r') as f:
    sql_script = f.read()

cursor = connection.cursor()

# Execute each statement
statements = [s.strip() for s in sql_script.split(';') if s.strip()]

print("Creating mart tables and inserting test data...")
print("=" * 60)

try:
    for i, statement in enumerate(statements):
        if statement:
            print(f"Executing statement {i+1}/{len(statements)}...")
            cursor.execute(statement)
    
    connection.commit()
    print(f"\n✓ Successfully created {len(statements)} statements")
    print("\nCreated tables:")
    print("  - dwh_marts_implantation.mart_implantation_suivi")
    print("  - dwh_marts_rh.mart_indemnisations")
    print("  - dwh_marts_rh.mart_emplois_crees")
    print("  - dwh_marts_financier.mart_creances_agees")
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    sys.exit(1)
