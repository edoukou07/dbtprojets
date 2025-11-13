

select
    id,
    libelle,
    description,
    created_at,
    updated_at
from "sigeti_node_db"."public"."domaines_activites"
where id is not null