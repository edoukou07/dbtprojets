{% macro fix_warehouse_data() %}
  {%- if execute -%}
    {%- set sql -%}
      UPDATE dwh_facts.fait_collectes
      SET duree_reelle_jours = ABS(duree_reelle_jours)
      WHERE duree_reelle_jours < 0;
      DROP TABLE IF EXISTS dwh_marts_financier.mart_performance_financiere CASCADE;
    {%- endset -%}
    {%- do run_query(sql) -%}
    {%- do log("Corrections applied - Negative durations and old mart table removed", info=true) -%}
  {%- endif -%}
{% endmacro %}
