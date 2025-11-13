
  create view "sigeti_node_db"."dwh_staging"."stg_demandes_attribution__dbt_tmp"
    
    
  as (
    

select
    id,
    reference,
    statut,
    etape_courante,
    type_demande,
    entreprise_id,
    lot_id,
    zone_id,
    informations_terrain,
    coordonnees_geospatiales,
    financement,
    emplois,
    priorite,
    decisions_commissions,
    historique_etapes,
    retours,
    metadata,
    user_id,
    created_at,
    updated_at
from "sigeti_node_db"."public"."demandes_attribution"
where id is not null
  );