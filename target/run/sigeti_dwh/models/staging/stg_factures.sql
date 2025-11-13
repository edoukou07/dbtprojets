
  create view "sigeti_node_db"."dwh_staging"."stg_factures__dbt_tmp"
    
    
  as (
    

select
    id,
    numero_facture,
    date_creation,
    date_echeance,
    date_paiement,
    montant_total,
    sous_total,
    statut,
    entreprise_id,
    processus_origine,
    demande_attribution_id,
    collecte_id,
    ayant_droit_id,
    created_by,
    updated_by,
    version,
    is_deleted,
    deleted_at,
    purge_id
from "sigeti_node_db"."public"."factures"
where id is not null
  and (is_deleted is null or is_deleted = false)
  );