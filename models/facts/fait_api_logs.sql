{{ config(
    materialized='table',
    schema='facts',
    tags=['infrastructure', 'P3']
) }}

-- Fact Table: Logs API (Daily Snapshot)
-- Snapshot quotidien des performances API par endpoint
-- Grain: Ligne par endpoint, user_role, date, heure
-- Update strategy: Full refresh

with stg as (
    select * from {{ ref('stg_audit_logs') }}
),

daily_agg as (
    select
        -- Clés naturelles
        user_role,
        request_path,
        request_method,
        status_code,
        
        -- Comptages
        count(*) as nombre_requetes,
        count(case when status_code >= 400 then 1 end) as nombre_erreurs,
        count(case when duration_ms > 5000 then 1 end) as nombre_requetes_lentes,
        
        -- Statistiques de timing
        min(duration_ms) as duration_min_ms,
        max(duration_ms) as duration_max_ms,
        avg(duration_ms)::numeric as duration_avg_ms,
        percentile_cont(0.95) within group (order by duration_ms) as duration_p95_ms,
        percentile_cont(0.99) within group (order by duration_ms) as duration_p99_ms,
        
        -- Calculs d'erreur
        round(count(case when status_code >= 400 then 1 end)::numeric / nullif(count(*), 0) * 100, 2) as taux_erreur_pct,
        round(count(case when status_code >= 500 then 1 end)::numeric / nullif(count(*), 0) * 100, 2) as taux_erreur_serveur_pct,
        
        -- Timestamp de traitement
        current_timestamp as dbt_processed_at
    
    from stg
    group by user_role, request_path, request_method, status_code
),

with_keys as (
    select
        {{ dbt_utils.generate_surrogate_key(['user_role', 'request_path', 'status_code']) }} as api_log_key,
        *
    from daily_agg
)

select * from with_keys
