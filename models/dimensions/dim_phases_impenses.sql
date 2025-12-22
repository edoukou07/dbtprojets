{{
    config(
        materialized='table',
        schema='dimensions',
        unique_key='phase_impense_key',
        tags=['impenses', 'workflow']
    )
}}

/*
    Dimension: Phases du Workflow Impenses
    ======================================
    
    Cette dimension référence toutes les phases et étapes
    du processus de traitement des demandes d'impenses.
    
    Architecture V2 (6 phases) avec mapping V1 (28 étapes)
    
    Source: Référentiel statique + workflow_historiques observées
*/

with phases_referentiel as (
    -- Référentiel statique des phases du workflow impenses
    select * from (
        values
            -- Phase 1: Création et soumission
            (1, 1, 'CREATION', 'Création de la demande', 'INITIALISATION', 'Opérateur', true),
            (1, 2, 'SOUMISSION', 'Soumission de la demande', 'INITIALISATION', 'Opérateur', false),
            
            -- Phase 2: Vérification documents
            (2, 3, 'VERIFICATION_COMPLETUDE', 'Vérification de complétude', 'VERIFICATION', 'Agent DI', true),
            (2, 4, 'UPLOAD_DOCUMENT', 'Upload de document', 'VERIFICATION', 'Opérateur', false),
            (2, 5, 'SUPPRESSION_DOCUMENT', 'Suppression de document', 'VERIFICATION', 'Opérateur', false),
            (2, 6, 'VALIDATION_RECEVABILITE', 'Validation recevabilité', 'VERIFICATION', 'Agent DI', true),
            (2, 7, 'INVALIDATION_RECEVABILITE', 'Invalidation recevabilité', 'VERIFICATION', 'Agent DI', false),
            
            -- Phase 3: Analyse technique (Experts)
            (3, 8, 'MODIFICATION', 'Modification des données', 'ANALYSE', 'Agent', false),
            (3, 9, 'TRANSMISSION', 'Transmission au service', 'ANALYSE', 'Agent DI', true),
            (3, 10, 'COMMENTAIRE', 'Ajout de commentaire', 'ANALYSE', 'Agent', false),
            
            -- Phase 4: Validation DI
            (4, 11, 'VALIDATION_DI', 'Validation Direction Industrielle', 'VALIDATION_DI', 'Directeur DI', true),
            (4, 12, 'REJET', 'Rejet de la demande', 'VALIDATION_DI', 'Directeur DI', false),
            (4, 13, 'RETOUR', 'Retour pour correction', 'VALIDATION_DI', 'Directeur DI', false),
            
            -- Phase 5: Validation DG
            (5, 14, 'VALIDATION_DG', 'Validation Direction Générale', 'VALIDATION_DG', 'Directeur Général', true),
            (5, 15, 'NOTIFICATION', 'Notification aux parties', 'VALIDATION_DG', 'Système', false),
            
            -- Phase 6: Clôture
            (6, 16, 'CLOTURE', 'Clôture du dossier', 'CLOTURE', 'Agent', true),
            (6, 17, 'SUSPENSION', 'Suspension du dossier', 'CLOTURE', 'Agent', false),
            (6, 18, 'REPRISE', 'Reprise du dossier', 'CLOTURE', 'Agent', false),
            (6, 19, 'ANNULATION', 'Annulation du dossier', 'CLOTURE', 'Agent', false)
            
    ) as t(phase_id, etape_id, action_code, action_libelle, categorie_phase, responsable_type, est_etape_principale)
),

-- Enrichir avec les actions réellement observées
actions_observees as (
    select distinct 
        action::varchar as action_code
    from {{ source('sigeti_source', 'workflow_historiques') }}
    where action is not null
),

-- Combiner référentiel et observations
phases_combinees as (
    select
        coalesce(r.phase_id, 0) as phase_id,
        coalesce(r.etape_id, 100 + row_number() over (order by o.action_code)) as etape_id,
        o.action_code,
        coalesce(r.action_libelle, o.action_code) as action_libelle,
        coalesce(r.categorie_phase, 'AUTRE') as categorie_phase,
        coalesce(r.responsable_type, 'Non défini') as responsable_type,
        coalesce(r.est_etape_principale, false) as est_etape_principale
    from actions_observees o
    left join phases_referentiel r on o.action_code = r.action_code
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['phase_id', 'etape_id', 'action_code']) }} as phase_impense_key,
        
        -- Identifiants
        phase_id,
        etape_id,
        action_code,
        
        -- Libellés
        action_libelle,
        case phase_id
            when 1 then 'Phase 1: Création'
            when 2 then 'Phase 2: Vérification'
            when 3 then 'Phase 3: Analyse'
            when 4 then 'Phase 4: Validation DI'
            when 5 then 'Phase 5: Validation DG'
            when 6 then 'Phase 6: Clôture'
            else 'Phase non définie'
        end as phase_libelle,
        
        -- Classification
        categorie_phase,
        responsable_type,
        
        -- Indicateurs
        est_etape_principale,
        case 
            when action_code in ('VALIDATION_DI', 'VALIDATION_DG', 'VALIDATION_RECEVABILITE') then true
            else false
        end as est_etape_validation,
        case 
            when action_code in ('REJET', 'ANNULATION', 'INVALIDATION_RECEVABILITE') then true
            else false
        end as est_etape_rejet,
        case 
            when action_code in ('CLOTURE') then true
            else false
        end as est_etape_finale,
        
        -- Ordre dans le workflow
        phase_id * 100 + etape_id as ordre_workflow,
        
        -- Metadata
        current_timestamp as dbt_created_at,
        current_timestamp as dbt_updated_at
        
    from phases_combinees
)

select * from final
