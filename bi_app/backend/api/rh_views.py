"""
API Views for dwh_marts_rh dashboards
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection


class RhViewSet(viewsets.ViewSet):
    """
    ViewSet for RH-related metrics dashboards from dwh_marts_rh.
    
    Available endpoints:
    - agents_productivite: Overview of all agents productivity
    - top_agents: Top performing agents by various metrics
    - performance_by_type: Performance analysis by agent type
    - collectes_analysis: Detailed collectes analysis by agents
    """

    @action(detail=False, methods=['get'])
    def agents_productivite(self, request):
        """
        Get overview of all agents productivity
        
        Returns:
        - List of all agents with productivity metrics
        - Total agents count
        - Average metrics
        """
        with connection.cursor() as cursor:
            # Get all agents productivity data
            cursor.execute("""
                SELECT 
                    agent_id,
                    nom_complet,
                    matricule,
                    email,
                    type_agent_id,
                    nombre_collectes,
                    collectes_cloturees,
                    montant_total_a_recouvrer,
                    montant_total_recouvre,
                    taux_recouvrement_moyen_pct,
                    taux_cloture_pct,
                    delai_moyen_traitement_jours,
                    montant_moyen_par_collecte,
                    rang_productivite_global
                FROM dwh_marts_rh.mart_agents_productivite
                ORDER BY montant_total_recouvre DESC NULLS LAST
            """)
            
            columns = [col[0] for col in cursor.description]
            agents = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Calculate summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_agents,
                    SUM(nombre_collectes) as total_collectes,
                    SUM(montant_total_recouvre) as montant_total_recouvre,
                    ROUND(AVG(taux_recouvrement_moyen_pct), 2) as taux_recouvrement_moyen,
                    ROUND(AVG(taux_cloture_pct), 2) as taux_cloture_moyen,
                    ROUND(AVG(delai_moyen_traitement_jours), 2) as delai_moyen_traitement
                FROM dwh_marts_rh.mart_agents_productivite
            """)
            
            summary = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        
        return Response({
            'agents': agents,
            'summary': summary
        })

    @action(detail=False, methods=['get'])
    def top_agents(self, request):
        """
        Get top performing agents by various metrics
        
        Query params:
        - limit: Number of top agents to return (default: 10)
        - metric: Metric to rank by (montant_recouvre, taux_recouvrement, nombre_collectes)
        
        Returns:
        - Top agents by selected metric
        """
        limit = int(request.query_params.get('limit', 10))
        metric = request.query_params.get('metric', 'montant_recouvre')
        
        # Map metric to column name
        metric_column_map = {
            'montant_recouvre': 'montant_total_recouvre',
            'taux_recouvrement': 'taux_recouvrement_moyen_pct',
            'nombre_collectes': 'nombre_collectes',
            'taux_cloture': 'taux_cloture_pct'
        }
        
        order_column = metric_column_map.get(metric, 'montant_total_recouvre')
        
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    agent_id,
                    nom_complet,
                    matricule,
                    nombre_collectes,
                    montant_total_recouvre,
                    taux_recouvrement_moyen_pct,
                    taux_cloture_pct,
                    delai_moyen_traitement_jours,
                    rang_productivite_global
                FROM dwh_marts_rh.mart_agents_productivite
                WHERE {order_column} IS NOT NULL
                ORDER BY {order_column} DESC
                LIMIT %s
            """, [limit])
            
            columns = [col[0] for col in cursor.description]
            top_agents = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response({
            'metric': metric,
            'limit': limit,
            'top_agents': top_agents
        })

    @action(detail=False, methods=['get'])
    def performance_by_type(self, request):
        """
        Get performance analysis grouped by agent type
        
        Returns:
        - Performance metrics aggregated by agent type
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    type_agent_id,
                    COUNT(*) as nombre_agents,
                    SUM(nombre_collectes) as total_collectes,
                    SUM(montant_total_recouvre) as total_montant_recouvre,
                    ROUND(AVG(taux_recouvrement_moyen_pct), 2) as taux_recouvrement_moyen,
                    ROUND(AVG(taux_cloture_pct), 2) as taux_cloture_moyen,
                    ROUND(AVG(delai_moyen_traitement_jours), 2) as delai_moyen_traitement,
                    ROUND(AVG(montant_moyen_par_collecte), 2) as montant_moyen_par_collecte
                FROM dwh_marts_rh.mart_agents_productivite
                GROUP BY type_agent_id
                ORDER BY total_montant_recouvre DESC NULLS LAST
            """)
            
            columns = [col[0] for col in cursor.description]
            performance_by_type = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response({
            'performance_by_type': performance_by_type
        })

    @action(detail=False, methods=['get'])
    def collectes_analysis(self, request):
        """
        Get detailed analysis of collectes by agents
        
        Returns:
        - Distribution of collectes by status
        - Efficiency metrics
        """
        with connection.cursor() as cursor:
            # Collectes distribution
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_agents,
                    SUM(nombre_collectes) as total_collectes,
                    SUM(collectes_cloturees) as total_cloturees,
                    SUM(nombre_collectes - collectes_cloturees) as total_ouvertes,
                    ROUND(AVG(taux_cloture_pct), 2) as taux_cloture_moyen
                FROM dwh_marts_rh.mart_agents_productivite
            """)
            
            distribution = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            # Recouvrement analysis
            cursor.execute("""
                SELECT 
                    SUM(montant_total_a_recouvrer) as montant_total_a_recouvrer,
                    SUM(montant_total_recouvre) as montant_total_recouvre,
                    ROUND(AVG(taux_recouvrement_moyen_pct), 2) as taux_recouvrement_global
                FROM dwh_marts_rh.mart_agents_productivite
            """)
            
            recouvrement = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            # Performance distribution by collectes ranges
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN nombre_collectes = 0 THEN '0 collecte'
                        WHEN nombre_collectes BETWEEN 1 AND 5 THEN '1-5 collectes'
                        WHEN nombre_collectes BETWEEN 6 AND 10 THEN '6-10 collectes'
                        WHEN nombre_collectes BETWEEN 11 AND 20 THEN '11-20 collectes'
                        ELSE '21+ collectes'
                    END as range_collectes,
                    COUNT(*) as nombre_agents,
                    ROUND(AVG(taux_recouvrement_moyen_pct), 2) as taux_recouvrement_moyen
                FROM dwh_marts_rh.mart_agents_productivite
                GROUP BY 
                    CASE 
                        WHEN nombre_collectes = 0 THEN '0 collecte'
                        WHEN nombre_collectes BETWEEN 1 AND 5 THEN '1-5 collectes'
                        WHEN nombre_collectes BETWEEN 6 AND 10 THEN '6-10 collectes'
                        WHEN nombre_collectes BETWEEN 11 AND 20 THEN '11-20 collectes'
                        ELSE '21+ collectes'
                    END
                ORDER BY MIN(nombre_collectes)
            """)
            
            distribution_ranges = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'distribution': distribution,
            'recouvrement': recouvrement,
            'distribution_by_ranges': distribution_ranges
        })

    @action(detail=False, methods=['get'])
    def agent_details(self, request):
        """
        Get detailed information for a specific agent
        
        Query params:
        - agent_id: ID of the agent (required)
        
        Returns:
        - Detailed agent productivity information
        """
        agent_id = request.query_params.get('agent_id')
        
        if not agent_id:
            return Response({'error': 'agent_id parameter is required'}, status=400)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    agent_id,
                    nom_complet,
                    matricule,
                    email,
                    type_agent_id,
                    annee_actuelle,
                    mois_actuel,
                    nombre_collectes,
                    collectes_cloturees,
                    montant_total_a_recouvrer,
                    montant_total_recouvre,
                    taux_recouvrement_moyen_pct,
                    taux_cloture_pct,
                    delai_moyen_traitement_jours,
                    montant_moyen_par_collecte,
                    rang_productivite_global
                FROM dwh_marts_rh.mart_agents_productivite
                WHERE agent_id = %s
            """, [agent_id])
            
            row = cursor.fetchone()
            
            if not row:
                return Response({'error': f'Agent with ID {agent_id} not found'}, status=404)
            
            columns = [col[0] for col in cursor.description]
            agent_details = dict(zip(columns, row))
        
        return Response(agent_details)

    @action(detail=False, methods=['get'])
    def efficiency_metrics(self, request):
        """
        Get efficiency metrics across all agents
        
        Returns:
        - Average efficiency metrics
        - Distribution of performance levels
        """
        with connection.cursor() as cursor:
            # Global efficiency metrics
            cursor.execute("""
                SELECT 
                    ROUND(AVG(delai_moyen_traitement_jours), 2) as delai_moyen_global,
                    ROUND(AVG(montant_moyen_par_collecte), 2) as montant_moyen_collecte_global,
                    ROUND(AVG(taux_recouvrement_moyen_pct), 2) as taux_recouvrement_global,
                    ROUND(AVG(taux_cloture_pct), 2) as taux_cloture_global
                FROM dwh_marts_rh.mart_agents_productivite
            """)
            
            global_metrics = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            # Performance levels distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN taux_recouvrement_moyen_pct >= 80 THEN 'Excellent (≥80%)'
                        WHEN taux_recouvrement_moyen_pct >= 60 THEN 'Bon (60-79%)'
                        WHEN taux_recouvrement_moyen_pct >= 40 THEN 'Moyen (40-59%)'
                        ELSE 'Faible (<40%)'
                    END as niveau_performance,
                    COUNT(*) as nombre_agents,
                    ROUND(AVG(montant_total_recouvre), 2) as montant_moyen_recouvre
                FROM dwh_marts_rh.mart_agents_productivite
                GROUP BY 
                    CASE 
                        WHEN taux_recouvrement_moyen_pct >= 80 THEN 'Excellent (≥80%)'
                        WHEN taux_recouvrement_moyen_pct >= 60 THEN 'Bon (60-79%)'
                        WHEN taux_recouvrement_moyen_pct >= 40 THEN 'Moyen (40-59%)'
                        ELSE 'Faible (<40%)'
                    END
                ORDER BY MIN(taux_recouvrement_moyen_pct) DESC
            """)
            
            performance_levels = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        
        return Response({
            'global_metrics': global_metrics,
            'performance_levels': performance_levels
        })
