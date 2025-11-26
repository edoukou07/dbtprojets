{{ config(
    materialized='table',
    schema='marts_compliance',
    indexes=[
        {'columns': ['request_path']},
        {'columns': ['status_code']}
    ],
    tags=['infrastructure', 'P3']
) }}

-- Data Mart: API Performance (SLA Monitoring)
-- Suivi de la performance et du SLA des API
-- Refresh: Real-time
-- Utilisateurs: Infra, Devops, Tech leads

with api_logs as (
    select * from {{ ref('fait_api_logs') }}
),

daily_kpis as (
    select
        request_path,
        request_method,
        status_code,
        user_role,
        
        -- Volume et erreurs
        sum(nombre_requetes) as total_requetes,
        sum(nombre_erreurs) as total_erreurs,
        sum(nombre_requetes_lentes) as total_requetes_lentes,
        
        -- Performance (cast to numeric for round function)
        round(avg(duration_avg_ms)::numeric, 2) as duration_avg_ms_global,
        round(max(duration_p99_ms)::numeric, 2) as duration_p99_ms_global,
        round(max(duration_max_ms)::numeric, 2) as duration_max_ms_global,
        
        -- Rates
        taux_erreur_pct,
        taux_erreur_serveur_pct,
        
        -- SLA Status
        case 
            when taux_erreur_pct <= 1 and round(avg(duration_avg_ms)::numeric, 2) <= 200 then 'OK'
            when taux_erreur_pct <= 2 and round(avg(duration_avg_ms)::numeric, 2) <= 500 then 'WARNING'
            else 'CRITICAL'
        end as sla_status,
        
        current_timestamp as dbt_processed_at
    
    from api_logs
    group by request_path, request_method, status_code, user_role, taux_erreur_pct, taux_erreur_serveur_pct
),

with_keys as (
    select
        {{ dbt_utils.generate_surrogate_key(['request_path', 'status_code']) }} as api_perf_key,
        *
    from daily_kpis
)

select * from with_keys

