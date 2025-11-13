{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['annee']},
            {'columns': ['annee', 'trimestre']},
            {'columns': ['annee', 'nom_mois']}
        ]
    )
}}

-- Mart Opérationnel - Indicateurs de performance opérationnelle
-- Matérialisé en table pour performance optimale des dashboards

with collectes as (
    select * from {{ ref('fait_collectes') }}
),

attributions as (
    select * from {{ ref('fait_attributions') }}
),

factures as (
    select * from {{ ref('fait_factures') }}
),

temps as (
    select * from {{ ref('dim_temps') }}
),

performance_collectes as (
    select
        t.annee,
        t.trimestre,
        t.nom_mois,
        
        -- Volume
        count(*) as nombre_collectes,
        count(case when c.est_cloturee then 1 end) as collectes_cloturees,
        count(case when not c.est_cloturee then 1 end) as collectes_ouvertes,
        
        -- Performance
        avg(c.taux_recouvrement) as taux_recouvrement_moyen,
        avg(c.duree_reelle_jours) as duree_moyenne_jours,
        
        -- Volumes financiers
        sum(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        sum(c.montant_recouvre) as montant_total_recouvre,
        
        -- Efficacité
        round(
            (count(case when c.est_cloturee then 1 end)::numeric / 
             nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_cloture_pct,
        
        round(
            (sum(c.montant_recouvre)::numeric / 
             nullif(sum(c.montant_a_recouvrer), 0)::numeric * 100), 
            2
        ) as taux_recouvrement_global_pct
        
    from collectes c
    join temps t on c.date_debut_key = t.date_key
    
    group by 
        t.annee,
        t.trimestre,
        t.nom_mois
),

performance_attributions as (
    select
        t.annee,
        t.trimestre,
        
        count(*) as nombre_demandes,
        count(case when a.est_approuve then 1 end) as demandes_approuvees,
        count(case when a.est_rejete then 1 end) as demandes_rejetees,
        count(case when a.est_en_attente then 1 end) as demandes_en_attente,
        
        avg(a.delai_traitement_jours) as delai_moyen_traitement,
        
        round(
            (count(case when a.est_approuve then 1 end)::numeric / 
             nullif(count(*), 0)::numeric * 100), 
            2
        ) as taux_approbation_pct,
        
        sum(a.superficie_demandee) as superficie_totale_demandee
        
    from attributions a
    join temps t on a.date_demande_key = t.date_key
    
    group by 
        t.annee,
        t.trimestre
),

performance_facturation as (
    select
        t.annee,
        t.trimestre,
        
        count(*) as nombre_factures_emises,
        count(case when f.est_paye then 1 end) as factures_payees,
        avg(case when f.est_paye then f.delai_paiement_jours end) as delai_moyen_paiement,
        
        sum(f.montant_total) as montant_total_facture,
        sum(case when f.est_paye then f.montant_total else 0 end) as montant_paye
        
    from factures f
    join temps t on f.date_creation_key = t.date_key
    
    group by 
        t.annee,
        t.trimestre
)

select
    c.annee,
    c.trimestre,
    c.nom_mois,
    
    -- Collectes
    c.nombre_collectes,
    c.collectes_cloturees,
    c.collectes_ouvertes,
    c.taux_recouvrement_moyen,
    c.duree_moyenne_jours as duree_moyenne_collecte_jours,
    c.taux_cloture_pct,
    c.taux_recouvrement_global_pct,
    
    -- Attributions
    a.nombre_demandes,
    a.demandes_approuvees,
    a.demandes_rejetees,
    a.demandes_en_attente,
    a.delai_moyen_traitement as delai_moyen_attribution_jours,
    a.taux_approbation_pct,
    
    -- Facturation
    f.nombre_factures_emises,
    f.factures_payees,
    f.delai_moyen_paiement as delai_moyen_paiement_jours,
    
    -- Volumes financiers
    c.montant_total_a_recouvrer,
    c.montant_total_recouvre,
    f.montant_total_facture,
    f.montant_paye
    
from performance_collectes c
left join performance_attributions a 
    on c.annee = a.annee and c.trimestre = a.trimestre
left join performance_facturation f 
    on c.annee = f.annee and c.trimestre = f.trimestre
    
order by c.annee desc, c.trimestre desc
