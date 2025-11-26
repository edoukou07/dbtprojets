-- Referential Integrity Tests - Return only if issues found
select 'date_consistency_check' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_facts"."fait_conventions"
where date_modification < date_creation and date_modification is not null
having count(*) > 0
union all
select 'emploi_sum_validation' as test_name, count(*) as issue_count
from "sigeti_node_db"."dwh_staging"."stg_emplois_crees"
where (emplois_nationaux + emplois_expatries) > (nombre_emplois_total + 1)
having count(*) > 0