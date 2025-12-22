
  create view "sigeti_node_db"."dwh_staging"."stg_entreprises__dbt_tmp"
    
    
  as (
    

select
    id,
    raison_sociale,
    segment_client,
    niveau_risque,
    secteur_activite
from "sigeti_node_db"."public"."entreprises"
where id is not null
  );