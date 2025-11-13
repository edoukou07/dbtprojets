
  create view "sigeti_node_db"."dwh_staging"."stg_entreprises__dbt_tmp"
    
    
  as (
    

select
    id,
    raison_sociale,
    telephone,
    email,
    registre_commerce,
    compte_contribuable,
    forme_juridique,
    adresse,
    date_constitution,
    domaine_activite_id,
    entreprise_id,
    user_id,
    date_creation,
    date_modification
from "sigeti_node_db"."public"."entreprises"
where id is not null
  );