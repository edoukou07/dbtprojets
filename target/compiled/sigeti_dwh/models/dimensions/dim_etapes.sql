

/*
    Dimension: Étapes du Workflow de Traitement
    ===========================================
    
    Cette dimension référence toutes les étapes du processus
    de traitement des dossiers de demande d'attribution.
    
    Source: Référentiel statique des étapes + historique_demandes
*/

with etapes_referentiel as (
    -- Référentiel statique des étapes connues
    select * from (
        values
            (1, 'CREATION_DEMANDE', 'Création de la demande', 1, 2, 'INITIALISATION', 'Demandeur'),
            (2, 'VERIFICATION_CEPICI', 'Vérification par le CEPICI', 2, 3, 'VERIFICATION', 'CEPICI'),
            (3, 'VERIFICATION_SOGEDI', 'Vérification par SOGEDI', 3, 4, 'VERIFICATION', 'SOGEDI'),
            (4, 'PAIEMENT', 'Enregistrement du paiement', 4, 4, 'PAIEMENT', 'Financier'),
            (5, 'GENERER_RECEPISSE_DEPOT', 'Génération du récépissé de dépôt', 4, 5, 'DOCUMENTATION', 'Système'),
            (6, 'UPLOAD_RECEPISSE_SIGNE', 'Upload du récépissé signé', 5, 6, 'DOCUMENTATION', 'Agent'),
            (7, 'ANALYSE_RECEVABILITE', 'Analyse de recevabilité', 6, 7, 'ANALYSE', 'Analyste'),
            (8, 'GENERATION_ATTESTATION_RECEVABILITE', 'Génération attestation de recevabilité', 7, 7, 'DOCUMENTATION', 'Système'),
            (9, 'SIGNATURE_ATTESTATION_RECEVABILITE', 'Signature attestation de recevabilité', 7, 8, 'VALIDATION', 'Responsable'),
            (10, 'SOUMETTRE_RAPPORT_TECHNIQUE', 'Soumission du rapport technique', 8, 9, 'ANALYSE', 'Technicien'),
            (11, 'TRAITER_DEMANDE_COMMISSION_INTERNE', 'Traitement commission interne', 9, 10, 'COMMISSION', 'Commission'),
            (12, 'TRAITER_DEMANDE_COMMISSION_INTERMINISTERIELLE', 'Traitement commission interministérielle', 10, 11, 'COMMISSION', 'Commission'),
            (13, 'REDACTION_LAMEV', 'Rédaction du LAMEV', 11, 11, 'DOCUMENTATION', 'Rédacteur'),
            (14, 'SIGNATURE_LAMEV', 'Signature du LAMEV', 11, 12, 'VALIDATION', 'Direction'),
            (15, 'DOCUMENTS_MODIFIES_SOUMIS', 'Documents modifiés soumis', null, null, 'MODIFICATION', 'Demandeur'),
            (16, 'Paiement enregistré avec succès', 'Confirmation de paiement', 4, 4, 'PAIEMENT', 'Système')
    ) as t(etape_id, action_code, action_libelle, etape_source, etape_destination, categorie_etape, responsable_type)
),

-- Enrichir avec les actions réellement observées dans les données
etapes_observees as (
    select distinct 
        action as action_code
    from "sigeti_node_db"."public"."historique_demandes"
    where action is not null
),

-- Combiner référentiel et observations
etapes_combinees as (
    select
        coalesce(r.etape_id, 100 + row_number() over (order by o.action_code)) as etape_id,
        o.action_code,
        coalesce(r.action_libelle, o.action_code) as action_libelle,
        r.etape_source,
        r.etape_destination,
        coalesce(r.categorie_etape, 'AUTRE') as categorie_etape,
        coalesce(r.responsable_type, 'Non défini') as responsable_type
    from etapes_observees o
    left join etapes_referentiel r on o.action_code = r.action_code
),

final as (
    select
        md5(cast(coalesce(cast(etape_id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(action_code as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as etape_key,
        etape_id,
        action_code,
        action_libelle,
        etape_source,
        etape_destination,
        categorie_etape,
        responsable_type,
        
        -- Ordre dans le workflow
        etape_source as ordre_workflow,
        
        -- Indicateurs
        case 
            when categorie_etape = 'INITIALISATION' then true 
            else false 
        end as est_etape_initiale,
        case 
            when categorie_etape = 'VALIDATION' and action_code like '%LAMEV%' then true 
            else false 
        end as est_etape_finale,
        case 
            when categorie_etape in ('VERIFICATION', 'ANALYSE', 'COMMISSION') then true 
            else false 
        end as est_etape_critique,
        
        -- Métadonnées
        current_timestamp as dbt_loaded_at
        
    from etapes_combinees
)

select * from final
order by etape_id