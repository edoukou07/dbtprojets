

/*
    Staging: Workflow Historiques (Impenses)
    ========================================
    
    Extract et validation de l'historique des actions sur les impenses
    Source: workflow_historiques table
    Grain: Une ligne par action sur une impense
    
    Équivalent de historique_demandes pour les impenses
*/

with raw_workflow as (
    select
        id,
        impense_id,
        etape,
        phase,
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
        user_agent,
        date_action,
        created_at,
        updated_at
    from "sigeti_node_db"."public"."workflow_historiques"
),

validated as (
    select
        -- Natural keys
        id as workflow_historique_id,
        impense_id,
        
        -- Workflow position
        etape as etape_v1,           -- Étape V1 (1-28)
        phase as phase_v2,            -- Phase V2 (1-6)
        action::varchar as action,    -- Type d'action
        
        -- Transition
        trim(statut_avant) as statut_avant,
        trim(statut_apres) as statut_apres,
        
        -- Agent
        user_id,
        trim(user_role) as user_role,
        
        -- Détails
        trim(description) as description,
        donnees_avant,
        donnees_apres,
        metadata,
        
        -- Tracking
        trim(ip_address) as ip_address,
        trim(user_agent) as user_agent,
        
        -- Timestamps
        date_action,
        created_at,
        updated_at,
        current_timestamp as dbt_extracted_at
    from raw_workflow
)

select * from validated