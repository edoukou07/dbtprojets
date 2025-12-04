
  create view "sigeti_node_db"."dwh_staging"."stg_conventions__dbt_tmp"
    
    
  as (
    

-- Staging: Conventions
-- Extract et validation des conventions
-- Source: conventions table
-- Grain: Une ligne par convention

with raw_conventions as (
    select
        id,
        numero_convention,
        nom,
        prenom,
        email,
        telephone,
        profession,
        adresse_personnelle,
        raison_sociale,
        forme_juridique,
        registre_commerce,
        domaine_activite,
        statut,
        etape_actuelle,
        cree_par,
        date_creation,
        date_modification
    from "sigeti_node_db"."public"."conventions"
),

validated as (
    select
        -- Natural keys
        id as convention_id,
        numero_convention,
        
        -- Attributes
        trim(nom) as nom_convention,
        trim(prenom) as prenom_convention,
        email,
        telephone,
        profession,
        adresse_personnelle,
        raison_sociale,
        forme_juridique,
        registre_commerce,
        domaine_activite,
        
        -- Status
        statut,
        etape_actuelle,
        cree_par,
        
        -- Audit
        date_creation,
        date_modification,
        current_timestamp as dbt_extracted_at
    
    from raw_conventions
    where id is not null
)

select * from validated
  );