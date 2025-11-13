
  create view "sigeti_node_db"."dwh_staging"."stg_collectes__dbt_tmp"
    
    
  as (
    

select
    id,
    reference,
    montant_a_recouvrer,
    montant_recouvre,
    date_debut,
    date_fin_prevue,
    status,
    commentaire,
    cree_par,
    modifie_par,
    created_at,
    updated_at,
    statut_cloture,
    date_cloture,
    cloture_par,
    entreprises_selectionnees,
    factures_generees,
    date_generation_factures
from "sigeti_node_db"."public"."collectes"
where id is not null
  );