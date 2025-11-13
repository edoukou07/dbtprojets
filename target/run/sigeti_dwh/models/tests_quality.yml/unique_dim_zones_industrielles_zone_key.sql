
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    zone_key as unique_field,
    count(*) as n_records

from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
where zone_key is not null
group by zone_key
having count(*) > 1



  
  
      
    ) dbt_internal_test