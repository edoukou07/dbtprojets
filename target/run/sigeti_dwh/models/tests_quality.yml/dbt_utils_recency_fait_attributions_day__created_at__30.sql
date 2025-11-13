
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  






with recency as (

    select 

      
      
        max(created_at) as most_recent

    from "sigeti_node_db"."dwh_facts"."fait_attributions"

    

)

select

    
    most_recent,
    cast(

    now() + ((interval '1 day') * (-30))

 as timestamp) as threshold

from recency
where most_recent < cast(

    now() + ((interval '1 day') * (-30))

 as timestamp)


  
  
      
    ) dbt_internal_test