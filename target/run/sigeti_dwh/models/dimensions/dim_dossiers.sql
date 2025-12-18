
  
    

  create  table "sigeti_node_db"."dwh_dimensions"."dim_dossiers__dbt_tmp"
  
  
    as
  
  (
    

/*
    Dimension: Dossiers de Demande d'Attribution
    ============================================
    
    Cette dimension contient les informations descriptives
    des dossiers de demande d'attribution.
    
    Source: demandes_attribution
*/

with demandes as (
    select
        id,
        reference,
        entreprise_id,
        lot_id,
        statut,
        etape_courante,
        type_demande,
        created_at,
        updated_at
    from "sigeti_node_db"."public"."demandes_attribution"
),

final as (
    select
        md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as dossier_key,
        id as dossier_id,
        reference as dossier_reference,
        entreprise_id,
        lot_id,
        statut as dossier_statut,
        etape_courante,
        type_demande,
        
        -- Dates clés
        created_at as date_creation,
        updated_at as date_modification,
        
        -- Indicateurs
        case when statut = 'VALIDE' then true else false end as est_valide,
        case when statut = 'EN_COURS' then true else false end as est_en_cours,
        case when statut = 'REJETE' then true else false end as est_rejete,
        
        -- Métadonnées
        current_timestamp as dbt_loaded_at
        
    from demandes
)

select * from final
  );
  