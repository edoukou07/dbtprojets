{{
    config(
        materialized='incremental',
        schema='facts',
        unique_key='traitement_key',
        on_schema_change='append_new_columns',
        tags=['rh', 'workflow', 'P1']
    )
}}

/*
    Table de Faits: Traitements des Dossiers
    ========================================
    
    Cette table de faits enregistre chaque transition/action
    effectuée sur les dossiers de demande d'attribution.
    
    Granularité: Une ligne par action sur un dossier
    
    Source: historique_demandes
    
    Dimensions liées:
    - dim_agents (agent_key)
    - dim_etapes (etape_key)
    - dim_temps (date_key)
    - dim_dossiers (dossier_key)
*/

with historique as (
    select
        h.id,
        h.demande_attribution_id,
        h.utilisateur_id,
        h.action,
        h.etape_source,
        h.etape_destination,
        h.statut_avant,
        h.statut_apres,
        h.date_action,
        h.commentaire
    from {{ source('sigeti_source', 'historique_demandes') }} h
    {% if is_incremental() %}
    where h.date_action > (select max(date_action) from {{ this }})
    {% endif %}
),

-- Calcul des durées avec LEAD
with_durations as (
    select
        h.*,
        lead(h.date_action) over (
            partition by h.demande_attribution_id 
            order by h.date_action
        ) as date_action_suivante,
        extract(epoch from (
            lead(h.date_action) over (
                partition by h.demande_attribution_id 
                order by h.date_action
            ) - h.date_action
        )) / 60 as duree_minutes
    from historique h
),

-- Jointure avec les dimensions
final as (
    select
        -- Clé surrogate de la fact
        {{ dbt_utils.generate_surrogate_key(['h.id', 'h.date_action']) }} as traitement_key,
        
        -- Clés étrangères vers dimensions
        da.dossier_key,
        e.etape_key,
        a.agent_key,
        cast(to_char(h.date_action, 'YYYYMMDD') as integer) as date_action_key,
        cast(to_char(h.date_action_suivante, 'YYYYMMDD') as integer) as date_fin_key,
        
        -- Clés naturelles (dégénérées)
        h.id as historique_id,
        h.demande_attribution_id as dossier_id,
        h.utilisateur_id as agent_id,
        h.action,
        
        -- Contexte de transition
        h.etape_source,
        h.etape_destination,
        h.statut_avant,
        h.statut_apres,
        
        -- Mesures (Faits)
        h.duree_minutes,
        h.duree_minutes / 60 as duree_heures,
        h.duree_minutes / 1440 as duree_jours,
        
        -- Indicateurs binaires
        case when h.duree_minutes is not null then 1 else 0 end as est_transition_complete,
        case when h.etape_source != h.etape_destination then 1 else 0 end as est_changement_etape,
        case when h.statut_avant != h.statut_apres then 1 else 0 end as est_changement_statut,
        
        -- Timestamps
        h.date_action,
        h.date_action_suivante,
        
        -- Attributs temporels
        extract(hour from h.date_action) as heure_action,
        extract(dow from h.date_action) as jour_semaine,
        date_trunc('day', h.date_action) as jour_action,
        date_trunc('week', h.date_action) as semaine_action,
        date_trunc('month', h.date_action) as mois_action,
        
        -- Commentaire
        h.commentaire,
        
        -- Métadonnées
        current_timestamp as dbt_loaded_at
        
    from with_durations h
    left join {{ ref('dim_dossiers') }} da on h.demande_attribution_id = da.dossier_id
    left join {{ ref('dim_etapes') }} e on h.action = e.action_code
    left join {{ ref('dim_agents') }} a on h.utilisateur_id = a.agent_id
)

select * from final
