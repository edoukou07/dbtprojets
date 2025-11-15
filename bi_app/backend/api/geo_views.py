"""
Geographic views for zones mapping
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_ratelimit.decorators import ratelimit
from django.db import connection
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Authentification requise
@ratelimit(key='user', rate='100/m', method='GET')  # 100 requêtes/min par utilisateur
def zones_map_data(request):
    """
    Get geographic data for all zones with occupation statistics
    Returns GeoJSON-like format for mapping
    """
    try:
        with connection.cursor() as cursor:
            # Query to get zones with their geographic data and occupation stats
            cursor.execute("""
                SELECT 
                    z.id,
                    z.code,
                    z.libelle as nom,
                    z.description,
                    z.superficie,
                    z.adresse,
                    z.statut,
                    ST_AsGeoJSON(z.location) as location_geojson,
                    ST_AsGeoJSON(z.polygon) as polygon_geojson,
                    ST_Y(ST_Centroid(z.polygon)) as latitude,
                    ST_X(ST_Centroid(z.polygon)) as longitude,
                    o.nombre_total_lots,
                    o.lots_disponibles,
                    o.lots_attribues,
                    o.lots_reserves,
                    o.superficie_totale,
                    o.superficie_disponible,
                    o.superficie_attribuee,
                    o.taux_occupation_pct,
                    o.taux_viabilisation_pct,
                    o.lots_viabilises,
                    o.nombre_demandes_attribution,
                    o.demandes_approuvees,
                    o.demandes_en_attente
                FROM public.zones_industrielles z
                LEFT JOIN dwh_marts_occupation.mart_occupation_zones o ON z.id = o.zone_id
                WHERE z.statut = 'actif'
                ORDER BY z.libelle
            """)
            
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            zones_data = []
            for row in rows:
                zone_dict = dict(zip(columns, row))
                
                # Parse GeoJSON strings
                if zone_dict['location_geojson']:
                    zone_dict['location'] = json.loads(zone_dict['location_geojson'])
                else:
                    zone_dict['location'] = None
                
                if zone_dict['polygon_geojson']:
                    zone_dict['polygon'] = json.loads(zone_dict['polygon_geojson'])
                else:
                    zone_dict['polygon'] = None
                
                # Remove raw GeoJSON strings
                del zone_dict['location_geojson']
                del zone_dict['polygon_geojson']
                
                # Convert Decimal to float for JSON serialization
                for key in ['superficie', 'latitude', 'longitude', 'superficie_totale', 
                           'superficie_disponible', 'superficie_attribuee', 
                           'taux_occupation_pct', 'taux_viabilisation_pct']:
                    if zone_dict.get(key) is not None:
                        zone_dict[key] = float(zone_dict[key])
                
                zones_data.append(zone_dict)
            
            return Response({
                'success': True,
                'count': len(zones_data),
                'zones': zones_data
            })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Authentification requise
@ratelimit(key='user', rate='100/m', method='GET')  # 100 requêtes/min par utilisateur
def zone_details_map(request, zone_id):
    """
    Get detailed geographic data for a specific zone including lots
    """
    try:
        with connection.cursor() as cursor:
            # Get zone info
            cursor.execute("""
                SELECT 
                    z.id,
                    z.code,
                    z.libelle as nom,
                    z.description,
                    z.superficie,
                    z.adresse,
                    z.statut,
                    ST_AsGeoJSON(z.location) as location_geojson,
                    ST_AsGeoJSON(z.polygon) as polygon_geojson,
                    ST_Y(ST_Centroid(z.polygon)) as latitude,
                    ST_X(ST_Centroid(z.polygon)) as longitude
                FROM public.zones_industrielles z
                WHERE z.id = %s
            """, [zone_id])
            
            zone_row = cursor.fetchone()
            if not zone_row:
                return Response({
                    'success': False,
                    'error': 'Zone not found'
                }, status=404)
            
            columns = [col[0] for col in cursor.description]
            zone_data = dict(zip(columns, zone_row))
            
            # Parse GeoJSON
            if zone_data['location_geojson']:
                zone_data['location'] = json.loads(zone_data['location_geojson'])
            if zone_data['polygon_geojson']:
                zone_data['polygon'] = json.loads(zone_data['polygon_geojson'])
            
            del zone_data['location_geojson']
            del zone_data['polygon_geojson']
            
            # Convert Decimal to float
            for key in ['superficie', 'latitude', 'longitude']:
                if zone_data.get(key) is not None:
                    zone_data[key] = float(zone_data[key])
            
            # Get lots in this zone with their coordinates
            cursor.execute("""
                SELECT 
                    l.id,
                    l.numero,
                    l.superficie,
                    l.statut,
                    l.prix,
                    l.viabilite,
                    l.coordonnees,
                    e.raison_sociale as occupant
                FROM public.lots l
                LEFT JOIN public.demandes_attribution da ON l.id = da.lot_id 
                    AND da.statut = 'VALIDE'
                LEFT JOIN public.entreprises e ON da.entreprise_id = e.id
                WHERE l.zone_industrielle_id = %s
                ORDER BY l.numero
            """, [zone_id])
            
            lots_columns = [col[0] for col in cursor.description]
            lots_rows = cursor.fetchall()
            
            lots_data = []
            for row in lots_rows:
                lot_dict = dict(zip(lots_columns, row))
                
                # Convert Decimal to float
                if lot_dict.get('superficie'):
                    lot_dict['superficie'] = float(lot_dict['superficie'])
                if lot_dict.get('prix'):
                    lot_dict['prix'] = float(lot_dict['prix'])
                
                lots_data.append(lot_dict)
            
            zone_data['lots'] = lots_data
            zone_data['lots_count'] = len(lots_data)
            
            return Response({
                'success': True,
                'zone': zone_data
            })
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
