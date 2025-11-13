

with collectes as (
    select * from "sigeti_node_db"."dwh_staging"."stg_collectes"
),

final as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(date_debut as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as collecte_key,
        
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
    
    
        where date_debut >= (select max(date_debut) from "sigeti_node_db"."dwh_facts"."fait_collectes")
    
)

select * from final