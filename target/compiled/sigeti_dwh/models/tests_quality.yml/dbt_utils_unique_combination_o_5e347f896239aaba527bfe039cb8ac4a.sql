





with validation_errors as (

    select
        entreprise_key
    from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
    group by entreprise_key
    having count(*) > 1

)

select *
from validation_errors


