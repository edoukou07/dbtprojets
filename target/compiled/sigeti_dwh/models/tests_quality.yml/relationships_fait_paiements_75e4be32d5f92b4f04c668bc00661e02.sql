
    
    

with child as (
    select date_paiement_key as from_field
    from "sigeti_node_db"."dwh_facts"."fait_paiements"
    where date_paiement_key is not null
),

parent as (
    select date_key as to_field
    from "sigeti_node_db"."dwh_dimensions"."dim_temps"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


