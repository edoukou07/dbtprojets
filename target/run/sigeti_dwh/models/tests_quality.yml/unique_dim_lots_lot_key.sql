
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    lot_key as unique_field,
    count(*) as n_records

from "sigeti_node_db"."dwh_dimensions"."dim_lots"
where lot_key is not null
group by lot_key
having count(*) > 1



  
  
      
    ) dbt_internal_test