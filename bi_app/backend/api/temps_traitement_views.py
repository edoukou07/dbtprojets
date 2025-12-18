"""
API Views for Temps Traitement & Goulots d'Étranglement Dashboard
Includes Performance Agents analysis (integrated view)
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection


class TempsTraitementViewSet(viewsets.ViewSet):
    """
    ViewSet for Temps de Traitement & Goulots d'Étranglement dashboard.
    
    Available endpoints:
    - summary: Overview of processing times and bottlenecks
    - goulots: Detailed bottleneck analysis
    - etapes_details: Processing time by step
    - tendances: Processing time trends
    - recommandations: Optimization recommendations
    - performance_agents_summary: Overview of agent performance
    - performance_agents: Detailed agent performance per step
    - performance_agents_comparison: Compare agents on same step
    """
    permission_classes = [AllowAny]  # Allow access without authentication for development

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary overview of processing times and bottlenecks
        
        Returns:
        - Global KPIs
        - Bottleneck distribution
        - Critical steps count
        """
        with connection.cursor() as cursor:
            # Global KPIs
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_etapes,
                    SUM(CASE WHEN est_goulot_etranglement THEN 1 ELSE 0 END) as nb_goulots,
                    SUM(CASE WHEN niveau_goulot = 'CRITIQUE' THEN 1 ELSE 0 END) as nb_critiques,
                    SUM(CASE WHEN niveau_goulot = 'MAJEUR' THEN 1 ELSE 0 END) as nb_majeurs,
                    SUM(CASE WHEN niveau_goulot = 'MODERE' THEN 1 ELSE 0 END) as nb_moderes,
                    ROUND(AVG(duree_moyenne_minutes)::numeric, 2) as duree_moyenne_globale_min,
                    ROUND(SUM(temps_total_heures)::numeric, 2) as temps_total_workflow_heures,
                    ROUND(SUM(gain_potentiel_heures)::numeric, 2) as gain_potentiel_total_heures,
                    ROUND(AVG(coefficient_variation_pct)::numeric, 2) as cv_moyen_pct,
                    ROUND(MAX(score_goulot)::numeric, 2) as score_goulot_max
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
            """)
            
            kpis = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            # Distribution by bottleneck level
            cursor.execute("""
                SELECT 
                    niveau_goulot,
                    COUNT(*) as count,
                    ROUND(SUM(pct_temps_total_workflow)::numeric, 2) as pct_temps_total,
                    ROUND(AVG(duree_moyenne_minutes)::numeric, 2) as duree_moyenne_min
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                GROUP BY niveau_goulot
                ORDER BY 
                    CASE niveau_goulot 
                        WHEN 'CRITIQUE' THEN 1 
                        WHEN 'MAJEUR' THEN 2 
                        WHEN 'MODERE' THEN 3 
                        ELSE 4 
                    END
            """)
            
            distribution = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Top 3 bottlenecks
            cursor.execute("""
                SELECT 
                    action,
                    niveau_goulot,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_moyenne_min,
                    ROUND(pct_temps_total_workflow::numeric, 2) as pct_workflow,
                    ROUND(score_goulot::numeric, 2) as score
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                WHERE est_goulot_etranglement = true
                ORDER BY score_goulot DESC NULLS LAST
                LIMIT 3
            """)
            
            top_goulots = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'kpis': kpis,
            'distribution': distribution,
            'top_goulots': top_goulots
        })

    @action(detail=False, methods=['get'])
    def goulots(self, request):
        """
        Get detailed bottleneck analysis
        
        Query params:
        - niveau: Filter by bottleneck level (CRITIQUE, MAJEUR, MODERE, NORMAL)
        - limit: Number of results (default: 20)
        
        Returns:
        - Complete list of steps with bottleneck indicators
        """
        niveau = request.query_params.get('niveau')
        limit = int(request.query_params.get('limit', 20))
        
        with connection.cursor() as cursor:
            where_clause = ""
            if niveau:
                where_clause = f"WHERE niveau_goulot = '{niveau}'"
            
            cursor.execute(f"""
                SELECT 
                    etape_id,
                    action,
                    etape_source,
                    etape_destination,
                    nb_occurrences,
                    nb_dossiers_distincts,
                    nb_agents_impliques,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_moyenne_min,
                    ROUND(duree_moyenne_heures::numeric, 2) as duree_moyenne_h,
                    ROUND(mediane_minutes::numeric, 2) as mediane_min,
                    ROUND(min_minutes::numeric, 2) as min_min,
                    ROUND(max_minutes::numeric, 2) as max_min,
                    ROUND(p90_minutes::numeric, 2) as p90_min,
                    ROUND(temps_total_heures::numeric, 2) as temps_total_h,
                    ROUND(ratio_vs_moyenne_globale::numeric, 2) as ratio_moyenne,
                    ROUND(pct_temps_total_workflow::numeric, 2) as pct_workflow,
                    ROUND(coefficient_variation_pct::numeric, 2) as cv_pct,
                    ROUND(score_goulot::numeric, 2) as score,
                    niveau_goulot,
                    est_goulot_etranglement as est_goulot,
                    ROUND(gain_potentiel_heures::numeric, 2) as gain_potentiel_h,
                    recommandation,
                    rang_duree_moyenne,
                    rang_temps_total,
                    rang_variabilite
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                {where_clause}
                ORDER BY score_goulot DESC NULLS LAST
                LIMIT {limit}
            """)
            
            columns = [col[0] for col in cursor.description]
            goulots = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response({
            'goulots': goulots,
            'total': len(goulots)
        })

    @action(detail=False, methods=['get'])
    def etapes_chart(self, request):
        """
        Get data formatted for charts
        
        Returns:
        - Data for bar chart (duration by step)
        - Data for pie chart (workflow distribution)
        - Data for scatter (variability vs duration)
        """
        with connection.cursor() as cursor:
            # Bar chart - Duration by step
            cursor.execute("""
                SELECT 
                    action as name,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_min,
                    ROUND(mediane_minutes::numeric, 2) as mediane_min,
                    niveau_goulot,
                    ROUND(score_goulot::numeric, 2) as score
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                ORDER BY duree_moyenne_minutes DESC NULLS LAST
                LIMIT 15
            """)
            bar_chart = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Pie chart - Workflow distribution
            cursor.execute("""
                SELECT 
                    action as name,
                    ROUND(pct_temps_total_workflow::numeric, 2) as value
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                WHERE pct_temps_total_workflow > 1
                ORDER BY pct_temps_total_workflow DESC
            """)
            pie_chart = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Scatter - Variability vs Duration
            cursor.execute("""
                SELECT 
                    action as name,
                    ROUND(duree_moyenne_minutes::numeric, 2) as x,
                    ROUND(coefficient_variation_pct::numeric, 2) as y,
                    niveau_goulot,
                    nb_occurrences as size
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                WHERE coefficient_variation_pct IS NOT NULL
            """)
            scatter_chart = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Funnel - Workflow steps
            cursor.execute("""
                SELECT 
                    action as name,
                    nb_occurrences as value,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_min
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                ORDER BY etape_source NULLS FIRST, nb_occurrences DESC
                LIMIT 12
            """)
            funnel_chart = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'bar_chart': bar_chart,
            'pie_chart': pie_chart,
            'scatter_chart': scatter_chart,
            'funnel_chart': funnel_chart
        })

    @action(detail=False, methods=['get'])
    def recommandations(self, request):
        """
        Get optimization recommendations prioritized by impact
        
        Returns:
        - List of recommendations with potential gains
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    action,
                    niveau_goulot,
                    recommandation,
                    ROUND(gain_potentiel_heures::numeric, 2) as gain_potentiel_h,
                    ROUND(score_goulot::numeric, 2) as score,
                    ROUND(pct_temps_total_workflow::numeric, 2) as pct_workflow,
                    ROUND(coefficient_variation_pct::numeric, 2) as cv_pct,
                    nb_occurrences,
                    nb_agents_impliques
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                WHERE niveau_goulot IN ('CRITIQUE', 'MAJEUR', 'MODERE')
                   OR coefficient_variation_pct > 150
                ORDER BY 
                    CASE niveau_goulot 
                        WHEN 'CRITIQUE' THEN 1 
                        WHEN 'MAJEUR' THEN 2 
                        WHEN 'MODERE' THEN 3 
                        ELSE 4 
                    END,
                    gain_potentiel_heures DESC NULLS LAST
            """)
            
            recommandations = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Calculate total potential gain
            total_gain = sum(r.get('gain_potentiel_h', 0) or 0 for r in recommandations)
        
        return Response({
            'recommandations': recommandations,
            'total_gain_heures': round(total_gain, 2),
            'nb_actions_requises': len(recommandations)
        })

    @action(detail=False, methods=['get'])
    def variabilite(self, request):
        """
        Get variability analysis (process stability)
        
        Returns:
        - Steps with highest variability
        - Process stability indicators
        """
        with connection.cursor() as cursor:
            # High variability steps
            cursor.execute("""
                SELECT 
                    action,
                    ROUND(coefficient_variation_pct::numeric, 2) as cv_pct,
                    ROUND(duree_moyenne_minutes::numeric, 2) as moyenne_min,
                    ROUND(mediane_minutes::numeric, 2) as mediane_min,
                    ROUND(ecart_type_minutes::numeric, 2) as ecart_type_min,
                    ROUND(min_minutes::numeric, 2) as min_min,
                    ROUND(max_minutes::numeric, 2) as max_min,
                    ROUND(p90_minutes::numeric, 2) as p90_min,
                    ROUND(indice_dispersion_p90::numeric, 2) as dispersion_p90,
                    nb_occurrences,
                    CASE 
                        WHEN coefficient_variation_pct > 200 THEN 'INSTABLE'
                        WHEN coefficient_variation_pct > 100 THEN 'VARIABLE'
                        WHEN coefficient_variation_pct > 50 THEN 'MODEREE'
                        ELSE 'STABLE'
                    END as stabilite
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                WHERE coefficient_variation_pct IS NOT NULL
                ORDER BY coefficient_variation_pct DESC NULLS LAST
            """)
            
            variabilite = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Stability summary
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN coefficient_variation_pct > 200 THEN 'INSTABLE'
                        WHEN coefficient_variation_pct > 100 THEN 'VARIABLE'
                        WHEN coefficient_variation_pct > 50 THEN 'MODEREE'
                        ELSE 'STABLE'
                    END as stabilite,
                    COUNT(*) as count
                FROM dwh_marts_rh.mart_temps_traitement_dossiers
                WHERE coefficient_variation_pct IS NOT NULL
                GROUP BY 
                    CASE 
                        WHEN coefficient_variation_pct > 200 THEN 'INSTABLE'
                        WHEN coefficient_variation_pct > 100 THEN 'VARIABLE'
                        WHEN coefficient_variation_pct > 50 THEN 'MODEREE'
                        ELSE 'STABLE'
                    END
                ORDER BY 
                    CASE 
                        WHEN coefficient_variation_pct > 200 THEN 1
                        WHEN coefficient_variation_pct > 100 THEN 2
                        WHEN coefficient_variation_pct > 50 THEN 3
                        ELSE 4
                    END
            """)
            
            stabilite_summary = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'variabilite': variabilite,
            'stabilite_summary': stabilite_summary
        })

    # =====================================================
    # PERFORMANCE AGENTS ENDPOINTS
    # =====================================================

    @action(detail=False, methods=['get'])
    def performance_agents_summary(self, request):
        """
        Get summary overview of agent performance
        
        Returns:
        - Global KPIs for agent performance
        - Distribution by performance classification
        - Top performers
        """
        with connection.cursor() as cursor:
            # Global KPIs
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT agent_id) as nb_agents,
                    COUNT(DISTINCT etape_key) as nb_etapes_analysees,
                    SUM(nb_actions) as total_traitements,
                    ROUND(AVG(duree_moyenne_minutes)::numeric, 2) as duree_moyenne_globale_min,
                    ROUND(AVG(score_rapidite)::numeric, 2) as score_rapidite_moyen,
                    SUM(CASE WHEN niveau_performance = 'EXCELLENT' THEN 1 ELSE 0 END) as nb_excellent,
                    SUM(CASE WHEN niveau_performance = 'BON' THEN 1 ELSE 0 END) as nb_bon,
                    SUM(CASE WHEN niveau_performance = 'STANDARD' THEN 1 ELSE 0 END) as nb_standard,
                    SUM(CASE WHEN niveau_performance = 'A_AMELIORER' THEN 1 ELSE 0 END) as nb_ameliorer,
                    SUM(CASE WHEN niveau_performance = 'CRITIQUE' THEN 1 ELSE 0 END) as nb_critique
                FROM dwh_marts_rh.mart_performance_agents
            """)
            kpis = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            # Distribution by classification
            cursor.execute("""
                SELECT 
                    niveau_performance as classification_performance,
                    COUNT(*) as count,
                    ROUND(AVG(score_global_performance)::numeric, 2) as score_moyen,
                    ROUND(AVG(duree_moyenne_minutes)::numeric, 2) as duree_moyenne_min
                FROM dwh_marts_rh.mart_performance_agents
                GROUP BY niveau_performance
                ORDER BY 
                    CASE niveau_performance 
                        WHEN 'EXCELLENT' THEN 1 
                        WHEN 'BON' THEN 2 
                        WHEN 'STANDARD' THEN 3 
                        WHEN 'A_AMELIORER' THEN 4 
                        WHEN 'CRITIQUE' THEN 5 
                    END
            """)
            distribution = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Top 5 performers (by global score)
            cursor.execute("""
                SELECT 
                    agent_id,
                    agent_nom_complet as nom_agent,
                    action_libelle as etape,
                    ROUND(score_global_performance::numeric, 2) as score,
                    niveau_performance as classification_performance,
                    nb_actions as nb_traitements,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_moyenne_min,
                    ROUND(score_rapidite::numeric, 2) as score_rapidite
                FROM dwh_marts_rh.mart_performance_agents
                ORDER BY score_global_performance DESC NULLS LAST
                LIMIT 5
            """)
            top_performers = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Agents needing improvement
            cursor.execute("""
                SELECT 
                    agent_id,
                    agent_nom_complet as nom_agent,
                    action_libelle as etape,
                    ROUND(score_global_performance::numeric, 2) as score,
                    niveau_performance as classification_performance,
                    nb_actions as nb_traitements,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_moyenne_min,
                    ROUND(ecart_benchmark_minutes::numeric, 2) as ecart_moyenne_min
                FROM dwh_marts_rh.mart_performance_agents
                WHERE niveau_performance IN ('A_AMELIORER', 'CRITIQUE')
                ORDER BY score_global_performance ASC NULLS LAST
                LIMIT 5
            """)
            need_improvement = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'kpis': kpis,
            'distribution': distribution,
            'top_performers': top_performers,
            'need_improvement': need_improvement
        })

    @action(detail=False, methods=['get'])
    def performance_agents(self, request):
        """
        Get detailed agent performance data
        
        Query params:
        - agent_id: Filter by agent
        - etape: Filter by step
        - classification: Filter by performance classification
        - limit: Number of results (default: 50)
        
        Returns:
        - Complete performance data per agent per step
        """
        agent_id = request.query_params.get('agent_id')
        etape = request.query_params.get('etape')
        classification = request.query_params.get('classification')
        limit = int(request.query_params.get('limit', 50))
        
        with connection.cursor() as cursor:
            where_clauses = []
            if agent_id:
                where_clauses.append(f"agent_id = {agent_id}")
            if etape:
                where_clauses.append(f"action_libelle ILIKE '%{etape}%'")
            if classification:
                where_clauses.append(f"classification_performance = '{classification}'")
            
            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            cursor.execute(f"""
                SELECT 
                    agent_id,
                    agent_nom_complet as nom_agent,
                    etape_key,
                    action_libelle,
                    categorie_etape,
                    nb_actions as nb_traitements,
                    nb_dossiers_traites as nb_dossiers_distincts,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_moyenne_min,
                    ROUND(mediane_minutes::numeric, 2) as duree_mediane_min,
                    ROUND(min_minutes::numeric, 2) as duree_min_min,
                    ROUND(max_minutes::numeric, 2) as duree_max_min,
                    ROUND(p90_minutes::numeric, 2) as duree_p90_min,
                    ROUND(ecart_type_minutes::numeric, 2) as ecart_type_min,
                    ROUND(coefficient_variation_pct::numeric, 2) as cv_pct,
                    ROUND(score_rapidite::numeric, 2) as score_rapidite,
                    ROUND(benchmark_moyenne_minutes::numeric, 2) as moyenne_etape_min,
                    ROUND(ecart_benchmark_minutes::numeric, 2) as ecart_moyenne_min,
                    ROUND(ratio_vs_benchmark::numeric, 2) as ratio_benchmark,
                    (rang_rapidite = 1) as est_meilleur_etape,
                    (rang_rapidite = nb_agents_action) as est_moins_bon_etape,
                    ROUND(score_rapidite::numeric, 2) as score_rapidite_2,
                    ROUND((100 - coefficient_variation_pct)::numeric, 2) as score_regularite,
                    ROUND(pct_charge_action::numeric, 2) as score_volume,
                    ROUND(score_global_performance::numeric, 2) as score_global,
                    niveau_performance as classification_performance,
                    rang_rapidite as rang_agent_etape,
                    nb_agents_action as nb_agents_etape,
                    ROUND(pct_charge_action::numeric, 2) as pct_traitements_etape
                FROM dwh_marts_rh.mart_performance_agents
                {where_sql}
                ORDER BY score_global_performance DESC NULLS LAST
                LIMIT {limit}
            """)
            
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response({
            'performance': data,
            'total': len(data)
        })

    @action(detail=False, methods=['get'])
    def performance_agents_comparison(self, request):
        """
        Compare agents on the same step
        
        Query params:
        - etape_key: The step to compare (required)
        
        Returns:
        - All agents performance on selected step
        - Best/worst performer
        - Average for comparison
        """
        etape_key = request.query_params.get('etape_key')
        
        with connection.cursor() as cursor:
            where_clause = f"WHERE etape_key = {etape_key}" if etape_key else ""
            
            # Get all agents on this step
            cursor.execute(f"""
                SELECT 
                    agent_id,
                    agent_nom_complet as nom_agent,
                    action_libelle,
                    nb_actions as nb_traitements,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_moyenne_min,
                    ROUND(mediane_minutes::numeric, 2) as duree_mediane_min,
                    ROUND(score_rapidite::numeric, 2) as score_rapidite,
                    ROUND(score_global_performance::numeric, 2) as score_global,
                    niveau_performance as classification_performance,
                    rang_rapidite as rang_agent_etape,
                    (rang_rapidite = 1) as est_meilleur_etape,
                    (rang_rapidite = nb_agents_action) as est_moins_bon_etape,
                    ROUND(ecart_benchmark_minutes::numeric, 2) as ecart_moyenne_min
                FROM dwh_marts_rh.mart_performance_agents
                {where_clause}
                ORDER BY score_global_performance DESC NULLS LAST
            """)
            
            agents = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Get step info and averages
            cursor.execute(f"""
                SELECT 
                    action_libelle as etape,
                    COUNT(DISTINCT agent_id) as nb_agents,
                    ROUND(AVG(duree_moyenne_minutes)::numeric, 2) as duree_moyenne_globale,
                    ROUND(MIN(duree_moyenne_minutes)::numeric, 2) as meilleur_temps,
                    ROUND(MAX(duree_moyenne_minutes)::numeric, 2) as pire_temps,
                    ROUND(AVG(score_global_performance)::numeric, 2) as score_moyen
                FROM dwh_marts_rh.mart_performance_agents
                {where_clause}
                GROUP BY action_libelle
            """)
            
            step_info = None
            row = cursor.fetchone()
            if row:
                step_info = dict(zip([col[0] for col in cursor.description], row))
        
        return Response({
            'agents': agents,
            'step_info': step_info
        })

    @action(detail=False, methods=['get'])
    def performance_agents_by_step(self, request):
        """
        Get aggregated performance data grouped by step
        
        Returns:
        - Performance summary for each step
        - Best performer per step
        - Charts data
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    etape_key,
                    action_libelle,
                    categorie_etape,
                    COUNT(DISTINCT agent_id) as nb_agents,
                    SUM(nb_actions) as total_traitements,
                    ROUND(AVG(duree_moyenne_minutes)::numeric, 2) as duree_moyenne_globale,
                    ROUND(MIN(duree_moyenne_minutes)::numeric, 2) as meilleur_temps,
                    ROUND(MAX(duree_moyenne_minutes)::numeric, 2) as pire_temps,
                    ROUND(AVG(score_global_performance)::numeric, 2) as score_moyen,
                    ROUND(STDDEV(duree_moyenne_minutes)::numeric, 2) as ecart_entre_agents
                FROM dwh_marts_rh.mart_performance_agents
                GROUP BY etape_key, action_libelle, categorie_etape
                ORDER BY total_traitements DESC
            """)
            
            steps = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Get best performer for each step
            cursor.execute("""
                SELECT DISTINCT ON (etape_key)
                    etape_key,
                    action_libelle,
                    agent_id,
                    agent_nom_complet as nom_agent,
                    ROUND(duree_moyenne_minutes::numeric, 2) as duree_min,
                    ROUND(score_global_performance::numeric, 2) as score
                FROM dwh_marts_rh.mart_performance_agents
                WHERE rang_rapidite = 1
                ORDER BY etape_key, score_global_performance DESC
            """)
            
            best_per_step = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'steps': steps,
            'best_per_step': best_per_step
        })

    @action(detail=False, methods=['get'])
    def performance_agents_chart(self, request):
        """
        Get chart-ready data for agent performance visualization
        
        Returns:
        - Radar chart data (scores by dimension)
        - Bar chart (agents comparison)
        - Heatmap data (agent x step)
        """
        with connection.cursor() as cursor:
            # Bar chart - Score by agent
            cursor.execute("""
                SELECT 
                    agent_nom_complet as nom_agent,
                    ROUND(AVG(score_rapidite)::numeric, 2) as rapidite,
                    ROUND(AVG(100 - coefficient_variation_pct)::numeric, 2) as regularite,
                    ROUND(AVG(pct_charge_action)::numeric, 2) as volume,
                    ROUND(AVG(score_global_performance)::numeric, 2) as global,
                    COUNT(*) as nb_etapes
                FROM dwh_marts_rh.mart_performance_agents
                GROUP BY agent_id, agent_nom_complet
                ORDER BY AVG(score_global_performance) DESC
            """)
            bar_chart = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Heatmap - Agent x Step performance
            cursor.execute("""
                SELECT 
                    agent_nom_complet as nom_agent,
                    action_libelle as etape,
                    ROUND(score_global_performance::numeric, 2) as score,
                    niveau_performance as classification_performance
                FROM dwh_marts_rh.mart_performance_agents
                ORDER BY agent_nom_complet, action_libelle
            """)
            heatmap = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
            
            # Classification distribution per agent
            cursor.execute("""
                SELECT 
                    agent_nom_complet as nom_agent,
                    niveau_performance as classification_performance,
                    COUNT(*) as count
                FROM dwh_marts_rh.mart_performance_agents
                GROUP BY agent_nom_complet, niveau_performance
                ORDER BY agent_nom_complet, 
                    CASE niveau_performance 
                        WHEN 'EXCELLENT' THEN 1 
                        WHEN 'BON' THEN 2 
                        WHEN 'STANDARD' THEN 3 
                        WHEN 'A_AMELIORER' THEN 4 
                        WHEN 'CRITIQUE' THEN 5 
                    END
            """)
            distribution_per_agent = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'bar_chart': bar_chart,
            'heatmap': heatmap,
            'distribution_per_agent': distribution_per_agent
        })

    @action(detail=False, methods=['get'])
    def analyse_dossier(self, request):
        """
        Analyse détaillée du parcours d'un dossier spécifique
        Identifie les points de retard par rapport aux benchmarks
        
        Query params:
        - dossier_id: ID du dossier à analyser (required)
        
        Returns:
        - info_dossier: Informations générales du dossier
        - parcours: Liste des étapes avec temps réel vs benchmark
        - points_retard: Étapes où le dossier a été retardé
        - resume: Synthèse des retards
        """
        dossier_ref = request.query_params.get('dossier_ref')
        dossier_id = request.query_params.get('dossier_id')  # Fallback pour compatibilité
        
        if not dossier_ref and not dossier_id:
            return Response({'error': 'dossier_ref ou dossier_id est requis'}, status=400)
        
        with connection.cursor() as cursor:
            # If we have a reference, get the dossier_id first
            if dossier_ref:
                cursor.execute("""
                    SELECT d.dossier_id 
                    FROM dwh_dimensions.dim_dossiers d 
                    WHERE d.dossier_reference = %s
                    LIMIT 1
                """, [dossier_ref])
                result = cursor.fetchone()
                if result:
                    dossier_id = result[0]
                else:
                    return Response({'error': f'Dossier avec référence {dossier_ref} non trouvé'}, status=404)
            
            # Get dossier journey with real times
            cursor.execute("""
                WITH parcours_dossier AS (
                    SELECT 
                        f.dossier_id,
                        f.action,
                        e.action_libelle,
                        e.categorie_etape,
                        f.agent_id,
                        a.nom_complet as nom_agent,
                        f.date_action,
                        f.date_action_suivante,
                        ROUND(f.duree_minutes::numeric, 2) as duree_reelle_min,
                        f.etape_source,
                        f.etape_destination,
                        ROW_NUMBER() OVER (PARTITION BY f.dossier_id ORDER BY f.date_action) as ordre_etape
                    FROM dwh_facts.fait_traitements f
                    LEFT JOIN dwh_dimensions.dim_etapes e ON f.etape_key = e.etape_key
                    LEFT JOIN dwh_dimensions.dim_agents a ON f.agent_key = a.agent_key
                    WHERE f.dossier_id = %s
                    ORDER BY f.date_action
                ),
                benchmarks AS (
                    SELECT 
                        action,
                        ROUND(duree_moyenne_minutes::numeric, 2) as benchmark_min,
                        ROUND(mediane_minutes::numeric, 2) as benchmark_mediane_min,
                        ROUND(p90_minutes::numeric, 2) as benchmark_p90_min,
                        niveau_goulot
                    FROM dwh_marts_rh.mart_temps_traitement_dossiers
                )
                SELECT 
                    p.*,
                    b.benchmark_min,
                    b.benchmark_mediane_min,
                    b.benchmark_p90_min,
                    b.niveau_goulot,
                    ROUND((p.duree_reelle_min - COALESCE(b.benchmark_min, 0))::numeric, 2) as ecart_min,
                    CASE 
                        WHEN b.benchmark_min > 0 THEN ROUND(((p.duree_reelle_min - b.benchmark_min) / b.benchmark_min * 100)::numeric, 2)
                        ELSE 0 
                    END as ecart_pct,
                    CASE 
                        WHEN b.benchmark_min > 0 AND p.duree_reelle_min > b.benchmark_min * 1.5 THEN 'RETARD_CRITIQUE'
                        WHEN b.benchmark_min > 0 AND p.duree_reelle_min > b.benchmark_min * 1.2 THEN 'RETARD_MODERE'
                        WHEN b.benchmark_min > 0 AND p.duree_reelle_min > b.benchmark_min THEN 'RETARD_LEGER'
                        WHEN b.benchmark_min > 0 AND p.duree_reelle_min < b.benchmark_min * 0.8 THEN 'RAPIDE'
                        ELSE 'NORMAL'
                    END as statut_temps
                FROM parcours_dossier p
                LEFT JOIN benchmarks b ON p.action = b.action
                ORDER BY p.ordre_etape
            """, [dossier_id])
            
            columns = [col[0] for col in cursor.description]
            parcours = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if not parcours:
                return Response({'error': f'Aucun historique trouvé pour le dossier {dossier_ref or dossier_id}'}, status=404)
            
            # Calculate summary
            total_temps_reel = sum(p['duree_reelle_min'] or 0 for p in parcours)
            total_benchmark = sum(p['benchmark_min'] or 0 for p in parcours)
            
            # Identify delay points
            points_retard = [
                {
                    'etape': p['action_libelle'] or p['action'],
                    'ordre': p['ordre_etape'],
                    'duree_reelle_min': p['duree_reelle_min'],
                    'benchmark_min': p['benchmark_min'],
                    'ecart_min': p['ecart_min'],
                    'ecart_pct': p['ecart_pct'],
                    'statut': p['statut_temps'],
                    'agent': p['nom_agent'],
                    'date_debut': p['date_action'].isoformat() if p['date_action'] else None,
                    'niveau_goulot_etape': p['niveau_goulot']
                }
                for p in parcours 
                if p['statut_temps'] in ['RETARD_CRITIQUE', 'RETARD_MODERE', 'RETARD_LEGER']
            ]
            
            # Dossier info
            first_action = parcours[0]['date_action'] if parcours else None
            last_action = parcours[-1]['date_action_suivante'] or parcours[-1]['date_action'] if parcours else None
            
            resume = {
                'dossier_id': int(dossier_id),
                'dossier_reference': dossier_ref,
                'nb_etapes': len(parcours),
                'nb_retards': len(points_retard),
                'nb_retards_critiques': len([p for p in points_retard if p['statut'] == 'RETARD_CRITIQUE']),
                'temps_total_reel_min': round(total_temps_reel, 2),
                'temps_total_reel_heures': round(total_temps_reel / 60, 2),
                'temps_total_benchmark_min': round(total_benchmark, 2),
                'temps_total_benchmark_heures': round(total_benchmark / 60, 2),
                'ecart_total_min': round(total_temps_reel - total_benchmark, 2),
                'ecart_total_pct': round((total_temps_reel - total_benchmark) / total_benchmark * 100, 2) if total_benchmark > 0 else 0,
                'date_debut': first_action.isoformat() if first_action else None,
                'date_fin': last_action.isoformat() if last_action else None,
                'etape_plus_longue': max(parcours, key=lambda x: x['duree_reelle_min'] or 0)['action_libelle'] if parcours else None,
                'principal_point_retard': points_retard[0]['etape'] if points_retard else None
            }
        
        return Response({
            'resume': resume,
            'parcours': parcours,
            'points_retard': sorted(points_retard, key=lambda x: x['ecart_min'] or 0, reverse=True)
        })

    @action(detail=False, methods=['get'])
    def recherche_dossiers(self, request):
        """
        Recherche de dossiers pour l'analyse
        
        Query params:
        - search: Recherche par numéro de dossier
        - limit: Nombre de résultats (default: 20)
        - with_delays: Filtrer uniquement les dossiers avec retards
        
        Returns:
        - Liste des dossiers avec temps total et nombre d'étapes
        """
        search = request.query_params.get('search', '')
        limit = int(request.query_params.get('limit', 20))
        with_delays = request.query_params.get('with_delays', 'false').lower() == 'true'
        
        with connection.cursor() as cursor:
            # Build the search filter
            search_filter = ""
            params = [limit]
            if search:
                search_filter = """
                WHERE (
                    d.dossier_reference ILIKE %s 
                    OR f.dossier_id::text LIKE %s
                )
                """
                params = [f'%{search}%', f'%{search}%', limit]
            
            cursor.execute(f"""
                WITH dossiers_stats AS (
                    SELECT 
                        f.dossier_id,
                        COALESCE(d.dossier_reference, 'Dossier #' || f.dossier_id::text) as dossier_reference,
                        COUNT(*) as nb_etapes,
                        ROUND(SUM(f.duree_minutes)::numeric, 2) as temps_total_min,
                        MIN(f.date_action) as date_debut,
                        MAX(f.date_action) as date_derniere_action
                    FROM dwh_facts.fait_traitements f
                    LEFT JOIN dwh_dimensions.dim_dossiers d ON f.dossier_key = d.dossier_key
                    {search_filter}
                    GROUP BY f.dossier_id, d.dossier_reference
                ),
                benchmarks_total AS (
                    SELECT SUM(duree_moyenne_minutes) as benchmark_total
                    FROM dwh_marts_rh.mart_temps_traitement_dossiers
                )
                SELECT 
                    ds.dossier_id,
                    ds.dossier_reference,
                    ds.nb_etapes,
                    ds.temps_total_min as duree_totale_minutes,
                    ds.date_debut,
                    ds.date_derniere_action,
                    bt.benchmark_total,
                    ROUND((ds.temps_total_min - bt.benchmark_total)::numeric, 2) as ecart_total_min,
                    CASE 
                        WHEN ds.temps_total_min > bt.benchmark_total * 1.5 THEN true
                        WHEN ds.temps_total_min > bt.benchmark_total THEN true
                        ELSE false
                    END as a_des_retards,
                    CASE 
                        WHEN ds.temps_total_min > bt.benchmark_total * 1.5 THEN 'RETARD_IMPORTANT'
                        WHEN ds.temps_total_min > bt.benchmark_total THEN 'RETARD'
                        ELSE 'NORMAL'
                    END as statut_global
                FROM dossiers_stats ds
                CROSS JOIN benchmarks_total bt
                ORDER BY ds.date_derniere_action DESC NULLS LAST
                LIMIT %s
            """, params)
            
            columns = [col[0] for col in cursor.description]
            dossiers = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if with_delays:
                dossiers = [d for d in dossiers if d['a_des_retards']]
        
        return Response({
            'dossiers': dossiers,
            'total': len(dossiers)
        })
