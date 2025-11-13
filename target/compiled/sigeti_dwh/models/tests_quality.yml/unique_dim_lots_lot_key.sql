
    
    

select
    lot_key as unique_field,
    count(*) as n_records

from "sigeti_node_db"."dwh_dimensions"."dim_lots"
where lot_key is not null
group by lot_key
having count(*) > 1


