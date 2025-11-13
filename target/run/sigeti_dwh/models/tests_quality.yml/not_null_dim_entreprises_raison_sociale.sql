
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select raison_sociale
from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
where raison_sociale is null



  
  
      
    ) dbt_internal_test