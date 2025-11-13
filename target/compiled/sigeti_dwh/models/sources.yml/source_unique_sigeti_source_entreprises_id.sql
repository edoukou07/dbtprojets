
    
    

select
    id as unique_field,
    count(*) as n_records

from "sigeti_node_db"."public"."entreprises"
where id is not null
group by id
having count(*) > 1


