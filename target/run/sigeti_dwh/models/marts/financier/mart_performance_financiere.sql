
  
    

  create  table "sigeti_node_db"."dwh_marts_financier"."mart_performance_financiere__dbt_tmp"
  
  
    as
  
  (
    

-- Financial Performance Mart - Corrected Logic

with factures as (
    select
        f.facture_id,
        f.montant_total,
        f.est_paye,
        f.delai_paiement_jours,
        f.date_creation,
        extract(year from f.date_creation)::int as annee,
        extract(month from f.date_creation)::int as mois,
        extract(quarter from f.date_creation)::int as trimestre
    from "sigeti_node_db"."dwh_facts"."fait_factures" f
),

collectes as (
    select
        c.collecte_id,
        c.montant_a_recouvrer,
        c.montant_recouvre,
        c.taux_recouvrement,
        c.duree_reelle_jours,
        extract(year from c.date_debut)::int as annee,
        extract(quarter from c.date_debut)::int as trimestre
    from "sigeti_node_db"."dwh_facts"."fait_collectes" c
),

factures_aggregees as (
    select
        f.annee,
        f.mois,
        f.trimestre,
        count(distinct f.facture_id) as nombre_factures,
        sum(f.montant_total) as montant_total_facture,
        sum(case when f.est_paye then f.montant_total else 0 end) as montant_paye,
        sum(case when not f.est_paye then f.montant_total else 0 end) as montant_impaye,
        round(avg(coalesce(extract(day from f.delai_paiement_jours), 0))::numeric, 2) as delai_moyen_paiement,
        round(
            (sum(case when f.est_paye then f.montant_total else 0 end)::numeric / 
             nullif(sum(f.montant_total), 0)::numeric * 100), 
            2
        ) as taux_paiement_pct
    from factures f
    group by f.annee, f.mois, f.trimestre
),

collectes_aggregees as (
    select
        c.annee,
        c.trimestre,
        count(distinct c.collecte_id) as nombre_collectes,
        sum(c.montant_a_recouvrer) as montant_total_a_recouvrer,
        sum(case when c.montant_recouvre > 0 then c.montant_recouvre else 0 end) as montant_total_recouvre,
        round(avg(coalesce(c.taux_recouvrement, 0))::numeric, 2) as taux_recouvrement_moyen,
        round(avg(abs(coalesce(c.duree_reelle_jours, 0)))::numeric, 1) as duree_moyenne_collecte
    from collectes c
    group by c.annee, c.trimestre
)

select
    f.annee,
    f.mois,
    f.trimestre,
    f.nombre_factures,
    f.montant_total_facture,
    f.montant_paye,
    f.montant_impaye,
    f.delai_moyen_paiement,
    f.taux_paiement_pct,
    coalesce(c.nombre_collectes, 0)::int as nombre_collectes,
    coalesce(c.montant_total_a_recouvrer, 0) as montant_total_a_recouvrer,
    coalesce(c.montant_total_recouvre, 0) as montant_total_recouvre,
    coalesce(c.taux_recouvrement_moyen, 0) as taux_recouvrement_moyen,
    coalesce(c.duree_moyenne_collecte, 0) as duree_moyenne_collecte
from factures_aggregees f
left join collectes_aggregees c 
    on f.annee = c.annee 
    and f.trimestre = c.trimestre
order by f.annee desc, f.mois desc
  );
  