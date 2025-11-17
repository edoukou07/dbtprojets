import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
import django
django.setup()

from django.db import connection

# Requête SQL pour recalculer la vue avec le fix
sql = '''
DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE;

CREATE TABLE dwh_marts_financier.mart_performance_financiere AS
WITH factures_aggregees AS (
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
        ROUND(SUM(CASE WHEN f.est_paye THEN f.montant_total ELSE 0 END)::numeric / 
              NULLIF(SUM(f.montant_total), 0)::numeric * 100, 2) as taux_paiement_pct,
        SUM(c.montant_recouvre) as montant_total_recouvre,
        COUNT(DISTINCT c.collecte_id) as nombre_collectes
    FROM dwh_facts.fait_factures f
    JOIN dwh_dimensions.dim_temps t ON f.date_creation_key = t.date_key
    LEFT JOIN dwh_dimensions.dim_entreprises e ON f.entreprise_id = e.entreprise_id
    LEFT JOIN dwh_facts.fait_collectes c ON f.collecte_id = c.collecte_id
    LEFT JOIN dwh_dimensions.dim_zones_industrielles z ON c.zone_id = z.zone_id
    GROUP BY t.annee, t.mois, t.trimestre, e.raison_sociale, e.domaine_activite_id, z.nom_zone
)
SELECT * FROM factures_aggregees;

-- Recréer les indexes
CREATE INDEX idx_mart_perf_annee ON dwh_marts_financier.mart_performance_financiere (annee);
CREATE INDEX idx_mart_perf_annee_mois ON dwh_marts_financier.mart_performance_financiere (annee, mois);
CREATE INDEX idx_mart_perf_zone ON dwh_marts_financier.mart_performance_financiere (nom_zone);
'''

try:
    with connection.cursor() as cursor:
        cursor.execute(sql)
    print('✅ Table régénérée avec succès!')
    print('La correction a été appliquée: les métriques de collecte sont maintenant par zone!')
except Exception as e:
    print(f'❌ Erreur: {e}')
