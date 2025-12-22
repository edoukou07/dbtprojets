

/*
    ================================================================
    Mart: Suivi des Dossiers d'Impenses
    ================================================================
    
    Vue consolidée de chaque dossier d'impense avec:
    - Durée totale de traitement
    - Temps passé dans chaque phase
    - Indicateurs de performance et productivité
    - Indicateurs géographiques (zone industrielle)
    - Indicateurs d'intervention par rôle
    - Indicateurs de qualité et prédiction
    - Alertes sur les dossiers en retard
    
    Granularité: Une ligne par dossier d'impense
    
    Utilisateurs: Direction, Gestionnaires de dossiers, Analystes
    
    Mise à jour: Décembre 2025 - Ajout indicateurs avancés
*/

-- =====================================================
-- SECTION 1: Métriques par dossier depuis les faits
-- =====================================================
with metriques_dossier as (
    select
        f.impense_id,
        
        -- Volume d'actions
        count(*) as nb_actions_total,
        count(distinct f.action) as nb_types_actions,
        count(distinct f.agent_id) as nb_agents_impliques,
        count(distinct f.user_role) as nb_roles_impliques,
        
        -- Première et dernière action
        min(f.date_action) as date_premiere_action,
        max(f.date_action) as date_derniere_action,
        
        -- Durée totale (en jours)
        extract(day from (max(f.date_action) - min(f.date_action))) as duree_totale_jours,
        extract(epoch from (max(f.date_action) - min(f.date_action))) / 3600 as duree_totale_heures,
        
        -- Temps par phase (agrégé)
        sum(case when p.phase_id = 1 then f.duree_minutes else 0 end) as temps_phase1_minutes,
        sum(case when p.phase_id = 2 then f.duree_minutes else 0 end) as temps_phase2_minutes,
        sum(case when p.phase_id = 3 then f.duree_minutes else 0 end) as temps_phase3_minutes,
        sum(case when p.phase_id = 4 then f.duree_minutes else 0 end) as temps_phase4_minutes,
        sum(case when p.phase_id = 5 then f.duree_minutes else 0 end) as temps_phase5_minutes,
        sum(case when p.phase_id = 6 then f.duree_minutes else 0 end) as temps_phase6_minutes,
        
        -- Compteurs par type d'action
        sum(f.est_validation) as nb_validations,
        sum(f.est_rejet) as nb_rejets,
        sum(f.est_correction) as nb_corrections,
        sum(f.est_cloture) as nb_clotures,
        
        -- NOUVEAUX: Compteurs d'actions spécifiques
        sum(case when f.action = 'RETOUR' then 1 else 0 end) as nb_retours,
        sum(case when f.action = 'SOUMISSION' then 1 else 0 end) as nb_soumissions,
        sum(case when f.action = 'UPLOAD_DOCUMENT' then 1 else 0 end) as nb_documents_uploades,
        sum(case when f.action = 'INVALIDATION_RECEVABILITE' then 1 else 0 end) as nb_invalidations_recevabilite,
        sum(case when f.action = 'VALIDATION_RECEVABILITE' then 1 else 0 end) as nb_validations_recevabilite,
        
        -- NOUVEAUX: Compteurs par rôle
        sum(case when f.user_role = 'admin' then 1 else 0 end) as nb_interventions_admin,
        sum(case when f.user_role = 'operateur' then 1 else 0 end) as nb_interventions_operateur,
        sum(case when f.user_role = 'utilisateur' then 1 else 0 end) as nb_interventions_utilisateur,
        
        -- Dernière phase atteinte
        max(p.phase_id) as derniere_phase_atteinte,
        
        -- Phase avec le plus de temps
        null::integer as phase_la_plus_longue  -- calculé plus bas
        
    from "sigeti_node_db"."dwh_facts"."fait_workflow_impenses" f
    left join "sigeti_node_db"."dwh_dimensions"."dim_phases_impenses" p on f.phase_impense_key = p.phase_impense_key
    group by f.impense_id
),

-- =====================================================
-- SECTION 1B: Agent principal par dossier
-- =====================================================
agent_principal as (
    select distinct on (impense_id)
        impense_id,
        agent_id as agent_principal_id,
        user_role as agent_principal_role,
        count(*) over (partition by impense_id, agent_id) as nb_actions_agent_principal
    from "sigeti_node_db"."dwh_facts"."fait_workflow_impenses"
    order by impense_id, count(*) over (partition by impense_id, agent_id) desc
),

