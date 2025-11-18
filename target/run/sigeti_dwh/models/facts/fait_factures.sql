
      
        
        
        delete from "sigeti_node_db"."dwh_facts"."fait_factures" as DBT_INTERNAL_DEST
        where (facture_key) in (
            select distinct facture_key
            from "fait_factures__dbt_tmp011231598521" as DBT_INTERNAL_SOURCE
        );

    

    insert into "sigeti_node_db"."dwh_facts"."fait_factures" ("facture_key", "date_creation_key", "date_paiement_key", "entreprise_id", "collecte_id", "demande_attribution_id", "ayant_droit_id", "facture_id", "numero_facture", "montant_total", "sous_total", "montant_taxes", "statut", "processus_origine", "date_creation", "date_echeance", "date_paiement", "delai_paiement_jours", "est_en_retard", "est_paye", "created_by", "updated_by", "version")
    (
        select "facture_key", "date_creation_key", "date_paiement_key", "entreprise_id", "collecte_id", "demande_attribution_id", "ayant_droit_id", "facture_id", "numero_facture", "montant_total", "sous_total", "montant_taxes", "statut", "processus_origine", "date_creation", "date_echeance", "date_paiement", "delai_paiement_jours", "est_en_retard", "est_paye", "created_by", "updated_by", "version"
        from "fait_factures__dbt_tmp011231598521"
    )
  