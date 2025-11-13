
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select zone_key
from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
where zone_key is null



  
  
      
    ) dbt_internal_test