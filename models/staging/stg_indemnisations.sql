{{ config(
    materialized='view',
    schema='staging'
) }}

-- Staging: Indemnisations
-- Extract et validation des données d'indemnisations
-- Source: indemnisations table
-- Grain: Une ligne par indemnisation

with raw_indemnisations as (
    select
        id,
        detenteur_id,
        montant_restant,
        motif_indemnisation,
        statut,
        date_creation,
        date_recevabilite,
        recevabilite_decision,
        zone_id,
        updated_at
    from {{ source('sigeti_source', 'indemnisations') }}
),

validated as (
    select
        -- Natural keys
        id as indemnisation_id,
        detenteur_id as beneficiaire_id,
        zone_id,
        
        -- Attributes
        montant_restant,
        motif_indemnisation,
        statut,
        recevabilite_decision,
        
        -- Dates
        date_creation,
        date_recevabilite,
        updated_at,
        
        -- Calculs d'indicateurs
        case 
            when recevabilite_decision = 'Recevable'
            then 1
            else 0
        end as est_acceptee,
        
        case 
            when montant_restant <= 0 and montant_restant is not null
            then 1
            else 0
        end as est_payee,
        
        case 
            when recevabilite_decision is not null and recevabilite_decision != 'En attente'
            then 1
            else 0
        end as est_evaluee,
        
        case 
            when recevabilite_decision = 'Non Recevable'
            then 1
            else 0
        end as est_rejetee,
        
        -- Calcul montants (montant_evalue = montant_restant + ce qui a été payé)
        case 
            when montant_restant is not null
            then abs(montant_restant)
            else 0
        end as montant_restant_value,
        
        -- Calcul délai (en jours)
        case 
            when date_recevabilite is not null and date_creation is not null
            then extract(epoch from (date_recevabilite - date_creation))/86400
            else null
        end as delai_evaluation_jours,
        
        -- Audit
        current_timestamp as dbt_extracted_at
    
    from raw_indemnisations
    where id is not null
)

select * from validated