-- =====================================================
-- SECTION 1C: Temps entre actions (délai moyen de réponse)
-- =====================================================
delais_entre_actions as (
    select 
        impense_id,
        date_action,
        lag(date_action) over (partition by impense_id order by date_action) as date_action_precedente,
        extract(epoch from (date_action - lag(date_action) over (partition by impense_id order by date_action))) / 3600 as delai_heures
    from "sigeti_node_db"."dwh_facts"."fait_workflow_impenses"
),

delais_actions as (
    select 
        impense_id,
        avg(delai_heures) as delai_moyen_reponse_heures,
        max(delai_heures) as delai_max_reponse_heures
    from delais_entre_actions
    where delai_heures is not null
    group by impense_id
),

-- =====================================================
-- SECTION 1D: Zone industrielle
-- =====================================================
zones as (
    select 
        id as zone_id,
        code as zone_code,
        libelle as zone_libelle,
        adresse as zone_adresse,
        superficie as zone_superficie_totale
    from "sigeti_node_db"."public"."zones_industrielles"
),

-- =====================================================
-- SECTION 1E: Informations lot enrichies
-- =====================================================
lots_info as (
    select
        l.id as lot_id,
        l.numero as lot_numero,
        l.superficie as lot_superficie,
        l.prix as lot_prix,
        l.statut as lot_statut,
        l.viabilite as lot_viabilite,
        l.zone_industrielle_id,
        z.zone_code,
        z.zone_libelle,
        z.zone_adresse
    from "sigeti_node_db"."public"."lots" l
    left join zones z on l.zone_industrielle_id = z.zone_id
),

-- =====================================================
-- SECTION 2: Jointure avec dimension impenses
-- =====================================================
dossiers_enrichis as (
    select
        di.impense_key,
        di.impense_id,
        di.numero_dossier,
        
        -- Lot avec enrichissement zone
        di.lot_id,
        coalesce(li.lot_numero, di.lot_numero) as lot_numero,
        coalesce(li.lot_superficie, di.lot_superficie_m2) as lot_superficie_m2,
        li.lot_prix,
        li.lot_statut,
        li.lot_viabilite,
        di.zone_industrielle_id,
        li.zone_code as zone_industrielle_code,
        li.zone_libelle as zone_industrielle_libelle,
        li.zone_adresse as zone_industrielle_adresse,
        
        -- Entreprise
        di.entreprise_id,
        di.nom_operateur,
        di.nom_entreprise,
        di.secteur_activite,
        
        -- Statut
        di.statut_actuel,
        di.statut_libelle,
        di.phase_actuelle,
        di.type_demande,
        di.motif_cession,
        
        -- Décisions
        di.decision_verification,
        di.resultat_analyse,
        di.a_decision_verification,
        di.a_resultat_analyse,
        di.est_analyse,
        di.est_cloture,
        
        -- Dates clés
        di.date_creation,
        di.date_emission,
        di.date_transmission,
        di.date_analyse,
        
        -- Métriques workflow de base
        coalesce(m.nb_actions_total, 0) as nb_actions_total,
        coalesce(m.nb_types_actions, 0) as nb_types_actions,
        coalesce(m.nb_agents_impliques, 0) as nb_agents_impliques,
        coalesce(m.nb_roles_impliques, 0) as nb_roles_impliques,
        
        m.date_premiere_action,
        m.date_derniere_action,
        coalesce(m.duree_totale_jours, 0) as duree_totale_jours,
        coalesce(m.duree_totale_heures, 0) as duree_totale_heures,
        
        -- Temps par phase
        coalesce(m.temps_phase1_minutes, 0) / 60.0 as temps_phase1_heures,
        coalesce(m.temps_phase2_minutes, 0) / 60.0 as temps_phase2_heures,
        coalesce(m.temps_phase3_minutes, 0) / 60.0 as temps_phase3_heures,
        coalesce(m.temps_phase4_minutes, 0) / 60.0 as temps_phase4_heures,
        coalesce(m.temps_phase5_minutes, 0) / 60.0 as temps_phase5_heures,
        coalesce(m.temps_phase6_minutes, 0) / 60.0 as temps_phase6_heures,
        
        -- Compteurs de base
        coalesce(m.nb_validations, 0) as nb_validations,
        coalesce(m.nb_rejets, 0) as nb_rejets,
        coalesce(m.nb_corrections, 0) as nb_corrections,
        coalesce(m.nb_clotures, 0) as nb_clotures,
        
        -- NOUVEAUX: Compteurs actions spécifiques
        coalesce(m.nb_retours, 0) as nb_retours,
        coalesce(m.nb_soumissions, 0) as nb_soumissions,
        coalesce(m.nb_documents_uploades, 0) as nb_documents_uploades,
        coalesce(m.nb_invalidations_recevabilite, 0) as nb_invalidations_recevabilite,
        coalesce(m.nb_validations_recevabilite, 0) as nb_validations_recevabilite,
        
        -- NOUVEAUX: Interventions par rôle
        coalesce(m.nb_interventions_admin, 0) as nb_interventions_admin,
        coalesce(m.nb_interventions_operateur, 0) as nb_interventions_operateur,
        coalesce(m.nb_interventions_utilisateur, 0) as nb_interventions_utilisateur,
        
        -- NOUVEAUX: Agent principal
        ap.agent_principal_id,
        ap.agent_principal_role,
        coalesce(ap.nb_actions_agent_principal, 0) as nb_actions_agent_principal,
        
        -- NOUVEAUX: Délais de réponse
        coalesce(da.delai_moyen_reponse_heures, 0) as delai_moyen_reponse_heures,
        coalesce(da.delai_max_reponse_heures, 0) as delai_max_reponse_heures,
        
        m.derniere_phase_atteinte
        
    from "sigeti_node_db"."dwh_dimensions"."dim_impenses" di
    left join metriques_dossier m on di.impense_id = m.impense_id
    left join agent_principal ap on di.impense_id = ap.impense_id
    left join delais_actions da on di.impense_id = da.impense_id
    left join lots_info li on di.lot_id = li.lot_id
),

