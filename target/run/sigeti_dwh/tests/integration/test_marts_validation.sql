
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Marts Layer Tests - Return only if issues found
select 'mart_api_performance_sla_null' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_marts_compliance"."mart_api_performance"
where sla_status is null
having count(*) > 0
union all
select 'mart_occupation_negative_pct' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_marts_occupation"."mart_occupation_zones"
where taux_occupation_pct < 0 or taux_occupation_pct > 100
having count(*) > 0
  
  
      
    ) dbt_internal_test