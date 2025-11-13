
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select entreprise_key
from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
where entreprise_key is null



  
  
      
    ) dbt_internal_test