

with paiements as (
    select * from "sigeti_node_db"."dwh_staging"."stg_paiements"
),

factures as (
    select 
        id,
        entreprise_id,
        montant_total,
        collecte_id
    from "sigeti_node_db"."dwh_staging"."stg_factures"
),

final as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(p.id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(p.date_paiement as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as paiement_key,
        
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
    
    
        where p.date_paiement >= (select max(date_paiement) from "sigeti_node_db"."dwh_facts"."fait_paiements")
    
)

select * from final