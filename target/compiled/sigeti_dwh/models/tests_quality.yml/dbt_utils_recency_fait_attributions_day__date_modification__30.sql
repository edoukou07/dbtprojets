






with recency as (

    select 

      
      
        max(date_modification) as most_recent

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

