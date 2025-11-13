
    
    

select
    date_key as unique_field,
    count(*) as n_records

from "sigeti_node_db"."dwh_dimensions"."dim_temps"
where date_key is not null
group by date_key
having count(*) > 1


