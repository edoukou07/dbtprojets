{% macro fix_data() %}
  {%- if execute -%}
    {% do log("Fixing negative durations in database", info=true) %}
    {% set _ = run_query("UPDATE dwh_facts.fait_collectes SET duree_reelle_jours = ABS(duree_reelle_jours) WHERE duree_reelle_jours < 0", execute=true) %}
    {% do log("Dropping old mart table", info=true) %}
    {% set _ = run_query("DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE", execute=true) %}
  {%- endif -%}
{% endmacro %}
