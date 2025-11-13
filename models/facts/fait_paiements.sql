{{
    config(
        materialized='incremental',
        unique_key='paiement_key',
        on_schema_change='append_new_columns'
    )
}}

with paiements as (
    select * from {{ ref('stg_paiements') }}
),

factures as (
    select 
        id,
        entreprise_id,
        montant_total,
        collecte_id
    from {{ ref('stg_factures') }}
),

final as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['p.id', 'p.date_paiement']) }} as paiement_key,
        
        -- Clés étrangères (dimensions)
        cast(to_char(p.date_paiement, 'YYYYMMDD') as integer) as date_paiement_key,
        f.entreprise_id,
        p.facture_id,
        f.collecte_id,
        
        -- Clés naturelles
        p.id as paiement_id,
        p.reference_paiement,
        
        -- Mesures
        p.montant as montant_paiement,
        f.montant_total as montant_facture,
        f.montant_total - p.montant as reste_a_payer,
        
        -- Attributs
        p.mode_paiement,
        p.statut,
        
        -- Dates
        p.date_paiement,
        
        -- Indicateurs
        case 
            when p.montant >= f.montant_total then true
            else false
        end as paiement_complet,
        
        case 
            when p.montant < f.montant_total then true
            else false
        end as paiement_partiel
        
    from paiements p
    left join factures f on p.facture_id = f.id
    
    {% if is_incremental() %}
        where p.date_paiement >= (select max(date_paiement) from {{ this }})
    {% endif %}
)

select * from final
