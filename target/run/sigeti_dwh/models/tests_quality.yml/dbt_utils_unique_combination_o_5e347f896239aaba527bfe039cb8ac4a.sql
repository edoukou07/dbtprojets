
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  





with validation_errors as (

    select
        entreprise_key
    from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
    group by entreprise_key
    having count(*) > 1

)

select *
from validation_errors



  
  
      
    ) dbt_internal_test