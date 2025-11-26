{{ config(
    materialized='table',
    schema='marts_financier',
    indexes=[
        {'columns': ['zone_id']},
        {'columns': ['date_evaluation']}
    ],
    tags=['compliance', 'P2'],
    enabled=false
) }}

-- Data Mart: Indemnisations
-- KPIs de suivi des indemnisations par zone et statut
-- Refresh: Quotidien
-- Utilisateurs: Compliance, Métier indemnisations

with indemnisations as (
    select * from {{ ref('fait_indemnisations') }}
),

ayants_droits as (
    select * from {{ ref('stg_ayants_droits') }}
),

zones as (
    select * from {{ ref('dim_zones_industrielles') }}
),

joined as (
    select
        z.zone_name,
        z.zone_id,
        extract(year from i.date_evaluation) as annee,
        extract(month from i.date_evaluation) as mois,
        to_char(i.date_evaluation, 'YYYY-MM') as annee_mois,
        
        i.statut,
        ar.statut_progression,
        
        -- Volumes
        count(*) as nombre_indemnisations,
        count(distinct i.ayant_droit_id) as nombre_ayants_droits,
        
        -- Statuts
        count(case when i.est_payee = 1 then 1 end) as indemnisations_payees,
        count(case when i.est_evalouee = 1 then 1 end) as indemnisations_evaluees,
        count(case when i.est_rejetee = 1 then 1 end) as indemnisations_rejetees,
        
        -- Montants
        sum(i.montant_evalue) as montant_total_evalue,
        sum(i.montant_paye) as montant_total_paye,
        sum(i.montant_restant) as montant_total_restant,
        
        -- Taux de paiement
        round(sum(i.montant_paye)::numeric / nullif(sum(i.montant_evalue), 0) * 100, 2) as taux_paiement_global_pct,
        
        -- Délais
        avg(i.delai_paiement_jours) as delai_moyen_paiement_jours,
        max(i.delai_paiement_jours) as delai_max_paiement_jours,
        percentile_cont(0.5) within group (order by i.delai_paiement_jours) as delai_median_paiement_jours,
        
        -- Montant moyen
        round(avg(i.montant_evalue), 2) as montant_moyen_evalue,
        round(avg(i.montant_paye), 2) as montant_moyen_paye,
        
        current_timestamp as dbt_updated_at
    
    from indemnisations i
    left join ayants_droits ar on i.ayant_droit_id = ar.ayant_droit_id
    left join zones z on ar.convention_id = z.zone_id
    group by z.zone_name, z.zone_id, annee, mois, annee_mois, i.statut, ar.statut_progression
)

select * from joined

