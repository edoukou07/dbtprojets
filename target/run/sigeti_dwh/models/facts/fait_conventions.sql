
      
        
        
        delete from "sigeti_node_db"."dwh_facts"."fait_conventions" as DBT_INTERNAL_DEST
        where (convention_id) in (
            select distinct convention_id
            from "fait_conventions__dbt_tmp231921609267" as DBT_INTERNAL_SOURCE
        );

    

    insert into "sigeti_node_db"."dwh_facts"."fait_conventions" ("convention_key", "convention_id", "numero_convention", "nom_convention", "prenom_convention", "email", "telephone", "profession", "raison_sociale", "forme_juridique", "registre_commerce", "adresse_personnelle", "statut", "etape_actuelle", "cree_par", "date_creation", "date_modification", "dbt_extracted_at", "dbt_loaded_at")
    (
        select "convention_key", "convention_id", "numero_convention", "nom_convention", "prenom_convention", "email", "telephone", "profession", "raison_sociale", "forme_juridique", "registre_commerce", "adresse_personnelle", "statut", "etape_actuelle", "cree_par", "date_creation", "date_modification", "dbt_extracted_at", "dbt_loaded_at"
        from "fait_conventions__dbt_tmp231921609267"
    )
  