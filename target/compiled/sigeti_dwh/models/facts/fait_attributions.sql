

with demandes as (
    select * from "sigeti_node_db"."dwh_staging"."stg_demandes_attribution"
),

lots as (
    select 
        id,
        superficie,
        prix,
        zone_industrielle_id
    from "sigeti_node_db"."dwh_staging"."stg_lots"
),

final as (
    select
        -- Clé surrogate
        md5(cast(coalesce(cast(d.id as TEXT), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(d.created_at as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) as attribution_key,
        
        -- Clés étrangères (dimensions)
        cast(to_char(d.created_at, 'YYYYMMDD') as integer) as date_demande_key,
        d.entreprise_id,
        d.lot_id,
        coalesce(d.zone_id, l.zone_industrielle_id) as zone_id,
        
        -- Clés naturelles
        d.id as demande_id,
        d.reference,
        
        -- Mesures
        l.superficie as superficie_demandee,
        l.prix as montant_attribution,
        
        -- Attributs
        d.statut,
        d.type_demande,
        d.etape_courante,
        d.priorite,
        
        -- Dates
        d.created_at as date_demande,
        d.updated_at as date_modification,
        
        -- Calculs
        case 
            when d.updated_at is not null 
            then extract(day from (d.updated_at - d.created_at))
            else extract(day from (current_timestamp - d.created_at))
        end as delai_traitement_jours,
        
        -- Indicateurs
        case 
            when d.statut::text in ('approuve', 'attribue', 'accepte') then true
            else false
        end as est_approuve,
        
        case 
            when d.statut::text = 'rejete' then true
            else false
        end as est_rejete,
        
        case 
            when d.statut::text in ('en_attente', 'en_cours') then true
            else false
        end as est_en_attente
        
    from demandes d
    left join lots l on d.lot_id = l.id
    
    
        where d.created_at >= (select max(date_demande) from "sigeti_node_db"."dwh_facts"."fait_attributions")
    
)

select * from final