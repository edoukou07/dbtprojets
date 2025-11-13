
  create view "sigeti_node_db"."dwh_staging"."stg_paiements__dbt_tmp"
    
    
  as (
    

select
    id,
    facture_id,
    montant,
    date_paiement,
    mode_paiement,
    statut,
    reference_paiement,
    piece_justificative,
    created_at,
    updated_at
from "sigeti_node_db"."public"."paiement_factures"
where id is not null
  );