-- =====================================================================
-- MACROS PERSONNALISÉES POUR LE PROJET SIGETI
-- =====================================================================

-- Macro pour calculer le DSO (Days Sales Outstanding)
{% macro calculate_dso(facture_table, paiement_table) %}
    (
        SUM(CASE 
            WHEN {{ facture_table }}.statut_paiement != 'paye' 
            THEN EXTRACT(DAY FROM (CURRENT_DATE - {{ facture_table }}.date_emission))
            ELSE 0 
        END) / NULLIF(COUNT(*), 0)
    ) as dso_moyen
{% endmacro %}

-- Macro pour formater les montants en FCFA
{% macro format_fcfa(column_name) %}
    CONCAT(TO_CHAR({{ column_name }}, 'FM999,999,999'), ' FCFA') as {{ column_name }}_formatted
{% endmacro %}

-- Macro pour classifier les entreprises par taille
{% macro classify_enterprise_size(revenue_column) %}
    CASE
        WHEN {{ revenue_column }} < 50000000 THEN 'TPE'
        WHEN {{ revenue_column }} < 500000000 THEN 'PME'
        WHEN {{ revenue_column }} < 5000000000 THEN 'ETI'
        ELSE 'GE'
    END as taille_entreprise
{% endmacro %}

-- Macro pour calculer le taux de remplissage
{% macro fill_rate(column_name) %}
    ROUND(
        (COUNT({{ column_name }})::NUMERIC / COUNT(*)::NUMERIC) * 100,
        2
    ) as {{ column_name }}_fill_rate_pct
{% endmacro %}

-- Macro pour créer une clé de date au format YYYYMMDD
{% macro date_key(date_column) %}
    TO_CHAR({{ date_column }}, 'YYYYMMDD')::INTEGER
{% endmacro %}

-- Macro pour gérer les divisions par zéro
{% macro safe_divide(numerator, denominator) %}
    CASE 
        WHEN {{ denominator }} = 0 OR {{ denominator }} IS NULL 
        THEN 0 
        ELSE {{ numerator }}::NUMERIC / {{ denominator }}::NUMERIC 
    END
{% endmacro %}

-- Macro pour calculer la variation en pourcentage
{% macro percent_change(current_value, previous_value) %}
    {{ safe_divide(
        '(' ~ current_value ~ ' - ' ~ previous_value ~ ') * 100',
        previous_value
    ) }}
{% endmacro %}

-- Macro pour créer des colonnes d'audit
{% macro audit_columns() %}
    CURRENT_TIMESTAMP as dbt_loaded_at,
    '{{ invocation_id }}' as dbt_run_id,
    '{{ this }}' as dbt_model_name
{% endmacro %}
