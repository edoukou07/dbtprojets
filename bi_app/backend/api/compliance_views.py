import logging
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import connection
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_date

logger = logging.getLogger(__name__)


class ComplianceViewSet(viewsets.ViewSet):
    """
    ViewSet pour les données de conformité et infractions.
    """

    def _execute_query(self, query, params=None):
        """Exécute une requête SQL et retourne les résultats."""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or [])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Erreur exécution requête: {str(e)}")
            raise

    def _serialize_decimal(self, obj):
        """Convertit Decimal en float pour JSON."""
        if isinstance(obj, Decimal):
            return float(obj)
        return obj

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retourne le résumé des infractions pour une année donnée.
        """
        annee = request.query_params.get('annee', datetime.now().year)
        
        query = """
        SELECT
            SUM(nombre_infractions) as nombre_total_infractions,
            SUM(infractions_resolues) as infractions_resolues,
            SUM(infractions_non_resolues) as infractions_non_resolues,
            ROUND(AVG(taux_resolution_pct), 2) as taux_resolution_moyen_pct,
            ROUND(AVG(delai_moyen_resolution_jours), 1) as delai_moyen_resolution,
            MAX(delai_max_resolution_jours) as delai_max_resolution,
            COUNT(DISTINCT zone_id) as nombre_zones_affectees,
            SUM(infractions_critiques) as nombre_infractions_critiques,
            SUM(infractions_majeures) as nombre_infractions_majeures,
            ROUND(AVG(severite_moyenne), 2) as severite_moyenne,
            ROUND(AVG(taux_resolution_pct), 2) as variation_infractions_pct,
            ROUND(AVG(taux_resolution_pct), 2) as variation_resolution_pct,
            0 as variation_delai_pct
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        """
        
        results = self._execute_query(query, [annee])
        
        if results:
            result = results[0]
            # Nettoyer les None et convertir les décimales
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
            return Response(result)
        
        return Response({})

    @action(detail=False, methods=['get'])
    def tendances_annuelles(self, request):
        """
        Retourne les tendances mensuelles des infractions.
        """
        query = """
        SELECT
            mois_debut,
            nombre_infractions,
            infractions_resolues,
            infractions_non_resolues,
            taux_resolution_pct,
            delai_moyen_resolution_jours
        FROM dwh_marts_operationnel.mart_conformite_infractions
        ORDER BY mois_debut DESC
        LIMIT 24
        """
        
        results = self._execute_query(query)
        
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(list(reversed(results)))

    @action(detail=False, methods=['get'])
    def infractions_par_zone(self, request):
        """
        Retourne les infractions par zone pour une année donnée.
        """
        annee = request.query_params.get('annee', datetime.now().year)
        
        query = """
        SELECT
            zone_id,
            zone_name,
            nombre_infractions as total,
            infractions_mineures,
            infractions_moderees,
            infractions_majeures,
            infractions_critiques,
            taux_resolution_pct,
            ROUND(delai_moyen_resolution_jours, 1) as delai_moyen
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        ORDER BY nombre_infractions DESC
        """
        
        results = self._execute_query(query, [annee])
        
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def distribution_gravite(self, request):
        """
        Retourne la distribution des infractions par gravité.
        """
        annee = request.query_params.get('annee', datetime.now().year)
        
        query = """
        SELECT
            'mineure' as gravite,
            SUM(infractions_mineures) as nombre,
            ROUND(SUM(infractions_mineures)::numeric / NULLIF(SUM(nombre_infractions), 0) * 100, 2) as pourcentage
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        
        UNION ALL
        
        SELECT
            'moderee' as gravite,
            SUM(infractions_moderees) as nombre,
            ROUND(SUM(infractions_moderees)::numeric / NULLIF(SUM(nombre_infractions), 0) * 100, 2) as pourcentage
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        
        UNION ALL
        
        SELECT
            'majeure' as gravite,
            SUM(infractions_majeures) as nombre,
            ROUND(SUM(infractions_majeures)::numeric / NULLIF(SUM(nombre_infractions), 0) * 100, 2) as pourcentage
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        
        UNION ALL
        
        SELECT
            'critique' as gravite,
            SUM(infractions_critiques) as nombre,
            ROUND(SUM(infractions_critiques)::numeric / NULLIF(SUM(nombre_infractions), 0) * 100, 2) as pourcentage
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        """
        
        results = self._execute_query(query, [annee, annee, annee, annee])
        
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def resolution_stats(self, request):
        """
        Retourne les statistiques de résolution par zone.
        """
        annee = request.query_params.get('annee', datetime.now().year)
        
        query = """
        SELECT
            zone_id,
            zone_name,
            nombre_infractions,
            taux_resolution_pct,
            infractions_resolues,
            delai_moyen_resolution_jours as delai_moyen,
            delai_max_resolution_jours as delai_max,
            severite_moyenne
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        ORDER BY nombre_infractions DESC
        LIMIT 50
        """
        
        results = self._execute_query(query, [annee])
        
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                else:
                    result[key] = self._serialize_decimal(value)
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def infractions_detail(self, request):
        """
        Retourne le détail des infractions avec filtres.
        """
        annee = request.query_params.get('annee', datetime.now().year)
        zone_id = request.query_params.get('zone_id')
        statut = request.query_params.get('statut', 'all')  # 'all', 'resolved', 'unresolved'
        
        query = """
        SELECT
            zone_id,
            zone_name,
            nombre_infractions,
            taux_resolution_pct,
            infractions_resolues,
            infractions_non_resolues,
            delai_moyen_resolution_jours,
            severite_moyenne,
            mois_debut
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE EXTRACT(YEAR FROM mois_debut) = %s
        """
        params = [annee]
        
        if zone_id:
            query += " AND zone_id = %s"
            params.append(zone_id)
        
        query += " ORDER BY mois_debut DESC LIMIT 1000"
        
        results = self._execute_query(query, params)
        
        for result in results:
            for key, value in result.items():
                if value is None:
                    result[key] = 0
                elif isinstance(value, Decimal):
                    result[key] = float(value)
                elif isinstance(value, datetime):
                    result[key] = value.isoformat()
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def zones(self, request):
        """
        Retourne la liste des zones disponibles.
        """
        query = """
        SELECT DISTINCT
            zone_id,
            zone_name
        FROM dwh_marts_operationnel.mart_conformite_infractions
        WHERE zone_id IS NOT NULL AND zone_name IS NOT NULL
        ORDER BY zone_name
        """
        
        results = self._execute_query(query)
        return Response(results)

    @action(detail=False, methods=['get'])
    def export_rapport(self, request):
        """
        Export complet du rapport de conformité.
        """
        annee = request.query_params.get('annee', datetime.now().year)
        
        # Récupérer tous les résumés
        summary_results = self.summary(request).data
        zone_results = self._execute_query(
            """SELECT zone_id, zone_name, nombre_infractions, taux_resolution_pct
               FROM dwh_marts_operationnel.mart_conformite_infractions
               WHERE EXTRACT(YEAR FROM mois_debut) = %s
               ORDER BY nombre_infractions DESC""",
            [annee]
        )
        
        rapport = {
            'rapport_date': datetime.now().isoformat(),
            'annee': annee,
            'resume': summary_results,
            'par_zone': zone_results
        }
        
        for item in rapport['par_zone']:
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)
        
        return Response(rapport)
