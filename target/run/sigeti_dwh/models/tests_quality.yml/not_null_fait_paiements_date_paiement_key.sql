
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date_paiement_key
from "sigeti_node_db"."dwh_facts"."fait_paiements"
where date_paiement_key is null



  
  
      
    ) dbt_internal_test