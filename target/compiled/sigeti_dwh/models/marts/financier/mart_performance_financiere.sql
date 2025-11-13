

-- Mart Financier - Vue complète pour analyse financière

with factures as (
    select * from "sigeti_node_db"."dwh_facts"."fait_factures"
),

paiements as (
    select * from "sigeti_node_db"."dwh_facts"."fait_paiements"
),

collectes as (
    select * from "sigeti_node_db"."dwh_facts"."fait_collectes"
),

entreprises as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
),

zones as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
),

temps as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_temps"
),

factures_aggregees as (
    select
        t.annee,
        t.mois,
        t.trimestre,
        e.raison_sociale,
        e.domaine_activite_id,
        z.nom_zone,
        
        -- Métriques de facturation
        count(distinct f.facture_id) as nombre_factures,
        sum(f.montant_total) as montant_total_facture,
        sum(case when f.est_paye then f.montant_total else 0 end) as montant_paye,
        sum(case when not f.est_paye then f.montant_total else 0 end) as montant_impaye,
        
        -- Délais
        avg(f.delai_paiement_jours) as delai_moyen_paiement,
        
        -- Taux
        round(
            (sum(case when f.est_paye then f.montant_total else 0 end)::numeric / 
             nullif(sum(f.montant_total), 0)::numeric * 100), 
            2
        ) as taux_paiement_pct
        
    from factures f
    join temps t on f.date_creation_key = t.date_key
    left join entreprises e on f.entreprise_id = e.entreprise_id
    left join collectes c on f.collecte_id = c.collecte_id
    left join zones z on c.collecte_id = z.zone_id  -- À ajuster selon votre modèle
    
    group by 
        t.annee,
        t.mois,
        t.trimestre,
        e.raison_sociale,
        e.domaine_activite_id,
        z.nom_zone
),

collectes_aggregees as (
    select
        t.annee,
        t.trimestre,
        
        -- Métriques de collecte
        count(distinct c.collecte_id) as nombre_collectes,
        sum(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        sum(c.montant_recouvre) as montant_total_recouvre,
        avg(c.taux_recouvrement) as taux_recouvrement_moyen,
        avg(c.duree_reelle_jours) as duree_moyenne_collecte
        
    from collectes c
    join temps t on c.date_debut_key = t.date_key
    
    group by 
        t.annee,
        t.trimestre
)

select
    -- Utiliser les factures comme base principale
    f.*,
    c.nombre_collectes,
    c.montant_total_a_recouvrer,
    c.montant_total_recouvre,
    c.taux_recouvrement_moyen
    
from factures_aggregees f
left join collectes_aggregees c 
    on f.annee = c.annee 
    and f.trimestre = c.trimestre