
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Facts Layer Tests - Return only if issues found
select 'fait_conventions_null_key' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_facts"."fait_conventions"
where convention_id is null
having count(*) > 0
union all
select 'fait_api_logs_invalid_status' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_facts"."fait_api_logs"
where status_code not between 100 and 599
having count(*) > 0
  
  
      
    ) dbt_internal_test