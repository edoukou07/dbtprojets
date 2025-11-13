{{
    config(
        materialized='incremental',
        unique_key='facture_key',
        on_schema_change='append_new_columns'
    )
}}

with factures as (
    select * from {{ ref('stg_factures') }}
),

final as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['id', 'date_creation']) }} as facture_key,
        
        -- Clés étrangères (dimensions)
        cast(to_char(date_creation, 'YYYYMMDD') as integer) as date_creation_key,
        cast(to_char(coalesce(date_paiement, date_creation), 'YYYYMMDD') as integer) as date_paiement_key,
        entreprise_id,
        collecte_id,
        demande_attribution_id,
        ayant_droit_id,
        
        -- Clés naturelles
        id as facture_id,
        numero_facture,
        
        -- Mesures
        montant_total,
        sous_total,
        montant_total - sous_total as montant_taxes,
        
        -- Attributs
        statut,
        processus_origine,
        
        -- Dates
        date_creation,
        date_echeance,
        date_paiement,
        
        -- Calculs
        case 
            when date_paiement is not null then date_paiement - date_creation
            else current_date - date_creation
        end as delai_paiement_jours,
        
        case 
            when date_paiement is null and current_date > date_echeance then true
            else false
        end as est_en_retard,
        
        case 
            when date_paiement is not null then true
            else false
        end as est_paye,
        
        -- Audit
        created_by,
        updated_by,
        version
        
    from factures
    
    {% if is_incremental() %}
        where date_creation >= (select max(date_creation) from {{ this }})
    {% endif %}
)

select * from final
