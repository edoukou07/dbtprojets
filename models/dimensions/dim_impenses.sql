{{
    config(
        materialized='table',
        schema='dimensions',
        unique_key='impense_key',
        tags=['impenses']
    )
}}

/*
    Dimension: Impenses (Dossiers)
    ==============================
    
    Dimension SCD Type 1 des dossiers d'impenses.
    Contient les attributs descriptifs de chaque demande d'impense.
    
    Granularité: Une ligne par demande d'impense
    
    Relations:
    - lot_id → dim_lots
    - entreprise_id → dim_entreprises
*/

with impenses_source as (
    select * from {{ ref('stg_impenses') }}
),

lots as (
    select 
        id as lot_id,
        numero as numero_lot,
        superficie as superficie_m2,
        zone_industrielle_id
    from {{ ref('stg_lots') }}
),

entreprises as (
    select 
        id as entreprise_id,
        raison_sociale as nom_entreprise,
        secteur_activite
    from {{ ref('stg_entreprises') }}
),

final as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['i.impense_id']) }} as impense_key,
        
        -- Clé naturelle
        i.impense_id,
        i.numero_dossier,
        
        -- Lot concerné
        i.lot_id,
        i.lot_numero,
        i.lot_ilot,
        l.superficie_m2 as lot_superficie_m2,
        l.zone_industrielle_id,
        
        -- Entreprise/Opérateur
        i.entreprise_id,
        i.operateur_id,
        i.nom_operateur,
        e.nom_entreprise,
        e.secteur_activite,
        
        -- Statut actuel
        i.statut::text as statut_actuel,
        i.etape_actuelle,
        case i.statut::text
            when 'en cours' then 'En cours de traitement'
            when 'complete' then 'Completee'
            when 'suspendue' then 'Suspendue'
            when 'annulee' then 'Annulee'
            when 'cloturee' then 'Cloturee'
            else coalesce(i.statut::text, 'Non defini')
        end as statut_libelle,
        
        -- Phase actuelle (déduction depuis étape)
        case 
            when i.etape_actuelle <= 2 then 1
            when i.etape_actuelle <= 7 then 2
            when i.etape_actuelle <= 10 then 3
            when i.etape_actuelle <= 13 then 4
            when i.etape_actuelle <= 15 then 5
            else 6
        end as phase_actuelle,
        
        -- Motif
        i.motif_cession,
        case 
            when lower(i.motif_cession) like '%volontaire%' then 'Cession volontaire'
            when lower(i.motif_cession) like '%retrait%' then 'Retrait administratif'
            else 'Autre'
        end as type_demande,
        
        -- Décisions
        i.decision_verification,
        i.resultat_analyse,
        
        -- Dates clés
        i.date_emission,
        i.date_transmission,
        i.date_enregistrement,
        i.date_analyse,
        i.created_at as date_creation,
        
        -- Indicateurs
        case when i.decision_verification is not null then true else false end as a_decision_verification,
        case when i.resultat_analyse is not null then true else false end as a_resultat_analyse,
        case when i.date_analyse is not null then true else false end as est_analyse,
        case when i.statut::text = 'cloturee' then true else false end as est_cloture,
        
        -- Durées calculées (jours)
        extract(day from (coalesce(i.date_transmission, current_timestamp) - i.date_emission)) as jours_avant_transmission,
        extract(day from (coalesce(i.date_analyse, current_timestamp) - i.date_emission)) as jours_avant_analyse,
        
        -- Audit
        i.created_at,
        i.updated_at,
        current_timestamp as dbt_created_at
        
    from impenses_source i
    left join lots l on i.lot_id = l.lot_id
    left join entreprises e on i.entreprise_id = e.entreprise_id
)

select * from final
