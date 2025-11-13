
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select montant_total
from "sigeti_node_db"."dwh_facts"."fait_attributions"
where montant_total is null



  
  
      
    ) dbt_internal_test