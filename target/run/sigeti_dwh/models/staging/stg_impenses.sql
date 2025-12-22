
  create view "sigeti_node_db"."dwh_staging"."stg_impenses__dbt_tmp"
    
    
  as (
    

/*
    Staging: Impenses
    =================
    
    Extract et validation des demandes d'impenses
    Source: impenses table
    Grain: Une ligne par demande d'impense
    
    Contexte métier:
    - Impense = investissements réalisés par un opérateur sur un lot
    - Processus de cession volontaire ou retrait administratif
*/

with raw_impenses as (
    select
        id,
        numero_dossier,
        statut,
        etape_actuelle,
        etapes_completees,
        lot_id,
        lot_numero,
        lot_ilot,
        operateur_id,
        entreprise_id,
        nom_operateur,
        date_emission,
        motif_cession,
        date_transmission,
        decision_verification,
        date_enregistrement,
        resultat_analyse,
        date_analyse,
        created_at,
        updated_at
    from "sigeti_node_db"."public"."impenses"
),

validated as (
    select
        -- Natural keys
        id as impense_id,
        numero_dossier,
        
        -- Lot information
        lot_id,
        trim(lot_numero) as lot_numero,
        trim(lot_ilot) as lot_ilot,
        
        -- Entreprise/Opérateur
        operateur_id,
        entreprise_id,
        trim(nom_operateur) as nom_operateur,
        
        -- Statut et workflow
        statut,
        etape_actuelle,
        etapes_completees,
        
        -- Dates du processus
        date_emission,
        date_transmission,
        date_enregistrement,
        date_analyse,
        
        -- Décisions
        motif_cession,
        decision_verification,
        resultat_analyse,
        
        -- Audit
        created_at,
        updated_at,
        current_timestamp as dbt_extracted_at
    from raw_impenses
)

select * from validated
  );