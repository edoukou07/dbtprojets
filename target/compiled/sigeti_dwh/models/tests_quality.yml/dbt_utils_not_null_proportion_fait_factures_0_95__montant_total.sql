







with validation as (
  select
    
    sum(case when montant_total is null then 0 else 1 end) / cast(count(*) as numeric) as not_null_proportion
  from "sigeti_node_db"."dwh_facts"."fait_factures"
  
),
validation_errors as (
  select
    
    not_null_proportion
  from validation
  where not_null_proportion < 0.95 or not_null_proportion > 1
)
select
  *
from validation_errors

