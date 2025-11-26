-- Dimensions Layer Tests - Return only if issues found
select 'dim_agents_null_key' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_dimensions"."dim_agents"
where agent_id is null
having count(*) > 0
union all
select 'dim_zones_null_key' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
where zone_id is null
having count(*) > 0