

-- Financial Performance Mart

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
        
        count(distinct f.facture_id) as nombre_factures,
        sum(f.montant_total) as montant_total_facture,
        sum(case when f.est_paye then f.montant_total else 0 end) as montant_paye,
        sum(case when not f.est_paye then f.montant_total else 0 end) as montant_impaye,
        
        avg(f.delai_paiement_jours) as delai_moyen_paiement,
        
        round(
            (sum(case when f.est_paye then f.montant_total else 0 end)::numeric / 
             nullif(sum(f.montant_total), 0)::numeric * 100), 
            2
        ) as taux_paiement_pct
        
    from factures f
    join temps t on f.date_creation_key = t.date_key
    left join entreprises e on f.entreprise_id = e.entreprise_id
    left join zones z on z.zone_id = f.zone_id
    
    group by 
        t.annee,
        t.mois,
        t.trimestre,
        e.raison_sociale,
        e.domaine_activite_id,
        z.nom_zone
),

paiements_par_collecte as (
    select
        f.collecte_id,
        t.annee,
        t.trimestre,
        sum(case when f.est_paye then f.montant_total else 0 end) as montant_paye_collecte,
        count(distinct f.facture_id) as nombre_factures_payees
    from factures f
    join temps t on f.date_creation_key = t.date_key
    where f.collecte_id is not null
    group by f.collecte_id, t.annee, t.trimestre
),

collectes_aggregees as (
    select
        t.annee,
        t.trimestre,
        
        count(distinct c.collecte_id) as nombre_collectes,
        sum(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        coalesce(sum(pc.montant_paye_collecte), 0) as montant_total_recouvre,
        avg(c.taux_recouvrement) as taux_recouvrement_moyen,
        avg(c.duree_reelle_jours) as duree_moyenne_collecte
        
    from collectes c
    join temps t on c.date_debut_key = t.date_key
    left join paiements_par_collecte pc on c.collecte_id = pc.collecte_id
        and t.annee = pc.annee
        and t.trimestre = pc.trimestre
    
    group by 
        t.annee,
        t.trimestre
)

select
    f.*,
    c.nombre_collectes,
    c.montant_total_a_recouvrer,
    c.montant_total_recouvre,
    c.taux_recouvrement_moyen
    
from factures_aggregees f
left join collectes_aggregees c 
    on f.annee = c.annee 
    and f.trimestre = c.trimestre