-- =====================================================
-- SECTION 3: Calculs finaux et alertes
-- =====================================================
final as (
    select
        -- ===========================================
        -- IDENTIFICATION
        -- ===========================================
        impense_key,
        impense_id,
        numero_dossier,
        
        -- ===========================================
        -- LOT ET ZONE INDUSTRIELLE
        -- ===========================================
        lot_id,
        lot_numero,
        lot_superficie_m2,
        lot_prix,
        lot_statut,
        lot_viabilite,
        zone_industrielle_id,
        zone_industrielle_code,
        zone_industrielle_libelle,
        zone_industrielle_adresse,
        
        -- ===========================================
        -- ENTREPRISE / OPÉRATEUR
        -- ===========================================
        entreprise_id,
        nom_operateur,
        nom_entreprise,
        secteur_activite,
        
        -- ===========================================
        -- STATUT ET TYPE DE DEMANDE
        -- ===========================================
        statut_actuel,
        statut_libelle,
        phase_actuelle,
        case phase_actuelle
            when 1 then 'Phase 1: Création'
            when 2 then 'Phase 2: Vérification'
            when 3 then 'Phase 3: Analyse'
            when 4 then 'Phase 4: Validation DI'
            when 5 then 'Phase 5: Validation DG'
            when 6 then 'Phase 6: Visite évaluation'
            when 7 then 'Phase 7: Clôture'
            else 'Non défini'
        end as phase_actuelle_libelle,
        type_demande,
        motif_cession,
        
        -- ===========================================
        -- DÉCISIONS ET ANALYSE
        -- ===========================================
        decision_verification,
        resultat_analyse,
        a_decision_verification,
        a_resultat_analyse,
        est_analyse,
        est_cloture,
        
        -- ===========================================
        -- DATES CLÉS
        -- ===========================================
        date_creation,
        date_emission,
        date_transmission,
        date_analyse,
        date_premiere_action,
        date_derniere_action,
        
        -- ===========================================
        -- INDICATEURS TEMPORELS AVANCÉS
        -- ===========================================
        extract(week from date_creation) as semaine_creation,
        to_char(date_creation, 'YYYY-MM') as mois_creation,
        to_char(date_creation, 'YYYY') || '-Q' || extract(quarter from date_creation) as trimestre_creation,
        extract(dow from date_creation) as jour_semaine_creation,
        case when extract(dow from date_creation) in (0, 6) then true else false end as est_weekend_creation,
        extract(day from (current_timestamp - date_creation)) as anciennete_dossier_jours,
        
        -- ===========================================
        -- DURÉES DE TRAITEMENT
        -- ===========================================
        round(duree_totale_jours::numeric, 1) as duree_totale_jours,
        round(duree_totale_heures::numeric, 1) as duree_totale_heures,
        
        -- Temps par phase (heures)
        round(temps_phase1_heures::numeric, 1) as temps_phase1_heures,
        round(temps_phase2_heures::numeric, 1) as temps_phase2_heures,
        round(temps_phase3_heures::numeric, 1) as temps_phase3_heures,
        round(temps_phase4_heures::numeric, 1) as temps_phase4_heures,
        round(temps_phase5_heures::numeric, 1) as temps_phase5_heures,
        round(temps_phase6_heures::numeric, 1) as temps_phase6_heures,
        
        -- Phase la plus longue
        case 
            when greatest(temps_phase1_heures, temps_phase2_heures, temps_phase3_heures, 
                         temps_phase4_heures, temps_phase5_heures, temps_phase6_heures) = temps_phase1_heures then 'Phase 1: Création'
            when greatest(temps_phase1_heures, temps_phase2_heures, temps_phase3_heures, 
                         temps_phase4_heures, temps_phase5_heures, temps_phase6_heures) = temps_phase2_heures then 'Phase 2: Vérification'
            when greatest(temps_phase1_heures, temps_phase2_heures, temps_phase3_heures, 
                         temps_phase4_heures, temps_phase5_heures, temps_phase6_heures) = temps_phase3_heures then 'Phase 3: Analyse'
            when greatest(temps_phase1_heures, temps_phase2_heures, temps_phase3_heures, 
                         temps_phase4_heures, temps_phase5_heures, temps_phase6_heures) = temps_phase4_heures then 'Phase 4: Validation DI'
            when greatest(temps_phase1_heures, temps_phase2_heures, temps_phase3_heures, 
                         temps_phase4_heures, temps_phase5_heures, temps_phase6_heures) = temps_phase5_heures then 'Phase 5: Validation DG'
            else 'Phase 6: Visite'
        end as phase_la_plus_longue,
        
        -- ===========================================
        -- MÉTRIQUES WORKFLOW (Volume)
        -- ===========================================
        nb_actions_total,
        nb_types_actions,
        nb_agents_impliques,
        nb_roles_impliques,
        nb_validations,
        nb_rejets,
        nb_corrections,
        nb_clotures,
        derniere_phase_atteinte,
        
        -- ===========================================
        -- NOUVEAUX: COMPTEURS ACTIONS SPÉCIFIQUES
        -- ===========================================
        nb_retours,
        nb_soumissions,
        nb_documents_uploades,
        nb_invalidations_recevabilite,
        nb_validations_recevabilite,
        
        -- Allers-retours (cycles de correction)
        nb_retours as nb_allers_retours,
        
        -- ===========================================
        -- NOUVEAUX: INDICATEURS PAR RÔLE
        -- ===========================================
        nb_interventions_admin,
        nb_interventions_operateur,
        nb_interventions_utilisateur,
        
        -- Ratio admin/opérateur
        case 
            when nb_interventions_operateur > 0 
            then round((nb_interventions_admin::float / nb_interventions_operateur)::numeric, 2)
            else null 
        end as ratio_admin_operateur,
        
        -- ===========================================
        -- NOUVEAUX: AGENT PRINCIPAL
        -- ===========================================
        agent_principal_id,
        agent_principal_role,
        nb_actions_agent_principal,
        
        -- ===========================================
        -- NOUVEAUX: DÉLAIS DE RÉPONSE
        -- ===========================================
        round(delai_moyen_reponse_heures::numeric, 1) as delai_moyen_reponse_heures,
        round(delai_max_reponse_heures::numeric, 1) as delai_max_reponse_heures,
        
        -- ===========================================
        -- INDICATEURS DE PERFORMANCE
        -- ===========================================
        case 
            when nb_actions_total > 0 then round((nb_rejets::float / nb_actions_total * 100)::numeric, 1)
            else 0 
        end as taux_rejet_pct,
        
        case 
            when nb_actions_total > 0 then round((nb_corrections::float / nb_actions_total * 100)::numeric, 1)
            else 0 
        end as taux_correction_pct,
        
        -- NOUVEAU: Taux first pass (validé sans retour)
        case 
            when nb_validations > 0 and nb_retours = 0 then 100.0
            when nb_validations > 0 then round(((nb_validations - nb_retours)::float / nb_validations * 100)::numeric, 1)
            else 0 
        end as taux_first_pass_pct,
        
        -- NOUVEAU: Efficacité (actions par jour)
        case 
            when duree_totale_jours > 0 then round((nb_actions_total::float / duree_totale_jours)::numeric, 2)
            else nb_actions_total::numeric
        end as efficacite_actions_par_jour,
        
        -- Jours depuis dernière action
        extract(day from (current_timestamp - date_derniere_action)) as jours_depuis_derniere_action,
        
        -- ===========================================
        -- NOUVEAUX: INDICATEURS DE QUALITÉ
        -- ===========================================
        -- Documents uploadés suffisants
        case when nb_documents_uploades >= 2 then true else false end as a_documents_complets,
        
        -- Recevabilité validée
        case when nb_validations_recevabilite > 0 then true else false end as recevabilite_validee,
        
        -- ===========================================
        -- NOUVEAUX: INDICATEURS DE PRÉDICTION
        -- ===========================================
        -- Durée estimée restante (basée sur moyenne 5 jours/phase)
        case 
            when statut_actuel = 'clôturé' then 0
            else (7 - coalesce(derniere_phase_atteinte, phase_actuelle)) * 5
        end as duree_estimee_restante_jours,
        
        -- Date estimée de clôture
        case 
            when statut_actuel = 'clôturé' then null
            else current_date + ((7 - coalesce(derniere_phase_atteinte, phase_actuelle)) * 5)
        end as date_estimee_cloture,
        
        -- Score de complexité (0-100)
        least(100, (
            nb_retours * 15 +
            nb_agents_impliques * 5 +
            nb_documents_uploades * 3 +
            nb_invalidations_recevabilite * 20 +
            case when duree_totale_jours > 30 then 20 else 0 end
        )) as complexite_score,
        
        -- ===========================================
        -- ALERTES ET FLAGS
        -- ===========================================
        case 
            when statut_actuel != 'clôturé' and extract(day from (current_timestamp - date_derniere_action)) > 7 then true
            else false
        end as est_inactif,
        
        case 
            when statut_actuel != 'clôturé' and duree_totale_jours > 30 then true
            else false
        end as est_en_retard,
        
        case 
            when nb_rejets > 2 then true
            else false
        end as a_rejets_multiples,
        
        case 
            when nb_corrections > 5 then true
            else false
        end as a_corrections_excessives,
        
        -- NOUVEAU: Risque d'abandon
        case 
            when statut_actuel != 'clôturé' and extract(day from (current_timestamp - date_derniere_action)) > 30 then true
            else false
        end as risque_abandon,
        
        -- Score de santé du dossier (0-100, 100 = parfait)
        100 - (
            case when duree_totale_jours > 30 then 20 else 0 end +
            case when nb_rejets > 2 then 20 else 0 end +
            case when nb_corrections > 5 then 20 else 0 end +
            case when extract(day from (current_timestamp - date_derniere_action)) > 7 and statut_actuel != 'clôturé' then 20 else 0 end +
            case when phase_actuelle < derniere_phase_atteinte then 20 else 0 end
        ) as score_sante_dossier,
        
        -- Niveau d'alerte
        case 
            when statut_actuel = 'clôturé' then 'TERMINE'
            when duree_totale_jours > 60 or nb_rejets > 3 then 'CRITIQUE'
            when duree_totale_jours > 30 or nb_rejets > 2 then 'ALERTE'
            when extract(day from (current_timestamp - date_derniere_action)) > 7 then 'ATTENTION'
            else 'NORMAL'
        end as niveau_alerte,
        
        -- ===========================================
        -- NOUVEAUX: SLA / CONFORMITÉ
        -- ===========================================
        -- SLA Phase 1 : max 2 jours
        case when temps_phase1_heures <= 48 then true else false end as sla_phase1_respecte,
        -- SLA Phase 2 : max 3 jours  
        case when temps_phase2_heures <= 72 then true else false end as sla_phase2_respecte,
        -- SLA Phase 3 : max 5 jours
        case when temps_phase3_heures <= 120 then true else false end as sla_phase3_respecte,
        
        -- Nombre de SLA dépassés
        (case when temps_phase1_heures > 48 then 1 else 0 end +
         case when temps_phase2_heures > 72 then 1 else 0 end +
         case when temps_phase3_heures > 120 then 1 else 0 end) as nb_sla_depasses,
        
        -- Taux conformité SLA
        case 
            when derniere_phase_atteinte >= 3 then
                round((
                    (case when temps_phase1_heures <= 48 then 1 else 0 end +
                     case when temps_phase2_heures <= 72 then 1 else 0 end +
                     case when temps_phase3_heures <= 120 then 1 else 0 end)::float / 3 * 100
                )::numeric, 1)
            when derniere_phase_atteinte = 2 then
                round((
                    (case when temps_phase1_heures <= 48 then 1 else 0 end +
                     case when temps_phase2_heures <= 72 then 1 else 0 end)::float / 2 * 100
                )::numeric, 1)
            when derniere_phase_atteinte = 1 then
                case when temps_phase1_heures <= 48 then 100.0 else 0.0 end
            else null
        end as taux_conformite_sla_pct,
        
        -- ===========================================
        -- METADATA
        -- ===========================================
        current_timestamp as dbt_created_at
        
    from dossiers_enrichis
)

select * from final
order by 
    case niveau_alerte 
        when 'CRITIQUE' then 1 
        when 'ALERTE' then 2 
        when 'ATTENTION' then 3 
        when 'NORMAL' then 4 
        else 5 
    end,
    duree_totale_jours desc