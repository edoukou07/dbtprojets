#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.db import connection

# Exécuter le SQL du DBT manuellement pour tester
with connection.cursor() as cursor:
    sql = '''
    DROP TABLE IF EXISTS dwh_marts_test.temp_mart_perf_financiere;
    
    CREATE TABLE dwh_marts_test.temp_mart_perf_financiere AS
    WITH factures as (
        SELECT * FROM dwh_facts.fait_factures
    ),
    paiements as (
        SELECT * FROM dwh_facts.fait_paiements
    ),
    collectes as (
        SELECT * FROM dwh_facts.fait_collectes
    ),
    attributions as (
        SELECT * FROM dwh_facts.fait_attributions
    ),
    entreprises as (
        SELECT * FROM dwh_dimensions.dim_entreprises
    ),
    zones as (
        SELECT * FROM dwh_dimensions.dim_zones_industrielles
    ),
    temps as (
        SELECT * FROM dwh_dimensions.dim_temps
    ),
    factures_aggregees as (
        SELECT
            t.annee,
            t.mois,
            t.trimestre,
            e.raison_sociale,
            e.domaine_activite_id,
            z.nom_zone,
            COUNT(DISTINCT f.facture_id) as nombre_factures,
            SUM(f.montant_total) as montant_total_facture,
            SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END) as montant_paye,
            SUM(CASE WHEN NOT f.est_paye THEN f.montant_total ELSE 0 END) as montant_impaye,
            AVG(f.delai_paiement_jours) as delai_moyen_paiement,
            ROUND((SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END)::NUMERIC / 
                   NULLIF(SUM(f.montant_total), 0)::NUMERIC * 100), 2) as taux_paiement_pct
        FROM factures f
        JOIN temps t ON f.date_creation_key = t.date_key
        LEFT JOIN entreprises e ON f.entreprise_id = e.entreprise_id
        LEFT JOIN attributions a ON f.demande_attribution_id = a.demande_id
        LEFT JOIN zones z ON a.zone_id = z.zone_id
        GROUP BY t.annee, t.mois, t.trimestre, e.raison_sociale, e.domaine_activite_id, z.nom_zone
    ),
    collectes_with_zones as (
        -- Agréger collectes par zone EN PREMIER, puis joindre zone
        SELECT
            c.collecte_id,
            c.date_debut_key,
            c.montant_a_recouvrer,
            c.montant_recouvre,
            c.taux_recouvrement,
            c.duree_reelle_jours,
            FIRST_VALUE(z.nom_zone) OVER (PARTITION BY c.collecte_id ORDER BY z.zone_id) as nom_zone
        FROM collectes c
        LEFT JOIN (
            SELECT DISTINCT c2.collecte_id, z2.zone_id, z2.nom_zone
            FROM collectes c2
            JOIN factures f2 ON c2.collecte_id = f2.collecte_id
            LEFT JOIN attributions a2 ON f2.demande_attribution_id = a2.demande_id
            LEFT JOIN zones z2 ON a2.zone_id = z2.zone_id
        ) zone_info ON c.collecte_id = zone_info.collecte_id
        LEFT JOIN zones z ON zone_info.zone_id = z.zone_id
    ),
    collectes_aggregees as (
        SELECT
            t.annee,
            t.trimestre,
            cz.nom_zone,
            COUNT(DISTINCT cz.collecte_id) as nombre_collectes,
            SUM(cz.montant_a_recouvrer) as montant_total_a_recouvrer,
            SUM(cz.montant_recouvre) as montant_total_recouvre,
            AVG(cz.taux_recouvrement) as taux_recouvrement_moyen,
            AVG(cz.duree_reelle_jours) as duree_moyenne_collecte
        FROM collectes_with_zones cz
        JOIN temps t ON cz.date_debut_key = t.date_key
        GROUP BY t.annee, t.trimestre, cz.nom_zone
    )
    SELECT
        f.*,
        c.nombre_collectes,
        c.montant_total_a_recouvrer,
        c.montant_total_recouvre,
        c.taux_recouvrement_moyen
    FROM factures_aggregees f
    LEFT JOIN collectes_aggregees c
        ON f.annee = c.annee
        AND f.trimestre = c.trimestre
        AND f.nom_zone = c.nom_zone;
    '''
    
    try:
        cursor.execute(sql)
        print('SUCCESS: Table temporaire creee!')
        
        # Check le résultat par zone
        cursor.execute('''
            SELECT 
                nom_zone,
                COUNT(*) as lignes,
                SUM(montant_total_recouvre) as total_recouvre
            FROM dwh_marts_test.temp_mart_perf_financiere
            WHERE nom_zone IS NOT NULL
            GROUP BY nom_zone
            ORDER BY total_recouvre DESC
        ''')
        print('\nRecouvrement par zone (apres fix):')
        total = 0
        for row in cursor.fetchall():
            if row[2]:
                total += row[2]
                print(f'{row[0]:40s} | lignes: {row[1]:3d} | recouvre: {row[2]:15,.0f}')
        print(f'\nTOTAL recouvre: {total:,.0f}')
            
    except Exception as e:
        print(f'ERROR: {str(e)[:500]}')
