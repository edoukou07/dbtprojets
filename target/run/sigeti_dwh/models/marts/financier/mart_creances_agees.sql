
  
    

  create  table "sigeti_node_db"."dwh_marts_financier"."mart_creances_agees__dbt_tmp"
  
  
    as
  
  (
    

-- Data Mart: Créances Âgées
-- Analysis des factures impayées par tranche d'ancienneté
-- Refresh: Quotidien
-- Utilisateurs: Finance, Direction commerciale

with factures as (
    select * from "sigeti_node_db"."dwh_facts"."fait_factures"
    where est_en_retard = true or montant_total > 0
),

calculs as (
    select
        entreprise_id,
        numero_facture,
        date_echeance,
        montant_total,
        
        case 
            when extract(day from current_date - date_echeance) between 0 and 30 then '0-30 jours'
            when extract(day from current_date - date_echeance) between 31 and 60 then '31-60 jours'
            when extract(day from current_date - date_echeance) between 61 and 90 then '61-90 jours'
            when extract(day from current_date - date_echeance) between 91 and 180 then '91-180 jours'
            when extract(day from current_date - date_echeance) > 180 then '> 180 jours'
            else 'A venir'
        end as tranche_anciennete,
        
        case 
            when extract(day from current_date - date_echeance) > 180 then 'CRITIQUE'
            when extract(day from current_date - date_echeance) > 90 then 'ELEVE'
            when extract(day from current_date - date_echeance) > 60 then 'MOYEN'
            else 'FAIBLE'
        end as niveau_risque,
        
        delai_paiement_jours
    
    from factures
    where date_echeance is not null
),

aggregated as (
    select
        tranche_anciennete,
        niveau_risque,
        
        -- Volumes
        count(*) as nombre_factures,
        count(distinct entreprise_id) as nombre_entreprises,
        
        -- Montants
        round(sum(montant_total)::numeric, 2) as montant_total_factures,
        round(avg(montant_total)::numeric, 2) as montant_moyen,
        
        -- Délais
        round(avg(extract(epoch from delai_paiement_jours)/86400)::numeric, 2) as delai_moyen_jours,
        max(extract(epoch from delai_paiement_jours)/86400) as delai_max_jours,
        
        current_timestamp as dbt_updated_at
    
    from calculs
    group by tranche_anciennete, niveau_risque
)

select * from aggregated
order by tranche_anciennete
  );
  