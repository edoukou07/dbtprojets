
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select nom_entreprise
from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
where nom_entreprise is null



  
  
      
    ) dbt_internal_test