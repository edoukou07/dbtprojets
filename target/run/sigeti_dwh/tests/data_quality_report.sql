
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Comprehensive Data Quality Report
-- Execute this query to get detailed data quality metrics across all layers

-- SECTION 1: STAGING LAYER DATA QUALITY
select 'STAGING_LAYER' as section, 'stg_agents' as table_name, 
  count(*) as total_rows,
  count(case when agent_id is null then 1 end) as null_agent_ids,
  count(distinct agent_id) as unique_agents,
  count(*) - count(distinct agent_id) as duplicate_agents
from "sigeti_node_db"."dwh_staging"."stg_agents"
union all

select 'STAGING_LAYER', 'stg_conventions', 
  count(*),
  count(case when convention_id is null then 1 end),
  count(distinct convention_id),
  count(*) - count(distinct convention_id)
from "sigeti_node_db"."dwh_staging"."stg_conventions"
union all

select 'STAGING_LAYER', 'stg_emplois_crees',
  count(*),
  count(case when demande_id is null then 1 end),
  count(distinct demande_id),
  0
from "sigeti_node_db"."dwh_staging"."stg_emplois_crees"
union all

select 'STAGING_LAYER', 'stg_indemnisations',
  count(*),
  count(case when indemnisation_id is null then 1 end),
  count(distinct indemnisation_id),
  count(*) - count(distinct indemnisation_id)
from "sigeti_node_db"."dwh_staging"."stg_indemnisations"
union all

-- SECTION 2: DIMENSION LAYER DATA QUALITY
select 'DIMENSION_LAYER', 'dim_agents',
  count(*),
  count(case when agent_id is null then 1 end),
  count(distinct agent_key),
  count(*) - count(distinct agent_key)
from "sigeti_node_db"."dwh_dimensions"."dim_agents"
union all

select 'DIMENSION_LAYER', 'dim_zones_industrielles',
  count(*),
  count(case when zone_id is null then 1 end),
  count(distinct zone_key),
  count(*) - count(distinct zone_key)
from "sigeti_node_db"."dwh_dimensions"."dim_zones_industrielles"
union all

select 'DIMENSION_LAYER', 'dim_entreprises',
  count(*),
  count(case when entreprise_id is null then 1 end),
  count(distinct entreprise_key),
  count(*) - count(distinct entreprise_key)
from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
union all

select 'DIMENSION_LAYER', 'dim_lots',
  count(*),
  count(case when lot_id is null then 1 end),
  count(distinct lot_key),
  count(*) - count(distinct lot_key)
from "sigeti_node_db"."dwh_dimensions"."dim_lots"
union all

-- SECTION 3: FACT LAYER DATA QUALITY
select 'FACT_LAYER', 'fait_conventions',
  count(*),
  count(case when convention_id is null then 1 end),
  count(distinct convention_key),
  count(*) - count(distinct convention_key)
from "sigeti_node_db"."dwh_facts"."fait_conventions"
union all

select 'FACT_LAYER', 'fait_api_logs',
  count(*),
  count(case when status_code is null then 1 end),
  count(distinct api_log_key),
  count(*) - count(distinct api_log_key)
from "sigeti_node_db"."dwh_facts"."fait_api_logs"
union all

select 'FACT_LAYER', 'fait_emplois_crees',
  count(*),
  0,
  count(distinct emplois_key),
  count(*) - count(distinct emplois_key)
from "sigeti_node_db"."dwh_facts"."fait_emplois_crees"
union all

select 'FACT_LAYER', 'fait_indemnisations',
  count(*),
  count(case when indemnisation_id is null then 1 end),
  count(distinct indemnisation_key),
  count(*) - count(distinct indemnisation_key)
from "sigeti_node_db"."dwh_facts"."fait_indemnisations"
union all

-- SECTION 4: MART LAYER DATA QUALITY
select 'MART_LAYER', 'mart_api_performance',
  count(*),
  count(case when sla_status is null then 1 end),
  count(distinct request_path),
  0
from "sigeti_node_db"."dwh_marts_compliance"."mart_api_performance"
union all

select 'MART_LAYER', 'mart_occupation_zones',
  count(*),
  count(case when zone_id is null then 1 end),
  count(distinct zone_id),
  0
from "sigeti_node_db"."dwh_marts_occupation"."mart_occupation_zones"
union all

select 'MART_LAYER', 'mart_conventions_validation',
  count(*),
  count(case when etape_actuelle is null then 1 end),
  count(distinct etape_actuelle),
  0
from "sigeti_node_db"."dwh_marts_compliance"."mart_conventions_validation"
union all

select 'MART_LAYER', 'mart_delai_approbation',
  count(*),
  0,
  count(distinct etape_actuelle),
  0
from "sigeti_node_db"."dwh_marts_compliance"."mart_delai_approbation"
  
  
      
    ) dbt_internal_test