
  
    

  create  table "sigeti_node_db"."dwh_marts_clients"."mart_portefeuille_clients__dbt_tmp"
  
  
    as
  
  (
    

-- Mart Clients - Analyse du portefeuille clients/entreprises
-- Materialized en table pour performance optimale des dashboards
-- Structure: Pre-aggregation dans CTEs separees pour eviter les doublocomptes de JOINs

with entreprises as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
),

domaines as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_domaines_activites"
),

factures_raw as (
    select * from "sigeti_node_db"."dwh_facts"."fait_factures"
),

attributions_raw as (
    select * from "sigeti_node_db"."dwh_facts"."fait_attributions"
),

lots_raw as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_lots"
),

-- Pre-aggregate factures by entreprise_id to avoid multiplications
factures_stats as (
    select
        f.entreprise_id,
        count(distinct f.facture_id) as nombre_factures,
        sum(f.montant_total) as chiffre_affaires_total,
        sum(case when f.est_paye then f.montant_total else 0 end) as ca_paye,
        sum(case when not f.est_paye then f.montant_total else 0 end) as ca_impaye,
        avg(f.delai_paiement_jours) as delai_moyen_paiement,
        count(case when f.est_en_retard then 1 end) as nombre_factures_retard,
        round(
            (count(case when f.est_paye then 1 end)::numeric / 
             nullif(count(f.facture_id), 0)::numeric * 100), 
            2
        ) as taux_paiement_pct
    from factures_raw f
    group by f.entreprise_id
),

-- Pre-aggregate attributions by entreprise_id to avoid multiplications
attributions_stats as (
    select
        a.entreprise_id,
        count(distinct a.demande_id) as nombre_demandes,
        count(distinct case when a.est_approuve then a.demande_id end) as demandes_approuvees,
        sum(case when a.est_approuve then a.superficie_demandee else 0 end) as superficie_totale_attribuee
    from attributions_raw a
    group by a.entreprise_id
),

-- Pre-aggregate lots by entreprise_id to avoid multiplications
lots_stats as (
    select
        l.entreprise_id,
        count(distinct l.lot_id) as nombre_lots_attribues
    from lots_raw l
    where l.est_attribue
    group by l.entreprise_id
),

-- Final join with pre-aggregated data - no risk of row multiplication
clients_stats as (
    select
        e.entreprise_id,
        e.raison_sociale,
        e.forme_juridique,
        e.registre_commerce,
        e.telephone,
        e.email,
        d.nom_domaine as secteur_activite,
        
        -- Facturation
        coalesce(f.nombre_factures, 0) as nombre_factures,
        coalesce(f.chiffre_affaires_total, 0) as chiffre_affaires_total,
        coalesce(f.ca_paye, 0) as ca_paye,
        coalesce(f.ca_impaye, 0) as ca_impaye,
        f.delai_moyen_paiement,
        coalesce(f.nombre_factures_retard, 0) as nombre_factures_retard,
        f.taux_paiement_pct,
        
        -- Attributions
        coalesce(a.nombre_demandes, 0) as nombre_demandes,
        coalesce(a.demandes_approuvees, 0) as demandes_approuvees,
        coalesce(a.superficie_totale_attribuee, 0) as superficie_totale_attribuee,
        
        -- Lots
        coalesce(l.nombre_lots_attribues, 0) as nombre_lots_attribues,
        
        -- Segmentation client
        case 
            when coalesce(f.chiffre_affaires_total, 0) > 10000000 then 'Grand client'
            when coalesce(f.chiffre_affaires_total, 0) > 1000000 then 'Client moyen'
            else 'Petit client'
        end as segment_client,
        
        case 
            when coalesce(f.nombre_factures_retard, 0)::numeric / 
                 nullif(coalesce(f.nombre_factures, 0), 0)::numeric > 0.3 then 'Risque elevé'
            when coalesce(f.nombre_factures_retard, 0)::numeric / 
                 nullif(coalesce(f.nombre_factures, 0), 0)::numeric > 0.1 then 'Risque moyen'
            else 'Risque faible'
        end as niveau_risque
        
    from entreprises e
    left join domaines d on e.domaine_activite_id = d.domaine_id
    left join factures_stats f on e.entreprise_id = f.entreprise_id
    left join attributions_stats a on e.entreprise_id = a.entreprise_id
    left join lots_stats l on e.entreprise_id = l.entreprise_id
)

select * from clients_stats
order by chiffre_affaires_total desc nulls last
  );
  