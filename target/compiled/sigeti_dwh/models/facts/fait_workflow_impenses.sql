

/*
    Table de Faits: Workflow Impenses
    =================================
    
    Cette table de faits enregistre chaque action effectuée
    sur les dossiers de demande d'impense.
    
    Granularité: Une ligne par action sur une impense
    
    Source: workflow_historiques
    
    Dimensions liées:
    - dim_impenses (impense_key)
    - dim_phases_impenses (phase_impense_key)
    - dim_agents (agent_key)
    - dim_temps (date_key)
    
    Équivalent de fait_traitements pour les impenses
*/

with workflow as (
    select
        workflow_historique_id,
        impense_id,
        etape_v1,
        phase_v2,
        action,
        statut_avant,
        statut_apres,
        user_id,
        user_role,
        description,
        donnees_avant,
        donnees_apres,
        metadata,
        ip_address,
        date_action,
        created_at
    from "sigeti_node_db"."dwh_staging"."stg_workflow_historiques"
    
    where date_action > (select coalesce(max(date_action), '1900-01-01') from "sigeti_node_db"."dwh_facts"."fait_workflow_impenses")
    
),

-- Calcul des durées avec LEAD (durée jusqu'à l'action suivante)
with_durations as (
    select
        w.*,
        lead(w.date_action) over (
            partition by w.impense_id 
            order by w.date_action
        ) as date_action_suivante,
        
        -- Durée jusqu'à la prochaine action (en minutes)
        extract(epoch from (
            lead(w.date_action) over (
                partition by w.impense_id 
                order by w.date_action
            ) - w.date_action
        )) / 60 as duree_minutes,
        
        -- Rang de l'action dans le dossier
        row_number() over (
            partition by w.impense_id 
            order by w.date_action
        ) as rang_action,
        
        -- Première et dernière action du dossier
        first_value(w.date_action) over (
            partition by w.impense_id 
            order by w.date_action
        ) as date_premiere_action,
        
        last_value(w.date_action) over (
            partition by w.impense_id 
            order by w.date_action
            rows between unbounded preceding and unbounded following
        ) as date_derniere_action
        
    from workflow w
),

-- Jointure avec les dimensions
final as (
    select
        -- Clé surrogate de la fact
        md5(cast(coalesce(cast(h.workflow_historique_id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(h.date_action as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as workflow_impense_key,
        
        -- Clés étrangères vers dimensions
        di.impense_key,
        dp.phase_impense_key,
        a.agent_key,
        cast(to_char(h.date_action, 'YYYYMMDD') as integer) as date_action_key,
        cast(to_char(h.date_action_suivante, 'YYYYMMDD') as integer) as date_fin_key,
        
        -- Clés naturelles (dégénérées)
        h.workflow_historique_id,
        h.impense_id,
        h.user_id as agent_id,
        h.action,
        h.user_role,
        
        -- Contexte de transition
        h.etape_v1,
        h.phase_v2,
        h.statut_avant,
        h.statut_apres,
        h.description,
        
        -- Mesures (Faits)
        h.duree_minutes,
        h.duree_minutes / 60.0 as duree_heures,
        h.duree_minutes / 1440.0 as duree_jours,
        
        -- Position dans le workflow
        h.rang_action,
        h.date_premiere_action,
        h.date_derniere_action,
        extract(epoch from (h.date_action - h.date_premiere_action)) / 86400.0 as jours_depuis_creation,
        
        -- Indicateurs binaires
        case when h.duree_minutes is not null then 1 else 0 end as est_transition_complete,
        case when h.statut_avant != h.statut_apres then 1 else 0 end as est_changement_statut,
        case when h.action in ('VALIDATION_DI', 'VALIDATION_DG', 'VALIDATION_RECEVABILITE') then 1 else 0 end as est_validation,
        case when h.action in ('REJET', 'ANNULATION', 'INVALIDATION_RECEVABILITE') then 1 else 0 end as est_rejet,
        case when h.action = 'CLOTURE' then 1 else 0 end as est_cloture,
        case when h.action = 'CREATION' then 1 else 0 end as est_creation,
        case when h.action in ('RETOUR', 'MODIFICATION') then 1 else 0 end as est_correction,
        
        -- Compteurs
        1 as nb_actions,
        
        -- Données additionnelles (JSONB)
        h.donnees_avant,
        h.donnees_apres,
        h.metadata,
        
        -- Tracking
        h.ip_address,
        
        -- Timestamps
        h.date_action,
        h.date_action_suivante,
        h.created_at,
        current_timestamp as dbt_loaded_at
        
    from with_durations h
    left join "sigeti_node_db"."dwh_dimensions"."dim_impenses" di on h.impense_id = di.impense_id
    left join "sigeti_node_db"."dwh_dimensions"."dim_phases_impenses" dp on h.action = dp.action_code
    left join "sigeti_node_db"."dwh_dimensions"."dim_agents" a on h.user_id = a.agent_id
)

select * from final