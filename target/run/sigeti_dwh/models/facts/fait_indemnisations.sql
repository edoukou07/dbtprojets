
      
        
        
        delete from "sigeti_node_db"."dwh_facts"."fait_indemnisations" as DBT_INTERNAL_DEST
        where (indemnisation_id) in (
            select distinct indemnisation_id
            from "fait_indemnisations__dbt_tmp231922385606" as DBT_INTERNAL_SOURCE
        );

    

    insert into "sigeti_node_db"."dwh_facts"."fait_indemnisations" ("indemnisation_key", "indemnisation_id", "beneficiaire_id", "zone_id", "statut", "motif_indemnisation", "montant_restant", "date_creation", "updated_at", "dbt_extracted_at", "dbt_loaded_at")
    (
        select "indemnisation_key", "indemnisation_id", "beneficiaire_id", "zone_id", "statut", "motif_indemnisation", "montant_restant", "date_creation", "updated_at", "dbt_extracted_at", "dbt_loaded_at"
        from "fait_indemnisations__dbt_tmp231922385606"
    )
  