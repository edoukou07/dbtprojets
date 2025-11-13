
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select lot_key
from "sigeti_node_db"."dwh_dimensions"."dim_lots"
where lot_key is null



  
  
      
    ) dbt_internal_test