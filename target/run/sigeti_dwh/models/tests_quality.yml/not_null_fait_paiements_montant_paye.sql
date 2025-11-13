
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select montant_paye
from "sigeti_node_db"."dwh_facts"."fait_paiements"
where montant_paye is null



  
  
      
    ) dbt_internal_test