{{ config(
    materialized='table',
    schema='marts_financier',
    indexes=[
        {'columns': ['zone_id']},
        {'columns': ['tranche_anciennete']}
    ],
    tags=['finance', 'P2'],
    enabled=false
) }}

-- Data Mart: Créances Âgées
-- Analysis des factures impayées par tranche d'ancienneté
-- Refresh: Quotidien
-- Utilisateurs: Finance, Direction commerciale

with factures as (
    select * from {{ source('sigeti_source', 'factures') }}
    where statut = 'IMPAYEE' or statut = 'PARTIELLEMENT_PAYEE'
),

calculs as (
    select
        zone_id,
        entreprise_id,
        reference_facture,
        date_echeance,
        montant_total,
        montant_paye,
        montant_total - coalesce(montant_paye, 0) as montant_restant,
        
        extract(day from current_date - date_echeance) as jours_anciennete,
        
        case 
            when extract(day from current_date - date_echeance) between 0 and 30 then '0-30 jours'
            when extract(day from current_date - date_echeance) between 31 and 60 then '31-60 jours'
            when extract(day from current_date - date_echeance) between 61 and 90 then '61-90 jours'
            when extract(day from current_date - date_echeance) between 91 and 180 then '91-180 jours'
            when extract(day from current_date - date_echeance) > 180 then '> 180 jours'
            else 'A venir'
        end as tranche_anciennete,
        
        case 
            when extract(day from current_date - date_echeance) > 180 then 'CRITIQUE'
            when extract(day from current_date - date_echeance) > 90 then 'ELEVE'
            when extract(day from current_date - date_echeance) > 60 then 'MOYEN'
            else 'FAIBLE'
        end as niveau_risque
    
    from factures
    where current_date >= date_echeance
),

aggregated as (
    select
        tranche_anciennete,
        niveau_risque,
        
        -- Volumes
        count(*) as nombre_factures,
        count(distinct zone_id) as nombre_zones,
        count(distinct entreprise_id) as nombre_entreprises,
        
        -- Montants
        sum(montant_total) as montant_total_factures,
        sum(montant_paye) as montant_total_paye,
        sum(montant_restant) as montant_total_impaye,
        
        -- Taux
        round(sum(montant_restant)::numeric / nullif(sum(montant_total), 0) * 100, 2) as taux_impaye_pct,
        
        -- Moyennes
        round(avg(montant_restant), 2) as montant_impaye_moyen,
        round(avg(jours_anciennete), 2) as jours_anciennete_moyen,
        
        -- Top entreprises (pour drill-down)
        array_agg(distinct zone_id order by zone_id) as zones_concernees,
        
        current_timestamp as dbt_updated_at
    
    from calculs
    group by tranche_anciennete, niveau_risque
)

select * from aggregated
order by tranche_anciennete
