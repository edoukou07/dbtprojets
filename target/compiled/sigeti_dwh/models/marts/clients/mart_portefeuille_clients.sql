

-- Mart Clients - Analyse du portefeuille clients/entreprises
-- Matérialisé en table pour performance optimale des dashboards

with entreprises as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_entreprises"
),

domaines as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_domaines_activites"
),

factures as (
    select * from "sigeti_node_db"."dwh_facts"."fait_factures"
),

attributions as (
    select * from "sigeti_node_db"."dwh_facts"."fait_attributions"
),

lots as (
    select * from "sigeti_node_db"."dwh_dimensions"."dim_lots"
),

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
        count(distinct f.facture_id) as nombre_factures,
        sum(f.montant_total) as chiffre_affaires_total,
        sum(case when f.est_paye then f.montant_total else 0 end) as ca_paye,
        sum(case when not f.est_paye then f.montant_total else 0 end) as ca_impaye,
        
        -- Comportement de paiement
        avg(f.delai_paiement_jours) as delai_moyen_paiement,
        count(case when f.est_en_retard then 1 end) as nombre_factures_retard,
        
        round(
            (count(case when f.est_paye then 1 end)::numeric / 
             nullif(count(f.facture_id), 0)::numeric * 100), 
            2
        ) as taux_paiement_pct,
        
        -- Attributions
        count(distinct a.demande_id) as nombre_demandes,
        count(distinct case when a.est_approuve then a.demande_id end) as demandes_approuvees,
        sum(case when a.est_approuve then a.superficie_demandee else 0 end) as superficie_totale_attribuee,
        
        -- Lots
        count(distinct l.lot_id) as nombre_lots_attribues,
        
        -- Segmentation client
        case 
            when sum(f.montant_total) > 10000000 then 'Grand client'
            when sum(f.montant_total) > 1000000 then 'Client moyen'
            else 'Petit client'
        end as segment_client,
        
        case 
            when count(case when f.est_en_retard then 1 end)::numeric / 
                 nullif(count(f.facture_id), 0)::numeric > 0.3 then 'Risque élevé'
            when count(case when f.est_en_retard then 1 end)::numeric / 
                 nullif(count(f.facture_id), 0)::numeric > 0.1 then 'Risque moyen'
            else 'Risque faible'
        end as niveau_risque
        
    from entreprises e
    left join domaines d on e.domaine_activite_id = d.domaine_id
    left join factures f on e.entreprise_id = f.entreprise_id
    left join attributions a on e.entreprise_id = a.entreprise_id
    left join lots l on e.entreprise_id = l.entreprise_id and l.est_attribue
    
    group by 
        e.entreprise_id,
        e.raison_sociale,
        e.forme_juridique,
        e.registre_commerce,
        e.telephone,
        e.email,
        d.nom_domaine
)

select * from clients_stats
order by chiffre_affaires_total desc nulls last