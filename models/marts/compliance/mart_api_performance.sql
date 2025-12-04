{{ config(
    materialized='table',
    schema='marts_compliance',
    indexes=[
        {'columns': ['request_path']},
        {'columns': ['status_code']},
        {'columns': ['user_role']},
        {'columns': ['environment']},
        {'columns': ['endpoint_category']}
    ],
    tags=['infrastructure', 'P3']
) }}

-- Data Mart: API Performance (SLA Monitoring)
-- Track API performance and SLA metrics
-- Dimensions: Endpoint, Method, Status, Role, Environment, Category
-- Refresh: Real-time
-- Users: Infrastructure, DevOps, Tech leads

with api_logs as (
    select * from {{ ref('fait_api_logs') }}
),

enriched_logs as (
    select
        *,
        -- Environment dimension (IMPORTANT)
        case 
            when request_path like '%prod%' then 'PRODUCTION'
            when request_path like '%staging%' then 'STAGING'
            when request_path like '%dev%' then 'DEVELOPMENT'
            else 'UNKNOWN'
        end as environment,
        
        -- Endpoint category dimension (IMPORTANT)
        case 
            when request_path like '%convention%' then 'Conventions'
            when request_path like '%attribution%' then 'Attributions'
            when request_path like '%facture%' or request_path like '%payment%' then 'Payments'
            when request_path like '%collecte%' then 'Collections'
            when request_path like '%agent%' then 'Agents'
            when request_path like '%infraction%' then 'Infractions'
            when request_path like '%zone%' or request_path like '%lot%' then 'Zones_Lots'
            else 'Other'
        end as endpoint_category
    
    from api_logs
),

daily_kpis as (
    select
        request_path,
        request_method,
        status_code,
        user_role,
        
        -- Enriched dimensions (IMPORTANT)
        environment,
        endpoint_category,
        
        -- Volume and errors
        sum(nombre_requetes) as total_requetes,
        sum(nombre_erreurs) as total_erreurs,
        sum(nombre_requetes_lentes) as total_requetes_lentes,
        
        -- Performance metrics
        round(avg(duration_avg_ms)::numeric, 2) as duration_avg_ms_global,
        round(max(duration_p99_ms)::numeric, 2) as duration_p99_ms_global,
        round(max(duration_max_ms)::numeric, 2) as duration_max_ms_global,
        round(min(duration_avg_ms)::numeric, 2) as duration_min_ms_global,
        
        -- Error rates
        avg(taux_erreur_pct) as taux_erreur_pct_avg,
        avg(taux_erreur_serveur_pct) as taux_erreur_serveur_pct_avg,
        
        -- Slow requests rate
        round(sum(nombre_requetes_lentes)::numeric / nullif(sum(nombre_requetes), 0) * 100, 2) as taux_requetes_lentes_pct,
        
        -- SLA Status
        case 
            when avg(taux_erreur_pct) <= 1 and round(avg(duration_avg_ms)::numeric, 2) <= 200 then 'OK'
            when avg(taux_erreur_pct) <= 2 and round(avg(duration_avg_ms)::numeric, 2) <= 500 then 'WARNING'
            else 'CRITICAL'
        end as sla_status,
        
        current_timestamp as dbt_processed_at
    
    from enriched_logs
    group by request_path, request_method, status_code, user_role, environment, endpoint_category
),

sla_summary as (
    select
        case 
            when sla_status = 'OK' then count(*)
            else 0
        end as endpoints_ok,
        case 
            when sla_status = 'WARNING' then count(*)
            else 0
        end as endpoints_warning,
        case 
            when sla_status = 'CRITICAL' then count(*)
            else 0
        end as endpoints_critical
    from daily_kpis
    group by sla_status
)

select
    {{ dbt_utils.generate_surrogate_key(['request_path', 'status_code', 'environment']) }} as api_perf_key,
    dk.*,
    (select coalesce(sum(endpoints_ok), 0) from sla_summary) as endpoints_ok,
    (select coalesce(sum(endpoints_warning), 0) from sla_summary) as endpoints_warning,
    (select coalesce(sum(endpoints_critical), 0) from sla_summary) as endpoints_critical
from daily_kpis dk

