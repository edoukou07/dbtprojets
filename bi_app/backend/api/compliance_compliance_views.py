"""
API Views for dwh_marts_compliance dashboards
Covering: API Performance, Conventions Validation, Approval Delays
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import connection
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ComplianceComplianceViewSet(viewsets.ViewSet):
    """
    ViewSet for compliance-related metrics dashboards from dwh_marts_compliance.
    Covers: API Performance, Conventions Validation, Approval Delays
    """

    def _execute_query(self, query, params=None):
        """Execute SQL query and return results as list of dicts."""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or [])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise

    def _serialize_decimal(self, obj):
        """Convert Decimal to float for JSON serialization."""
        if isinstance(obj, Decimal):
            return float(obj)
        return obj

    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """
        Get overall dashboard summary combining all 3 compliance marts.
        """
        annee = request.query_params.get('annee', datetime.now().year)
        
        queries = {
            'api_performance': """
                SELECT
                    COUNT(*) as total_endpoints,
                    ROUND(AVG(duration_avg_ms_global), 2) as avg_response_time_ms,
                    ROUND(AVG(taux_erreur_pct), 2) as avg_error_rate_pct,
                    SUM(total_requetes) as total_requests,
                    SUM(total_erreurs) as total_errors,
                    SUM(CASE WHEN sla_status = 'OK' THEN 1 ELSE 0 END) as sla_compliant
                FROM dwh_marts_compliance.mart_api_performance
            """,
            'conventions': """
                SELECT
                    COUNT(*) as total_records,
                    ROUND(AVG(taux_validation_pct), 2) as avg_validation_rate_pct,
                    SUM(nombre_conventions) as total_conventions,
                    SUM(conventions_validees) as conventions_approved,
                    SUM(conventions_rejetees) as conventions_rejected,
                    ROUND(AVG(delai_moyen_traitement_jours), 1) as avg_processing_days
                FROM dwh_marts_compliance.mart_conventions_validation
                WHERE EXTRACT(YEAR FROM to_date(annee_mois, 'YYYY-MM')) = %s
            """,
            'approval_delays': """
                SELECT
                    COUNT(*) as total_records,
                    ROUND(AVG(delai_moyen_traitement_jours), 1) as avg_approval_days,
                    ROUND(AVG(delai_median_traitement_jours), 1) as median_approval_days,
                    ROUND(AVG(delai_max_traitement_jours), 1) as max_approval_days,
                    SUM(nombre_conventions) as total_conventions_tracked
                FROM dwh_marts_compliance.mart_delai_approbation
                WHERE EXTRACT(YEAR FROM to_date(annee_mois, 'YYYY-MM')) = %s
            """
        }
        
        result = {}
        try:
            api_perf = self._execute_query(queries['api_performance'])[0]
            conventions = self._execute_query(queries['conventions'], [annee])[0]
            delays = self._execute_query(queries['approval_delays'], [annee])[0]
            
            # Serialize decimals
            for d in [api_perf, conventions, delays]:
                for key, value in d.items():
                    if value is None:
                        d[key] = 0
                    else:
                        d[key] = self._serialize_decimal(value)
            
            result = {
                'api_performance': api_perf,
                'conventions_validation': conventions,
                'approval_delays': delays
            }
        except Exception as e:
            logger.error(f"Dashboard summary error: {str(e)}")
            result = {
                'api_performance': {},
                'conventions_validation': {},
                'approval_delays': {}
            }
        
        return Response(result)

    # ==========================
    # API Performance Endpoints
    # ==========================

    @action(detail=False, methods=['get'])
    def api_performance_summary(self, request):
        """Get API performance KPIs."""
        query = """
            SELECT
                COUNT(*) as total_endpoints,
                ROUND(AVG(duration_avg_ms_global), 2) as avg_response_time_ms,
                ROUND(MIN(duration_avg_ms_global), 2) as min_response_time_ms,
                ROUND(MAX(duration_max_ms_global), 2) as max_response_time_ms,
                ROUND(AVG(taux_erreur_pct), 2) as avg_error_rate_pct,
                ROUND(AVG(duration_p99_ms_global), 2) as p99_response_time_ms,
                SUM(total_requetes) as total_requests,
                SUM(total_erreurs) as total_errors,
                SUM(total_requetes_lentes) as total_slow_requests,
                SUM(CASE WHEN sla_status = 'OK' THEN 1 ELSE 0 END) as sla_compliant_endpoints,
                COUNT(*) - SUM(CASE WHEN sla_status = 'OK' THEN 1 ELSE 0 END) as sla_non_compliant_endpoints
            FROM dwh_marts_compliance.mart_api_performance
        """
        
        results = self._execute_query(query)
        if results:
            result = results[0]
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
            return Response(result)
        return Response({})

    @action(detail=False, methods=['get'])
    def api_performance_by_endpoint(self, request):
        """Get performance metrics by API endpoint."""
        query = """
            SELECT
                request_path,
                request_method,
                status_code,
                total_requetes,
                total_erreurs,
                total_requetes_lentes,
                ROUND(duration_avg_ms_global, 2) as avg_response_time_ms,
                ROUND(duration_p99_ms_global, 2) as p99_response_time_ms,
                ROUND(duration_max_ms_global, 2) as max_response_time_ms,
                ROUND(taux_erreur_pct, 2) as error_rate_pct,
                sla_status
            FROM dwh_marts_compliance.mart_api_performance
            ORDER BY total_requetes DESC
            LIMIT 50
        """
        
        results = self._execute_query(query)
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def api_performance_by_role(self, request):
        """Get performance metrics by user role."""
        query = """
            SELECT
                user_role,
                COUNT(*) as endpoints_count,
                ROUND(AVG(duration_avg_ms_global), 2) as avg_response_time_ms,
                ROUND(AVG(taux_erreur_pct), 2) as avg_error_rate_pct,
                SUM(total_requetes) as total_requests,
                SUM(total_erreurs) as total_errors
            FROM dwh_marts_compliance.mart_api_performance
            GROUP BY user_role
            ORDER BY total_requests DESC
        """
        
        results = self._execute_query(query)
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    # ==========================
    # Conventions Validation Endpoints
    # ==========================

    @action(detail=False, methods=['get'])
    def conventions_summary(self, request):
        """Get conventions validation KPIs."""
        annee = request.query_params.get('annee', datetime.now().year)
        
        query = """
            SELECT
                COUNT(*) as total_records,
                ROUND(AVG(taux_validation_pct), 2) as avg_validation_rate_pct,
                ROUND(AVG(taux_rejet_pct), 2) as avg_rejection_rate_pct,
                SUM(nombre_conventions) as total_conventions,
                SUM(conventions_validees) as conventions_approved,
                SUM(conventions_rejetees) as conventions_rejected,
                SUM(conventions_en_cours) as conventions_in_progress,
                SUM(conventions_archivees) as conventions_archived,
                ROUND(AVG(delai_moyen_traitement_jours), 1) as avg_processing_days,
                ROUND(MAX(delai_max_traitement_jours), 1) as max_processing_days
            FROM dwh_marts_compliance.mart_conventions_validation
            WHERE EXTRACT(YEAR FROM to_date(annee_mois, 'YYYY-MM')) = %s
        """
        
        results = self._execute_query(query, [annee])
        if results:
            result = results[0]
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
            return Response(result)
        return Response({})

    @action(detail=False, methods=['get'])
    def conventions_trends(self, request):
        """Get monthly conventions trends."""
        query = """
            SELECT
                annee_mois,
                nombre_conventions,
                conventions_validees,
                conventions_rejetees,
                conventions_en_cours,
                ROUND(taux_validation_pct, 2) as validation_rate_pct,
                ROUND(taux_rejet_pct, 2) as rejection_rate_pct,
                ROUND(delai_moyen_traitement_jours, 1) as avg_processing_days
            FROM dwh_marts_compliance.mart_conventions_validation
            ORDER BY annee_mois DESC
            LIMIT 24
        """
        
        results = self._execute_query(query)
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def conventions_by_status(self, request):
        """Get conventions breakdown by status."""
        query = """
            SELECT
                statut,
                COUNT(*) as records_count,
                SUM(nombre_conventions) as total_conventions,
                ROUND(AVG(taux_validation_pct), 2) as avg_validation_pct,
                ROUND(AVG(delai_moyen_traitement_jours), 1) as avg_processing_days
            FROM dwh_marts_compliance.mart_conventions_validation
            GROUP BY statut
            ORDER BY total_conventions DESC
        """
        
        results = self._execute_query(query)
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    # ==========================
    # Approval Delays Endpoints
    # ==========================

    @action(detail=False, methods=['get'])
    def approval_delays_summary(self, request):
        """Get approval delays KPIs."""
        annee = request.query_params.get('annee', datetime.now().year)
        
        query = """
            SELECT
                COUNT(*) as total_records,
                ROUND(AVG(delai_moyen_traitement_jours), 1) as avg_approval_days,
                ROUND(AVG(delai_median_traitement_jours), 1) as median_approval_days,
                ROUND(AVG(delai_min_traitement_jours), 1) as min_approval_days,
                ROUND(AVG(delai_max_traitement_jours), 1) as max_approval_days,
                ROUND(AVG(delai_p95_traitement_jours), 1) as p95_approval_days,
                SUM(nombre_conventions) as total_conventions_tracked,
                SUM(conventions_validees) as conventions_approved,
                SUM(conventions_rejetees) as conventions_rejected,
                SUM(conventions_en_cours) as conventions_in_progress
            FROM dwh_marts_compliance.mart_delai_approbation
            WHERE EXTRACT(YEAR FROM to_date(annee_mois, 'YYYY-MM')) = %s
        """
        
        results = self._execute_query(query, [annee])
        if results:
            result = results[0]
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
            return Response(result)
        return Response({})

    @action(detail=False, methods=['get'])
    def approval_delays_trends(self, request):
        """Get monthly approval delays trends."""
        query = """
            SELECT
                annee_mois,
                nombre_conventions,
                ROUND(delai_moyen_traitement_jours, 1) as avg_approval_days,
                ROUND(delai_median_traitement_jours, 1) as median_approval_days,
                ROUND(delai_p95_traitement_jours, 1) as p95_approval_days,
                ROUND(delai_max_traitement_jours, 1) as max_approval_days,
                conventions_validees,
                conventions_rejetees,
                conventions_en_cours
            FROM dwh_marts_compliance.mart_delai_approbation
            ORDER BY annee_mois DESC
            LIMIT 24
        """
        
        results = self._execute_query(query)
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def approval_delays_by_status(self, request):
        """Get approval delays breakdown by status."""
        query = """
            SELECT
                statut,
                etape_actuelle,
                COUNT(*) as records_count,
                SUM(nombre_conventions) as total_conventions,
                ROUND(AVG(delai_moyen_traitement_jours), 1) as avg_approval_days,
                ROUND(AVG(delai_median_traitement_jours), 1) as median_approval_days,
                ROUND(AVG(delai_p95_traitement_jours), 1) as p95_approval_days
            FROM dwh_marts_compliance.mart_delai_approbation
            GROUP BY statut, etape_actuelle
            ORDER BY total_conventions DESC
        """
        
        results = self._execute_query(query)
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def approval_delays_by_etape(self, request):
        """Get approval delays by current step."""
        query = """
            SELECT
                etape_actuelle,
                COUNT(*) as records_count,
                SUM(nombre_conventions) as total_conventions,
                ROUND(AVG(delai_moyen_traitement_jours), 1) as avg_approval_days,
                ROUND(AVG(delai_median_traitement_jours), 1) as median_approval_days,
                ROUND(MIN(delai_min_traitement_jours), 1) as min_approval_days,
                ROUND(MAX(delai_max_traitement_jours), 1) as max_approval_days
            FROM dwh_marts_compliance.mart_delai_approbation
            GROUP BY etape_actuelle
            ORDER BY total_conventions DESC
        """
        
        results = self._execute_query(query)
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)
