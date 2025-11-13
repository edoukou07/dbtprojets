{{
    config(
        materialized='incremental',
        unique_key='collecte_key',
        on_schema_change='append_new_columns'
    )
}}

with collectes as (
    select * from {{ ref('stg_collectes') }}
),

final as (
    select
        -- Clé surrogate
        {{ dbt_utils.generate_surrogate_key(['id', 'date_debut']) }} as collecte_key,
        
        -- Clés étrangères (dimensions)
        cast(to_char(date_debut, 'YYYYMMDD') as integer) as date_debut_key,
        cast(to_char(date_fin_prevue, 'YYYYMMDD') as integer) as date_fin_prevue_key,
        cast(to_char(date_cloture, 'YYYYMMDD') as integer) as date_cloture_key,
        
        -- Clés naturelles
        id as collecte_id,
        reference,
        
        -- Mesures
        montant_a_recouvrer,
        montant_recouvre,
        montant_a_recouvrer - montant_recouvre as montant_restant,
        
        -- Ratios
        case 
            when montant_a_recouvrer > 0 
            then (montant_recouvre::numeric / montant_a_recouvrer::numeric) * 100
            else 0
        end as taux_recouvrement,
        
        -- Attributs
        status,
        statut_cloture,
        
        -- Dates
        date_debut,
        date_fin_prevue,
        date_cloture,
        date_generation_factures,
        
        -- Calculs
        (date_fin_prevue - date_debut) as duree_prevue_jours,
        
        case 
            when date_cloture is not null 
            then (date_cloture::date - date_debut)
            else (current_date - date_debut)
        end as duree_reelle_jours,
        
        -- Indicateurs
        factures_generees,
        
        case 
            when statut_cloture = 'cloturee' then true
            else false
        end as est_cloturee,
        
        case 
            when montant_recouvre >= montant_a_recouvrer then true
            else false
        end as est_complete,
        
        -- Audit
        cree_par,
        cloture_par
        
    from collectes
    
    {% if is_incremental() %}
        where date_debut >= (select max(date_debut) from {{ this }})
    {% endif %}
)

select * from final
