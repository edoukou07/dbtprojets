
  create view "sigeti_node_db"."dwh_staging"."stg_audit_logs__dbt_tmp"
    
    
  as (
    

-- Staging: Audit Logs (API Performance)
-- Extract et validation des logs d'audit pour tracking API
-- Source: audit_logs table
-- Grain: Une ligne par requête API

with raw_audit_logs as (
    select
        id,
        user_id,
        request_path,
        request_method,
        status_code,
        duration_ms,
        created_at,
        user_role,
        ip_address,
        table_name,
        record_id,
        action,
        user_name,
        error_message
    from "sigeti_node_db"."public"."audit_logs"
),

validated as (
    select
        -- Clés naturelles
        id as log_id,
        user_id,
        
        -- Request
        request_path,
        request_method,
        
        -- Response
        status_code,
        duration_ms,
        
        -- Context
        user_role,
        ip_address as user_ip,
        table_name,
        record_id,
        action,
        user_name,
        error_message,
        
        -- Dates
        created_at::timestamp as created_at,
        cast(to_char(created_at, 'YYYYMMDD') as int) as date_key,
        extract(hour from created_at) as heure,
        extract(dow from created_at) as jour_semaine,
        
        -- Validations
        case when status_code >= 400 then 1 else 0 end as est_erreur,
        case when status_code >= 500 then 1 else 0 end as est_erreur_serveur,
        case when duration_ms > 1000 then 1 else 0 end as est_lent,
        
        -- Indicateurs
        case when status_code >= 200 and status_code < 300 then 'SUCCESS'
             when status_code >= 300 and status_code < 400 then 'REDIRECT'
             when status_code >= 400 and status_code < 500 then 'CLIENT_ERROR'
             when status_code >= 500 then 'SERVER_ERROR'
             else 'UNKNOWN'
        end as status_category,
        
        -- Catégorisation endpoint
        case 
            when request_path like '/api/conventions/%' then 'conventions'
            when request_path like '/api/collectes/%' then 'collectes'
            when request_path like '/api/infractions/%' then 'infractions'
            when request_path like '/api/attributions/%' then 'attributions'
            when request_path like '/api/indemnisations/%' then 'indemnisations'
            else 'other'
        end as endpoint_category,
        
        -- Audit
        current_timestamp as dbt_extracted_at
    
    from raw_audit_logs
    where id is not null
)

select * from validated
  );