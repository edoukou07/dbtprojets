
      
        
        
        delete from "sigeti_node_db"."dwh_facts"."fait_workflow_impenses" as DBT_INTERNAL_DEST
        where (workflow_impense_key) in (
            select distinct workflow_impense_key
            from "fait_workflow_impenses__dbt_tmp111451816715" as DBT_INTERNAL_SOURCE
        );

    

    insert into "sigeti_node_db"."dwh_facts"."fait_workflow_impenses" ("workflow_impense_key", "impense_key", "phase_impense_key", "agent_key", "date_action_key", "date_fin_key", "workflow_historique_id", "impense_id", "agent_id", "action", "user_role", "etape_v1", "phase_v2", "statut_avant", "statut_apres", "description", "duree_minutes", "duree_heures", "duree_jours", "rang_action", "date_premiere_action", "date_derniere_action", "jours_depuis_creation", "est_transition_complete", "est_changement_statut", "est_validation", "est_rejet", "est_cloture", "est_creation", "est_correction", "nb_actions", "donnees_avant", "donnees_apres", "metadata", "ip_address", "date_action", "date_action_suivante", "created_at", "dbt_loaded_at")
    (
        select "workflow_impense_key", "impense_key", "phase_impense_key", "agent_key", "date_action_key", "date_fin_key", "workflow_historique_id", "impense_id", "agent_id", "action", "user_role", "etape_v1", "phase_v2", "statut_avant", "statut_apres", "description", "duree_minutes", "duree_heures", "duree_jours", "rang_action", "date_premiere_action", "date_derniere_action", "jours_depuis_creation", "est_transition_complete", "est_changement_statut", "est_validation", "est_rejet", "est_cloture", "est_creation", "est_correction", "nb_actions", "donnees_avant", "donnees_apres", "metadata", "ip_address", "date_action", "date_action_suivante", "created_at", "dbt_loaded_at"
        from "fait_workflow_impenses__dbt_tmp111451816715"
    )
  