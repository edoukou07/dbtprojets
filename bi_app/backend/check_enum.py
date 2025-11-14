import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='lots' AND table_schema='public' ORDER BY ordinal_position")
    columns = cursor.fetchall()
    print("Colonnes de la table lots:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
