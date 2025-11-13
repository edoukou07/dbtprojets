
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    domaine_key as unique_field,
    count(*) as n_records

from "sigeti_node_db"."dwh_dimensions"."dim_domaines_activites"
where domaine_key is not null
group by domaine_key
having count(*) > 1



  
  
      
    ) dbt_internal_test