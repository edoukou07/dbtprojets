
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select montant_attribution
from "sigeti_node_db"."dwh_facts"."fait_attributions"
where montant_attribution is null



  
  
      
    ) dbt_internal_test