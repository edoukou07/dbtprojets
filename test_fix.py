#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, 'bi_app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Test the corrected SQL logic directly
sql = """
WITH factures AS (
    SELECT * FROM dwh_facts.fait_factures
),
temps AS (
    SELECT * FROM dwh_dimensions.dim_temps
),
collectes AS (
    SELECT * FROM dwh_facts.fait_collectes
),
paiements_par_collecte AS (
    SELECT
        f.collecte_id,
        t.annee,
        t.trimestre,
        SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye_collecte
    FROM factures f
    JOIN temps t ON f.date_creation_key = t.date_key
    WHERE f.collecte_id IS NOT NULL
    GROUP BY f.collecte_id, t.annee, t.trimestre
)
SELECT 
    t.annee,
    t.trimestre,
    COALESCE(SUM(pc.montant_paye_collecte), 0) as montant_total_recouvre
FROM collectes c
JOIN temps t ON c.date_debut_key = t.date_key
LEFT JOIN paiements_par_collecte pc ON c.collecte_id = pc.collecte_id
    AND t.annee = pc.annee
    AND t.trimestre = pc.trimestre
GROUP BY t.annee, t.trimestre
ORDER BY t.annee, t.trimestre
"""

try:
    cursor.execute(sql)
    print("NEW CORRECTED VALUES:")
    for row in cursor.fetchall():
        print(f"  Year {row[0]}, Q{row[1]}: recouvre={row[2]:,.0f}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
