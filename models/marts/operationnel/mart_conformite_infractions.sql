{{ config(
    materialized='table',
    schema='marts_operationnel',
    indexes=[
        {'columns': ['mois_debut']}
    ],
    tags=['conformite', 'P1'],
    enabled=true
) }}

-- Data Mart: Conformité Infractions
-- KPIs de conformité par période

with fct as (
    select * from {{ ref('fait_infractions') }}
)

select
    date_trunc('month', fct.date_detection)::date as mois_debut,
    coalesce(fct.lot_id, 0) as zone_id,
    'Zone_' || coalesce(fct.lot_id::text, 'Unknown') as zone_name,
    
    count(*) as nombre_infractions,
    count(case when fct.is_resolved then 1 end) as infractions_resolues,
    count(case when not fct.is_resolved then 1 end) as infractions_non_resolues,
    
    count(case when fct.etape::text in ('1', '2') then 1 end) as infractions_mineures,
    count(case when fct.etape::text in ('3', '4') then 1 end) as infractions_moderees,
    count(case when fct.etape::text in ('5', '6') then 1 end) as infractions_majeures,
    count(case when fct.etape::text in ('7', '8', '9') then 1 end) as infractions_critiques,
    
    round(count(case when fct.is_resolved then 1 end)::numeric / nullif(count(*), 0) * 100, 2) as taux_resolution_pct,
    
    avg(fct.days_to_resolution) as delai_moyen_resolution_jours,
    max(fct.days_to_resolution) as delai_max_resolution_jours,
    percentile_cont(0.5) within group (order by fct.days_to_resolution) as delai_median_resolution_jours,
    
    round(avg(
        case when fct.etape::text in ('1', '2') then 1
             when fct.etape::text in ('3', '4') then 2
             when fct.etape::text in ('5', '6') then 3
             else 4
        end
    ), 2) as severite_moyenne,
    
    current_timestamp as dbt_updated_at
    
from fct
where fct.date_detection is not null
group by 
    date_trunc('month', fct.date_detection)::date,
    fct.lot_id
