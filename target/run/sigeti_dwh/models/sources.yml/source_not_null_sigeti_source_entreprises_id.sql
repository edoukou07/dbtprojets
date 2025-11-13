
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id
from "sigeti_node_db"."public"."entreprises"
where id is null



  
  
      
    ) dbt_internal_test