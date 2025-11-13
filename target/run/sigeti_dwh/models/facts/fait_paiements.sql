
      
        
        
        delete from "sigeti_node_db"."dwh_facts"."fait_paiements" as DBT_INTERNAL_DEST
        where (paiement_key) in (
            select distinct paiement_key
            from "fait_paiements__dbt_tmp080056110556" as DBT_INTERNAL_SOURCE
        );

    

    insert into "sigeti_node_db"."dwh_facts"."fait_paiements" ("paiement_key", "date_paiement_key", "entreprise_id", "facture_id", "collecte_id", "paiement_id", "reference_paiement", "montant_paiement", "montant_facture", "reste_a_payer", "mode_paiement", "statut", "date_paiement", "paiement_complet", "paiement_partiel")
    (
        select "paiement_key", "date_paiement_key", "entreprise_id", "facture_id", "collecte_id", "paiement_id", "reference_paiement", "montant_paiement", "montant_facture", "reste_a_payer", "mode_paiement", "statut", "date_paiement", "paiement_complet", "paiement_partiel"
        from "fait_paiements__dbt_tmp080056110556"
    )
  