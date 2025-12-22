

select
    id,
    raison_sociale,
    segment_client,
    niveau_risque,
    secteur_activite
from "sigeti_node_db"."public"."entreprises"
where id is not null