
      
        
        
        delete from "sigeti_node_db"."dwh_facts"."fait_attributions" as DBT_INTERNAL_DEST
        where (attribution_key) in (
            select distinct attribution_key
            from "fait_attributions__dbt_tmp041314768391" as DBT_INTERNAL_SOURCE
        );

    

    insert into "sigeti_node_db"."dwh_facts"."fait_attributions" ("attribution_key", "date_demande_key", "entreprise_id", "lot_id", "zone_id", "demande_id", "reference", "superficie_demandee", "montant_attribution", "statut", "type_demande", "etape_courante", "priorite", "date_demande", "date_modification", "delai_traitement_jours", "est_approuve", "est_rejete", "est_en_attente")
    (
        select "attribution_key", "date_demande_key", "entreprise_id", "lot_id", "zone_id", "demande_id", "reference", "superficie_demandee", "montant_attribution", "statut", "type_demande", "etape_courante", "priorite", "date_demande", "date_modification", "delai_traitement_jours", "est_approuve", "est_rejete", "est_en_attente"
        from "fait_attributions__dbt_tmp041314768391"
    )
  