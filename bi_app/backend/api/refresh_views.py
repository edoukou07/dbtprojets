"""
API pour rafraîchir les vues matérialisées et tables dbt
"""
import subprocess
import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

# Liste des vues matérialisées à rafraîchir
MATERIALIZED_VIEWS = [
    'mart_occupation_zones',
    'mart_performance_financiere',
    'mart_portefeuille_clients',
    'mart_kpi_operationnels'
]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_all_views(request):
    """
    Rafraîchit toutes les vues matérialisées en exécutant dbt run
    """
    try:
        start_time = timezone.now()
        
        # Chemin vers le projet dbt (2 niveaux au-dessus de backend)
        dbt_project_path = os.path.abspath(os.path.join(
            settings.BASE_DIR, '..', '..'
        ))
        
        logger.info(f"Rafraîchissement des vues depuis: {dbt_project_path}")
        
        # Exécuter dbt run pour rafraîchir les marts
        result = subprocess.run(
            ['dbt', 'run', '--select', 'marts.*'],
            cwd=dbt_project_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        if result.returncode == 0:
            logger.info(f"Rafraîchissement réussi en {duration}s")
            return Response({
                'success': True,
                'message': 'Vues rafraîchies avec succès',
                'duration_seconds': duration,
                'views_refreshed': MATERIALIZED_VIEWS,
                'output': result.stdout,
                'timestamp': end_time.isoformat()
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"Erreur dbt: {result.stderr}")
            return Response({
                'success': False,
                'message': 'Erreur lors du rafraîchissement',
                'error': result.stderr,
                'output': result.stdout,
                'timestamp': end_time.isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout lors du rafraîchissement")
        return Response({
            'success': False,
            'message': 'Timeout: le rafraîchissement a pris trop de temps'
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_specific_view(request, view_name):
    """
    Rafraîchit une vue matérialisée spécifique
    """
    try:
        if view_name not in MATERIALIZED_VIEWS:
            return Response({
                'success': False,
                'message': f'Vue inconnue: {view_name}',
                'available_views': MATERIALIZED_VIEWS
            }, status=status.HTTP_400_BAD_REQUEST)
        
        start_time = timezone.now()
        
        dbt_project_path = os.path.abspath(os.path.join(
            settings.BASE_DIR, '..', '..'
        ))
        
        logger.info(f"Rafraîchissement de {view_name}")
        
        # Exécuter dbt run pour une vue spécifique
        result = subprocess.run(
            ['dbt', 'run', '--select', view_name],
            cwd=dbt_project_path,
            capture_output=True,
            text=True,
            timeout=180  # 3 minutes max pour une vue
        )
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        if result.returncode == 0:
            logger.info(f"Vue {view_name} rafraîchie en {duration}s")
            return Response({
                'success': True,
                'message': f'Vue {view_name} rafraîchie avec succès',
                'duration_seconds': duration,
                'view_name': view_name,
                'output': result.stdout,
                'timestamp': end_time.isoformat()
            }, status=status.HTTP_200_OK)
        else:
            logger.error(f"Erreur dbt pour {view_name}: {result.stderr}")
            return Response({
                'success': False,
                'message': f'Erreur lors du rafraîchissement de {view_name}',
                'error': result.stderr,
                'output': result.stdout
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except subprocess.TimeoutExpired:
        return Response({
            'success': False,
            'message': f'Timeout: le rafraîchissement de {view_name} a pris trop de temps'
        }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement de {view_name}: {str(e)}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_refresh_status(request):
    """
    Retourne le statut des vues matérialisées
    """
    try:
        from django.db import connection
        
        views_status = []
        
        with connection.cursor() as cursor:
            for view_name in MATERIALIZED_VIEWS:
                # Vérifier si la table existe et obtenir des infos
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        n_tup_ins as rows_inserted,
                        n_tup_upd as rows_updated,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables
                    WHERE tablename = %s
                """, [view_name])
                
                row = cursor.fetchone()
                
                if row:
                    views_status.append({
                        'name': view_name,
                        'schema': row[0],
                        'size': row[2],
                        'rows_inserted': row[3],
                        'rows_updated': row[4],
                        'last_vacuum': row[5].isoformat() if row[5] else None,
                        'last_analyze': row[7].isoformat() if row[7] else None,
                        'exists': True
                    })
                else:
                    views_status.append({
                        'name': view_name,
                        'exists': False
                    })
        
        return Response({
            'success': True,
            'views': views_status,
            'total_views': len(MATERIALIZED_VIEWS),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {str(e)}")
        return Response({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
