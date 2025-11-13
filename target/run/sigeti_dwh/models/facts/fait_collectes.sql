
      
        
        
        delete from "sigeti_node_db"."dwh_facts"."fait_collectes" as DBT_INTERNAL_DEST
        where (collecte_key) in (
            select distinct collecte_key
            from "fait_collectes__dbt_tmp041314793467" as DBT_INTERNAL_SOURCE
        );

    

    insert into "sigeti_node_db"."dwh_facts"."fait_collectes" ("collecte_key", "date_debut_key", "date_fin_prevue_key", "date_cloture_key", "collecte_id", "reference", "montant_a_recouvrer", "montant_recouvre", "montant_restant", "taux_recouvrement", "status", "statut_cloture", "date_debut", "date_fin_prevue", "date_cloture", "date_generation_factures", "duree_prevue_jours", "duree_reelle_jours", "factures_generees", "est_cloturee", "est_complete", "cree_par", "cloture_par")
    (
        select "collecte_key", "date_debut_key", "date_fin_prevue_key", "date_cloture_key", "collecte_id", "reference", "montant_a_recouvrer", "montant_recouvre", "montant_restant", "taux_recouvrement", "status", "statut_cloture", "date_debut", "date_fin_prevue", "date_cloture", "date_generation_factures", "duree_prevue_jours", "duree_reelle_jours", "factures_generees", "est_cloturee", "est_complete", "cree_par", "cloture_par"
        from "fait_collectes__dbt_tmp041314793467"
    )
  