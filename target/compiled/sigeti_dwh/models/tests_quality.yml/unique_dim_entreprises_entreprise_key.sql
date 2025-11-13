
    
    

select
    entreprise_key as unique_field,
    count(*) as n_records

from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
where entreprise_key is not null
group by entreprise_key
having count(*) > 1


