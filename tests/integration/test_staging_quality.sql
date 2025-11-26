-- Staging Layer Tests - Return only if issues found
select 'stg_agents_null_key' as test_name, count(*) as issue_count
from {{ ref('stg_agents') }}
where agent_id is null
having count(*) > 0
union all
select 'stg_conventions_null_key' as test_name, count(*) as issue_count
from {{ ref('stg_conventions') }}
where convention_id is null
having count(*) > 0