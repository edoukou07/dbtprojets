-- Snapshot pour historiser les changements de statut des entreprises
-- Permet de tracer l'évolution dans le temps

{% snapshot snapshot_entreprises %}

{{
    config(
      target_schema='dwh_snapshots',
      unique_key='id',
      strategy='timestamp',
      updated_at='updated_at',
      invalidate_hard_deletes=True
    )
}}

select * from {{ source('sigeti_source', 'entreprises') }}

{% endsnapshot %}
