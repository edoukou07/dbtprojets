

select
    id,
    libelle,
    description,
    created_at,
    updated_at
from "sigeti_node_db"."public"."zones_industrielles"
where id is not null