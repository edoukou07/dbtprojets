"""
API Views for SIGETI BI
"""
from datetime import datetime
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count, Q, F, ExpressionWrapper, IntegerField
from django.db.models.functions import Extract
from rest_framework.decorators import action
from rest_framework.response import Response

from analytics.models import (  
    MartPerformanceFinanciere,
    MartOccupationZones,
    MartPortefeuilleClients,
    MartKPIOperationnels,
    Alert,
    AlertThreshold,
    MartImplantationSuivi,
    MartIndemnisations,
    MartEmploisCrees,
    MartCreancesAgees
)
from .serializers import (
    MartCreancesAgeesSerializer,
    MartEmploisCreesSerializer,
    MartImplantationSuiviSerializer,
    MartIndemnisationsSerializer,
    MartPerformanceFinanciereSerializer,
    MartOccupationZonesSerializer,
    MartPortefeuilleClientsSerializer,
    MartKPIOperationnelsSerializer,
    AlertSerializer,
    AlertThresholdSerializer,
    ReportScheduleSerializer,
    SMTPConfigurationSerializer,
)
from analytics.models import ReportSchedule
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
import csv
import io
import os
from pathlib import Path
from django.utils import timezone
from .cache_decorators import cache_api_response
from django.db.utils import OperationalError, ProgrammingError
from .models import SMTPConfiguration

try:
    # Utilisé pour générer les PDF avec graphiques
    import matplotlib
    matplotlib.use("Agg")  # backend non interactif, évite Tkinter/GUI
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.patches import FancyBboxPatch, Circle
    MATPLOTLIB_AVAILABLE = True
except Exception:  # pragma: no cover - environnement sans matplotlib
    MATPLOTLIB_AVAILABLE = False


def _base_email_settings():
    """Retourne la configuration SMTP définie dans les settings Django."""
    return {
        'backend': getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'),
        'host': getattr(settings, 'EMAIL_HOST', ''),
        'port': getattr(settings, 'EMAIL_PORT', 25),
        'username': getattr(settings, 'EMAIL_HOST_USER', ''),
        'password': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
        'use_tls': getattr(settings, 'EMAIL_USE_TLS', False),
        'use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
        'timeout': getattr(settings, 'EMAIL_TIMEOUT', None),
        'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
    }


def get_effective_email_settings():
    """
    Combine les settings Django avec la configuration SMTP active (si disponible).
    Retourne un tuple (config_dict, source, instance).
    """
    config_dict = _base_email_settings()
    source = 'settings'
    instance = None
    try:
        instance = SMTPConfiguration.get_active()
    except (OperationalError, ProgrammingError):
        instance = None

    if instance:
        overrides = instance.as_connection_kwargs()
        for key, value in overrides.items():
            if value is not None:
                config_dict[key] = value
        source = 'database'

    return config_dict, source, instance


def build_email_connection():
    """
    Construit une connexion SMTP prête à l'emploi ainsi que l'email expéditeur.
    """
    config_dict, source, instance = get_effective_email_settings()

    connection = get_connection(
        backend=config_dict['backend'],
        host=config_dict['host'] or None,
        port=config_dict['port'],
        username=config_dict['username'] or None,
        password=config_dict['password'] or None,
        use_tls=config_dict['use_tls'],
        use_ssl=config_dict['use_ssl'],
        timeout=config_dict['timeout'],
    )
    from_email = config_dict['default_from_email'] or settings.DEFAULT_FROM_EMAIL

    return {
        'connection': connection,
        'from_email': from_email,
        'source': source,
        'instance': instance,
    }


class MartPerformanceFinanciereViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Financial Performance Mart
    
    Filters available:
    - annee: Filter by year
    - mois: Filter by month
    - trimestre: Filter by quarter
    - nom_zone: Filter by zone name
    """
    queryset = MartPerformanceFinanciere.objects.all()
    serializer_class = MartPerformanceFinanciereSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['annee', 'mois', 'trimestre', 'nom_zone']
    ordering_fields = ['annee', 'mois', 'montant_total_facture']
    ordering = ['-annee', '-mois']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('financier_summary', timeout=300)
    def summary(self, request):
        """Get financial summary statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtres personnalisés
        date_debut = request.query_params.get('date_debut')
        date_fin = request.query_params.get('date_fin')
        zone_id = request.query_params.get('zone_id')
        domaine_id = request.query_params.get('domaine_id')
        
        # Appliquer les filtres de dates (format YYYY-MM-DD)
        if date_debut:
            try:
                date_obj = datetime.strptime(date_debut, '%Y-%m-%d')
                queryset = queryset.filter(annee__gte=date_obj.year)
                queryset = queryset.filter(Q(annee__gt=date_obj.year) | Q(mois__gte=date_obj.month))
            except ValueError:
                pass
        
        if date_fin:
            try:
                date_obj = datetime.strptime(date_fin, '%Y-%m-%d')
                queryset = queryset.filter(annee__lte=date_obj.year)
                queryset = queryset.filter(Q(annee__lt=date_obj.year) | Q(mois__lte=date_obj.month))
            except ValueError:
                pass
        
        # Appliquer les filtres zone et domaine
        if zone_id:
            queryset = queryset.filter(nom_zone__icontains=zone_id)
        
        if domaine_id:
            queryset = queryset.filter(domaine_activite_id=domaine_id)
        
        # To avoid double-counting collectes (which are aggregated by trimestre in the mart),
        # we need to sum carefully. Get factures data from all rows, but collectes only once per trimestre.
        
        # Step 1: Sum all factures (these are by month, so we sum them directly)
        factures_summary = queryset.aggregate(
            total_factures=Sum('nombre_factures'),
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
            delai_moyen_paiement=Avg('delai_moyen_paiement'),
            taux_paiement_pct=Avg('taux_paiement_pct'),
        )
        
        # Step 2: Get collectes data (one row per trimestre to avoid duplication)
        # Django's .distinct() doesn't work with .values().annotate() properly
        # So we need to deduplicate manually in Python
        collectes_raw = queryset.values('trimestre').annotate(
            total_collectes=Sum('nombre_collectes'),
            montant_recouvre=Sum('montant_total_recouvre'),
            montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
            taux_recouvrement_moyen=Avg('taux_recouvrement_moyen'),
        )
        
        # Deduplicate by trimestre (keep only one row per trimestre)
        collectes_by_trimestre_dict = {}
        for row in collectes_raw:
            trimestre = row['trimestre']
            if trimestre not in collectes_by_trimestre_dict:
                collectes_by_trimestre_dict[trimestre] = row
        
        collectes_list = list(collectes_by_trimestre_dict.values())
        
        # Step 3: Combine the two
        summary = {
            'total_factures': factures_summary['total_factures'] or 0,
            'ca_total': factures_summary['ca_total'] or 0,
            'ca_paye': factures_summary['ca_paye'] or 0,
            'ca_impaye': factures_summary['ca_impaye'] or 0,
            'delai_moyen_paiement': 0,
            'taux_paiement_pct': 0,
            'total_collectes': 0,
            'montant_recouvre': 0,
            'montant_a_recouvrer': 0,
            'taux_recouvrement': 0,
        }
        
        # Add collectes data (sum of one row per trimestre, deduplicated)
        taux_list = []
        for collectes_row in collectes_list:
            summary['total_collectes'] += collectes_row['total_collectes'] or 0
            summary['montant_recouvre'] += collectes_row['montant_recouvre'] or 0
            summary['montant_a_recouvrer'] += collectes_row['montant_a_recouvrer'] or 0
            if collectes_row['taux_recouvrement_moyen'] is not None:
                taux_list.append(collectes_row['taux_recouvrement_moyen'])
        
        # Average the taux only if we have data
        if taux_list:
            summary['taux_recouvrement'] = sum(taux_list) / len(taux_list)
        else:
            summary['taux_recouvrement'] = 0
        
        # Handle delai_moyen_paiement - calculer directement à partir des vraies factures
        from django.db import connection
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT ROUND(AVG(EXTRACT(DAY FROM (date_paiement - date_creation))))
            FROM factures
            WHERE date_paiement IS NOT NULL
              AND date_creation IS NOT NULL
              AND date_paiement >= date_creation
        """)
        
        delai_result = cursor.fetchone()
        summary['delai_moyen_paiement'] = float(delai_result[0]) if delai_result[0] is not None else 0
        
        # Calculs additionnels
        # Recalculer les taux correctement (pas une moyenne de moyennes)
        if summary['ca_total']:
            summary['taux_paiement_moyen'] = round((summary['ca_paye'] or 0) / summary['ca_total'] * 100, 2)
            summary['taux_impaye_pct'] = round((summary['ca_impaye'] or 0) / summary['ca_total'] * 100, 2)
        else:
            summary['taux_paiement_moyen'] = 0
            summary['taux_impaye_pct'] = 0
        
        # Taux de recouvrement des collectes
        if summary['montant_a_recouvrer']:
            summary['taux_recouvrement_moyen'] = round((summary['montant_recouvre'] or 0) / summary['montant_a_recouvrer'] * 100, 2)
        else:
            summary['taux_recouvrement_moyen'] = summary['taux_recouvrement'] or 0  # Fallback to average if no amounts
        
        return Response(summary)

    
    @action(detail=False, methods=['get'])
    @cache_api_response('financier_by_zone', timeout=300)
    def by_zone(self, request):
        """Get data grouped by zone"""
        annee = request.query_params.get('annee')
        
        queryset = self.get_queryset()
        if annee:
            queryset = queryset.filter(annee=annee)
        
        data = queryset.values('nom_zone').annotate(
            total_facture=Sum('montant_total_facture'),
            total_paye=Sum('montant_paye'),
            total_impaye=Sum('montant_impaye'),
            nombre_factures=Sum('nombre_factures'),
        ).order_by('-total_facture')
        
        # Recalculer le taux de paiement correctement pour chaque zone
        result = []
        for item in data:
            if item['total_facture']:
                item['taux_paiement'] = round((item['total_paye'] or 0) / item['total_facture'] * 100, 2)
            else:
                item['taux_paiement'] = 0
            result.append(item)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def tendances_mensuelles(self, request):
        """Get monthly trends for the current year"""
        annee = request.query_params.get('annee', datetime.now().year)
        
        queryset = self.get_queryset().filter(annee=annee)
        
        tendances = queryset.values('mois').annotate(
            ca_facture=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
            nombre_factures=Sum('nombre_factures'),
        ).order_by('mois')
        
        # Ajouter les noms de mois
        mois_names = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
            5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
            9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        
        result = []
        for item in tendances:
            item['nom_mois'] = mois_names.get(item['mois'], f"Mois {item['mois']}")
            # Recalculer le taux de paiement correctement
            if item['ca_facture']:
                item['taux_paiement'] = round((item['ca_paye'] or 0) / item['ca_facture'] * 100, 2)
            else:
                item['taux_paiement'] = 0
            result.append(item)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def tendances_trimestrielles(self, request):
        """Get quarterly trends"""
        annee = request.query_params.get('annee', datetime.now().year)
        
        queryset = self.get_queryset().filter(annee=annee)
        
        tendances = queryset.values('trimestre').annotate(
            ca_facture=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
        ).order_by('trimestre')
        
        result = []
        for item in tendances:
            item['nom_trimestre'] = f"T{item['trimestre']}"
            # Recalculer le taux de paiement correctement
            if item['ca_facture']:
                item['taux_paiement'] = round((item['ca_paye'] or 0) / item['ca_facture'] * 100, 2)
            else:
                item['taux_paiement'] = 0
            result.append(item)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def analyse_recouvrement(self, request):
        """Detailed recovery analysis"""
        annee = request.query_params.get('annee')
        queryset = self.get_queryset()
        
        if annee:
            queryset = queryset.filter(annee=annee)
        
        # Calcul corrigé: Créances = Total Facturé - Payé
        total_facture = queryset.aggregate(Sum('montant_total_facture'))['montant_total_facture__sum'] or 0
        total_paye = queryset.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0
        total_creances = total_facture - total_paye
        
        analysis = {
            'total_creances': total_creances,
            'montant_recouvre': total_paye,  # Utiliser montant payé comme recouvrement
            'nombre_collectes': queryset.aggregate(Sum('nombre_collectes'))['nombre_collectes__sum'] or 0,
        }
        
        # Taux de recouvrement
        if total_facture > 0:
            analysis['taux_recouvrement'] = (total_paye / total_facture) * 100
        else:
            analysis['taux_recouvrement'] = 0
        
        # Créances restantes = Total Créances - Payé = Impayé
        analysis['creances_restantes'] = total_creances
        
        # Performance par zone
        analysis['par_zone'] = list(queryset.values('nom_zone').annotate(
            creances=Sum('montant_impaye'),
            recouvre=Sum('montant_paye'),
        ).order_by('-creances')[:10])
        
        for zone in analysis['par_zone']:
            if zone['creances']:
                zone['taux_recouvrement'] = (zone['recouvre'] or 0) / zone['creances'] * 100
            else:
                zone['taux_recouvrement'] = 0
        
        return Response(analysis)
    
    @action(detail=False, methods=['get'])
    def top_zones_performance(self, request):
        """Get top and bottom performing zones"""
        annee = request.query_params.get('annee')
        limit = int(request.query_params.get('limit', 5))
        
        queryset = self.get_queryset()
        if annee:
            queryset = queryset.filter(annee=annee)
        
        # Top zones par CA
        top_ca = list(queryset.values('nom_zone').annotate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
        ).order_by('-ca_total')[:limit])
        for item in top_ca:
            item['taux_paiement'] = round((item['ca_paye'] or 0) / (item['ca_total'] or 1) * 100, 2) if item['ca_total'] else 0
        
        # Top zones par taux de paiement
        top_paiement = list(queryset.values('nom_zone').annotate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
        ).order_by('nom_zone')[:limit])
        for item in top_paiement:
            item['taux_paiement'] = round((item['ca_paye'] or 0) / (item['ca_total'] or 1) * 100, 2) if item['ca_total'] else 0
        top_paiement = sorted(top_paiement, key=lambda x: x['taux_paiement'], reverse=True)
        
        # Zones a risque (faible taux de paiement)
        zones_risque = list(queryset.values('nom_zone').annotate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
        ).order_by('nom_zone')[:limit])
        for item in zones_risque:
            item['taux_paiement'] = round((item['ca_paye'] or 0) / (item['ca_total'] or 1) * 100, 2) if item['ca_total'] else 0
        zones_risque = [z for z in zones_risque if z['taux_paiement'] < 70]
        zones_risque = sorted(zones_risque, key=lambda x: x['taux_paiement'])
        
        return Response({
            'top_chiffre_affaires': top_ca,
            'meilleurs_payeurs': top_paiement,
            'zones_a_risque': zones_risque,
        })
    
    @action(detail=False, methods=['get'])
    def comparaison_annuelle(self, request):
        """Compare current year with previous year"""
        annee_actuelle = int(request.query_params.get('annee', datetime.now().year))
        annee_precedente = annee_actuelle - 1
        
        # Donnees annee actuelle
        current = self.get_queryset().filter(annee=annee_actuelle).aggregate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
        )
        if current['ca_total']:
            current['taux_paiement'] = round((current['ca_paye'] or 0) / current['ca_total'] * 100, 2)
        else:
            current['taux_paiement'] = 0
        
        # Donnees annee precedente
        previous = self.get_queryset().filter(annee=annee_precedente).aggregate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
        )
        if previous['ca_total']:
            previous['taux_paiement'] = round((previous['ca_paye'] or 0) / previous['ca_total'] * 100, 2)
        else:
            previous['taux_paiement'] = 0
        
        # Calcul des variations
        comparison = {
            'annee_actuelle': annee_actuelle,
            'annee_precedente': annee_precedente,
            'current': current,
            'previous': previous,
            'variations': {}
        }
        
        if previous['ca_total']:
            comparison['variations']['ca_total'] = ((current['ca_total'] or 0) - previous['ca_total']) / previous['ca_total'] * 100
        else:
            comparison['variations']['ca_total'] = 0
            
        if previous['ca_paye']:
            comparison['variations']['ca_paye'] = ((current['ca_paye'] or 0) - previous['ca_paye']) / previous['ca_paye'] * 100
        else:
            comparison['variations']['ca_paye'] = 0
        
        return Response(comparison)


class MartOccupationZonesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Zone Occupation Mart
    
    Filters available:
    - nom_zone: Filter by zone name
    - taux_occupation_pct__gte: Occupation rate >= value
    """
    queryset = MartOccupationZones.objects.all()
    serializer_class = MartOccupationZonesSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['nom_zone']
    ordering_fields = ['taux_occupation_pct', 'superficie_totale', 'nombre_total_lots']
    ordering = ['-taux_occupation_pct']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('occupation_summary', timeout=300)
    def summary(self, request):
        """Get occupation summary statistics"""
        queryset = self.get_queryset()
        
        # Filtres personnalisés
        zone_id = request.query_params.get('zone_id')
        
        if zone_id:
            queryset = queryset.filter(nom_zone__icontains=zone_id)
        
        summary = queryset.aggregate(
            total_lots=Sum('nombre_total_lots'),
            lots_disponibles=Sum('lots_disponibles'),
            lots_attribues=Sum('lots_attribues'),
            superficie_totale=Sum('superficie_totale'),
            superficie_disponible=Sum('superficie_disponible'),
            superficie_attribuee=Sum('superficie_attribuee'),
            valeur_totale=Sum('valeur_totale_lots'),
        )
        
        # Calculer le nombre de zones
        summary['nombre_zones'] = queryset.count()
        
        # Recalculer le taux d'occupation global correctement (pas une moyenne de moyennes)
        if summary['total_lots']:
            summary['taux_occupation_moyen'] = round(
                (summary['lots_attribues'] or 0) / summary['total_lots'] * 100, 2
            )
        else:
            summary['taux_occupation_moyen'] = 0
        
        # Zones critiques (occupation < 50%)
        summary['zones_faible_occupation'] = queryset.filter(
            taux_occupation_pct__lt=50
        ).count()
        
        # Zones saturées (occupation > 90%)
        summary['zones_saturees'] = queryset.filter(
            taux_occupation_pct__gt=90
        ).count()
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    @cache_api_response('occupation_by_zone', timeout=300)
    def by_zone(self, request):
        """Get detailed data by zone"""
        queryset = self.get_queryset()
        
        data = queryset.values(
            'nom_zone',
            'nombre_total_lots',
            'lots_disponibles',
            'lots_attribues',
            'lots_reserves',
            'superficie_totale',
            'superficie_disponible',
            'superficie_attribuee',
            'taux_occupation_pct',
            'valeur_totale_lots'
        ).order_by('-taux_occupation_pct')
        
        return Response(list(data))
    
    @action(detail=False, methods=['get'])
    def disponibilite(self, request):
        """Get availability statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'par_zone': [],
            'totaux': {
                'lots_disponibles': 0,
                'superficie_disponible': 0,
                'valeur_disponible': 0,
            }
        }
        
        for zone in queryset:
            if zone.lots_disponibles > 0:
                stats['par_zone'].append({
                    'zone': zone.nom_zone,
                    'lots_disponibles': zone.lots_disponibles,
                    'superficie_disponible': zone.superficie_disponible,
                    'taux_occupation': zone.taux_occupation_pct,
                })
                
                stats['totaux']['lots_disponibles'] += zone.lots_disponibles or 0
                stats['totaux']['superficie_disponible'] += zone.superficie_disponible or 0
        
        # Trier par nombre de lots disponibles (décroissant)
        stats['par_zone'].sort(key=lambda x: x['lots_disponibles'], reverse=True)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def top_zones(self, request):
        """Get top zones by occupation rate"""
        limit = int(request.query_params.get('limit', 5))
        queryset = self.get_queryset()
        
        top_occupied = list(queryset.order_by('-taux_occupation_pct')[:limit].values(
            'nom_zone', 'taux_occupation_pct', 'lots_attribues', 'nombre_total_lots'
        ))
        
        low_occupied = list(queryset.order_by('taux_occupation_pct')[:limit].values(
            'nom_zone', 'taux_occupation_pct', 'lots_disponibles', 'nombre_total_lots'
        ))
        
        return Response({
            'plus_occupees': top_occupied,
            'moins_occupees': low_occupied,
        })

    @action(detail=False, methods=['get'])
    def zone_details(self, request):
        """Get detailed information for a specific zone"""
        nom_zone = request.query_params.get('nom_zone')
        
        if not nom_zone:
            return Response({'error': 'nom_zone parameter is required'}, status=400)
        
        try:
            zone = self.get_queryset().get(nom_zone__iexact=nom_zone)
            serializer = self.get_serializer(zone)
            
            # Ajouter des métriques calculées
            data = serializer.data
            
            # Calculs supplémentaires
            if zone.nombre_total_lots:
                data['pct_disponible'] = round((zone.lots_disponibles or 0) / zone.nombre_total_lots * 100, 2)
                data['pct_attribues'] = round((zone.lots_attribues or 0) / zone.nombre_total_lots * 100, 2)
                data['pct_reserves'] = round((zone.lots_reserves or 0) / zone.nombre_total_lots * 100, 2)
            else:
                data['pct_disponible'] = 0
                data['pct_attribues'] = 0
                data['pct_reserves'] = 0
            
            if zone.superficie_totale:
                data['pct_superficie_disponible'] = round((zone.superficie_disponible or 0) / zone.superficie_totale * 100, 2)
                data['pct_superficie_attribuee'] = round((zone.superficie_attribuee or 0) / zone.superficie_totale * 100, 2)
            else:
                data['pct_superficie_disponible'] = 0
                data['pct_superficie_attribuee'] = 0
            
            # Valeur moyenne par lot
            if zone.nombre_total_lots and zone.valeur_totale_lots:
                data['valeur_moyenne_lot'] = round(zone.valeur_totale_lots / zone.nombre_total_lots, 2)
            else:
                data['valeur_moyenne_lot'] = 0
            
            return Response(data)
            
        except MartOccupationZones.DoesNotExist:
            return Response({'error': f'Zone "{nom_zone}" not found'}, status=404)


class MartPortefeuilleClientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Client Portfolio Mart
    
    Filters available:
    - segment_client: Filter by client segment
    - niveau_risque: Filter by risk level
    - secteur_activite: Filter by sector
    """
    queryset = MartPortefeuilleClients.objects.all()
    serializer_class = MartPortefeuilleClientsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['segment_client', 'niveau_risque', 'secteur_activite']
    search_fields = ['raison_sociale', 'registre_commerce']
    ordering_fields = ['chiffre_affaires_total', 'taux_paiement_pct']
    ordering = ['-chiffre_affaires_total']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('clients_summary', timeout=300)
    def summary(self, request):
        """Get comprehensive client portfolio summary with enhanced metrics"""
        from decimal import Decimal
        from datetime import timedelta
        
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtres personnalisés
        zone_id = request.query_params.get('zone_id')
        domaine_id = request.query_params.get('domaine_id')
        
        if zone_id:
            queryset = queryset.filter(nom_zone__icontains=zone_id)
        
        if domaine_id:
            queryset = queryset.filter(secteur_activite__icontains=domaine_id)
        
        summary = queryset.aggregate(
            total_clients=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_paye=Sum('ca_paye'),
            ca_impaye=Sum('ca_impaye'),
            taux_paiement_moyen=Avg('taux_paiement_pct'),
            total_factures=Sum('nombre_factures'),
            total_lots_attribues=Sum('nombre_lots_attribues'),
            superficie_totale=Sum('superficie_totale_attribuee'),
            factures_retard_total=Sum('nombre_factures_retard'),
        )
        
        # Calculate delai_moyen_paiement from mart data (extract days from INTERVAL)
        from django.db import connection
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT ROUND(AVG(EXTRACT(EPOCH FROM delai_moyen_paiement) / 86400))
            FROM dwh_marts_clients.mart_portefeuille_clients
            WHERE delai_moyen_paiement IS NOT NULL
        """)
        
        delai_result = cursor.fetchone()
        summary['delai_moyen_paiement'] = float(delai_result[0]) if delai_result[0] is not None else 0
        
        # Convert Decimal/None to float for safe calculations
        ca_total = float(summary['ca_total'] or 0)
        ca_paye = float(summary['ca_paye'] or 0)
        ca_impaye = float(summary['ca_impaye'] or 0)
        
        # Calculate derived metrics
        if ca_total > 0:
            summary['taux_impaye_pct'] = (ca_impaye / ca_total) * 100
            summary['taux_paye_pct'] = (ca_paye / ca_total) * 100
        else:
            summary['taux_impaye_pct'] = 0
            summary['taux_paye_pct'] = 0
        
        # Segmentation breakdown
        segmentation = queryset.values('segment_client').annotate(
            count=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_paye=Sum('ca_paye'),
            taux_paiement_moyen=Avg('taux_paiement_pct')
        ).order_by('-ca_total')
        
        # Risk level breakdown
        risque = queryset.values('niveau_risque').annotate(
            count=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_impaye=Sum('ca_impaye')
        ).order_by('niveau_risque')
        
        # Sector breakdown
        secteurs = queryset.values('secteur_activite').annotate(
            count=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total')
        ).order_by('-ca_total')[:10]
        
        summary['segmentation'] = list(segmentation)
        summary['par_niveau_risque'] = list(risque)
        summary['par_secteur'] = list(secteurs)
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def client_details(self, request):
        """Get detailed information for a specific client"""
        entreprise_id = request.query_params.get('entreprise_id')
        
        if not entreprise_id:
            return Response({'error': 'entreprise_id parameter is required'}, status=400)
        
        try:
            client = self.get_queryset().get(entreprise_id=entreprise_id)
        except MartPortefeuilleClients.DoesNotExist:
            return Response({'error': 'Client not found'}, status=404)
        
        # Calculer des métriques additionnelles
        from decimal import Decimal
        
        ca_total = float(client.chiffre_affaires_total or 0)
        ca_paye = float(client.ca_paye or 0)
        ca_impaye = float(client.ca_impaye or 0)
        
        # Taux de recouvrement
        taux_recouvrement = round((ca_paye / ca_total * 100), 2) if ca_total > 0 else 0
        
        # Taux d'approbation demandes
        taux_approbation = 0
        if client.nombre_demandes and client.nombre_demandes > 0:
            taux_approbation = round((client.demandes_approuvees or 0) / client.nombre_demandes * 100, 2)
        
        # Délai moyen paiement en jours
        delai_paiement_jours = 0
        if client.delai_moyen_paiement:
            delai_paiement_jours = client.delai_moyen_paiement.days
        
        # Superficie moyenne par lot
        superficie_moy_lot = 0
        if client.nombre_lots_attribues and client.nombre_lots_attribues > 0:
            superficie_moy_lot = round(float(client.superficie_totale_attribuee or 0) / client.nombre_lots_attribues, 2)
        
        # Taux de factures en retard
        taux_factures_retard = 0
        if client.nombre_factures and client.nombre_factures > 0:
            taux_factures_retard = round((client.nombre_factures_retard or 0) / client.nombre_factures * 100, 2)
        
        data = {
            # Informations de base
            'entreprise_id': client.entreprise_id,
            'raison_sociale': client.raison_sociale,
            'forme_juridique': client.forme_juridique,
            'registre_commerce': client.registre_commerce,
            'telephone': client.telephone,
            'email': client.email,
            'secteur_activite': client.secteur_activite,
            
            # Métriques financières
            'nombre_factures': client.nombre_factures or 0,
            'chiffre_affaires_total': ca_total,
            'ca_paye': ca_paye,
            'ca_impaye': ca_impaye,
            'taux_recouvrement': taux_recouvrement,
            'taux_paiement_pct': float(client.taux_paiement_pct or 0),
            
            # Comportement paiement
            'delai_moyen_paiement_jours': delai_paiement_jours,
            'nombre_factures_retard': client.nombre_factures_retard or 0,
            'taux_factures_retard': taux_factures_retard,
            
            # Attributions
            'nombre_demandes': client.nombre_demandes or 0,
            'demandes_approuvees': client.demandes_approuvees or 0,
            'taux_approbation': taux_approbation,
            'superficie_totale_attribuee': float(client.superficie_totale_attribuee or 0),
            'nombre_lots_attribues': client.nombre_lots_attribues or 0,
            'superficie_moyenne_lot': superficie_moy_lot,
            
            # Segmentation
            'segment_client': client.segment_client,
            'niveau_risque': client.niveau_risque,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def segmentation(self, request):
        """Get detailed client segmentation analysis"""
        from datetime import timedelta
        
        queryset = self.get_queryset()
        
        # By segment
        par_segment = list(queryset.values('segment_client').annotate(
            nombre_clients=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_paye=Sum('ca_paye'),
            ca_impaye=Sum('ca_impaye'),
            taux_paiement_moyen=Avg('taux_paiement_pct'),
            nombre_factures=Sum('nombre_factures'),
            delai_moyen_paiement=Avg('delai_moyen_paiement'),
            lots_attribues=Sum('nombre_lots_attribues'),
            superficie_totale=Sum('superficie_totale_attribuee')
        ).order_by('-ca_total'))
        
        # Convert timedelta to days for each segment
        for item in par_segment:
            if item.get('delai_moyen_paiement') and isinstance(item['delai_moyen_paiement'], timedelta):
                item['delai_moyen_paiement'] = item['delai_moyen_paiement'].days
        
        # By risk level
        par_risque = list(queryset.values('niveau_risque').annotate(
            nombre_clients=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_impaye=Sum('ca_impaye'),
            taux_paiement_moyen=Avg('taux_paiement_pct'),
            factures_retard=Sum('nombre_factures_retard')
        ).order_by('niveau_risque'))
        
        # By sector
        par_secteur = list(queryset.values('secteur_activite').annotate(
            nombre_clients=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_paye=Sum('ca_paye'),
            taux_paiement_moyen=Avg('taux_paiement_pct')
        ).order_by('-ca_total')[:15])
        
        return Response({
            'par_segment': par_segment,
            'par_niveau_risque': par_risque,
            'par_secteur': par_secteur
        })
    
    @action(detail=False, methods=['get'])
    def top_clients(self, request):
        """Get top clients by various metrics"""
        limit = int(request.query_params.get('limit', 10))
        
        # Top by revenue
        top_ca = self.get_queryset().filter(
            chiffre_affaires_total__isnull=False
        ).order_by('-chiffre_affaires_total')[:limit]
        
        # Best payers (high payment rate + significant revenue)
        meilleurs_payeurs = self.get_queryset().filter(
            chiffre_affaires_total__gte=1000000,
            taux_paiement_pct__gte=90
        ).order_by('-taux_paiement_pct', '-chiffre_affaires_total')[:limit]
        
        # Biggest debtors
        plus_gros_debiteurs = self.get_queryset().filter(
            ca_impaye__isnull=False
        ).order_by('-ca_impaye')[:limit]
        
        # Most active (by number of invoices)
        plus_actifs = self.get_queryset().filter(
            nombre_factures__isnull=False
        ).order_by('-nombre_factures')[:limit]
        
        return Response({
            'top_chiffre_affaires': self.get_serializer(top_ca, many=True).data,
            'meilleurs_payeurs': self.get_serializer(meilleurs_payeurs, many=True).data,
            'plus_gros_debiteurs': self.get_serializer(plus_gros_debiteurs, many=True).data,
            'plus_actifs': self.get_serializer(plus_actifs, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """Get clients at risk with detailed analysis"""
        # High risk criteria:
        # - Low payment rate (<70%)
        # - High unpaid amount
        # - Marked as high risk
        queryset = self.get_queryset().filter(
            Q(niveau_risque='Risque élevé') | 
            Q(taux_paiement_pct__lt=70) |
            Q(ca_impaye__gte=500000)
        ).order_by('-ca_impaye')
        
        # Calculate risk metrics
        total_at_risk = queryset.count()
        total_creances_risque = queryset.aggregate(
            total=Sum('ca_impaye')
        )['total'] or 0
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'clients_a_risque': serializer.data,
            'nombre_total': total_at_risk,
            'total_creances': total_creances_risque,
            'montant_moyen_creance': total_creances_risque / total_at_risk if total_at_risk > 0 else 0
        })
    
    @action(detail=False, methods=['get'])
    def analyse_comportement(self, request):
        """Analyze client payment behavior patterns"""
        from datetime import timedelta
        
        queryset = self.get_queryset()
        
        # Payment behavior distribution - using mart data  which already has taux_paiement_pct
        comportement = []
        
        # Define payment categories
        categories = [
            {'min': 95, 'max': 100, 'label': 'Excellent (>95%)'},
            {'min': 80, 'max': 95, 'label': 'Bon (80-95%)'},
            {'min': 60, 'max': 80, 'label': 'Moyen (60-80%)'},
            {'min': 0, 'max': 60, 'label': 'Faible (<60%)'}
        ]
        
        for cat in categories:
            # Filter by payment rate from mart (already calculated)
            filtered_qs = queryset.filter(
                taux_paiement_pct__gte=cat['min'],
                taux_paiement_pct__lt=cat['max']
            )
            
            # Aggregate data
            stats = filtered_qs.aggregate(
                count=Count('entreprise_id'),
                ca_total=Sum('chiffre_affaires_total')
            )
            
            # Calculate delai_moyen directly from raw SQL to handle INTERVAL type
            delai_moyen = 0
            if stats['count'] > 0:
                from django.db import connection
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT ROUND(AVG(EXTRACT(EPOCH FROM delai_moyen_paiement) / 86400))
                    FROM dwh_marts_clients.mart_portefeuille_clients
                    WHERE taux_paiement_pct >= %s AND taux_paiement_pct < %s
                      AND delai_moyen_paiement IS NOT NULL
                """, [cat['min'], cat['max']])
                result = cursor.fetchone()
                delai_moyen = int(result[0]) if result[0] else 0
            
            comportement.append({
                'count': stats['count'] or 0,
                'ca_total': float(stats['ca_total'] or 0),
                'delai_moyen': delai_moyen,
                'categorie': cat['label'],
                'min_taux': cat['min'],
                'max_taux': cat['max']
            })
        
        # Payment delay analysis - using mart data
        from django.db import connection
        cursor = connection.cursor()
        
        delai_ranges = [
            {'min': 0, 'max': 30, 'label': '0-30 jours'},
            {'min': 30, 'max': 60, 'label': '30-60 jours'},
            {'min': 60, 'max': 90, 'label': '60-90 jours'},
            {'min': 90, 'max': 999, 'label': '>90 jours'}
        ]
        
        par_delai = []
        for range_def in delai_ranges:
            # Calculate delay from mart data (extract days from INTERVAL)
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT entreprise_id) as count,
                    COALESCE(SUM(chiffre_affaires_total), 0) as ca_total,
                    COALESCE(AVG(taux_paiement_pct), 0) as taux_paiement_moyen
                FROM dwh_marts_clients.mart_portefeuille_clients
                WHERE delai_moyen_paiement IS NOT NULL
                  AND EXTRACT(EPOCH FROM delai_moyen_paiement) / 86400 >= %s
                  AND EXTRACT(EPOCH FROM delai_moyen_paiement) / 86400 < %s
            """, [range_def['min'], range_def['max']])
            
            result = cursor.fetchone()
            stats = {
                'count': result[0] or 0,
                'ca_total': float(result[1]) or 0,
                'taux_paiement_moyen': float(result[2]) or 0,
                'plage_delai': range_def['label']
            }
            par_delai.append(stats)
        
        return Response({
            'par_taux_paiement': comportement,
            'par_delai_paiement': par_delai
        })
    
    @action(detail=False, methods=['get'])
    def analyse_occupation(self, request):
        """Analyze client occupation of industrial lots"""
        from django.db import connection
        cursor = connection.cursor()
        
        queryset = self.get_queryset()
        
        # Clients with attributions
        avec_lots = queryset.filter(nombre_lots_attribues__gt=0)
        sans_lots = queryset.filter(Q(nombre_lots_attribues=0) | Q(nombre_lots_attribues__isnull=True))
        
        # Calculate stats from mart data (already aggregated)
        stats_avec_lots_agg = avec_lots.aggregate(
            nombre_clients=Count('entreprise_id'),
            total_lots=Sum('nombre_lots_attribues'),
            superficie_totale=Sum('superficie_totale_attribuee')
        )
        
        stats_avec_lots = {
            'nombre_clients': stats_avec_lots_agg['nombre_clients'] or 0,
            'total_lots': stats_avec_lots_agg['total_lots'] or 0,
            'superficie_totale': float(stats_avec_lots_agg['superficie_totale'] or 0),
        }
        
        # Get CA stats from the marts queryset
        ca_stats = avec_lots.aggregate(
            ca_total=Sum('chiffre_affaires_total'),
            ca_moyen=Avg('chiffre_affaires_total')
        )
        stats_avec_lots['ca_total'] = float(ca_stats['ca_total'] or 0)
        stats_avec_lots['ca_moyen'] = float(ca_stats['ca_moyen'] or 0)
        
        stats_sans_lots = sans_lots.aggregate(
            nombre_clients=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_moyen=Avg('chiffre_affaires_total')
        )
        
        # Distribution by number of lots
        par_nombre_lots = avec_lots.values('nombre_lots_attribues').annotate(
            count=Count('entreprise_id')
        ).order_by('nombre_lots_attribues')
        
        return Response({
            'avec_lots': stats_avec_lots,
            'sans_lots': stats_sans_lots,
            'distribution_lots': list(par_nombre_lots)
        })


class MartKPIOperationnelsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Operational KPIs Mart
    
    Filters available:
    - annee: Filter by year
    - trimestre: Filter by quarter
    - nom_mois: Filter by month name
    """
    queryset = MartKPIOperationnels.objects.all()
    serializer_class = MartKPIOperationnelsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['annee', 'trimestre', 'nom_mois']
    ordering_fields = ['annee', 'trimestre']
    ordering = ['-annee', 'trimestre']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('operationnel_summary', timeout=300)
    def summary(self, request):
        """Get operational KPIs summary"""
        from datetime import datetime as dt
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtres personnalisés
        date_debut = request.query_params.get('date_debut')
        date_fin = request.query_params.get('date_fin')
        zone_id = request.query_params.get('zone_id')
        
        # Filtre par année par défaut (année actuelle)
        current_year = dt.now().year
        if not date_debut and not date_fin:
            queryset = queryset.filter(annee=current_year)
        
        # Appliquer les filtres de dates
        if date_debut:
            try:
                date_obj = datetime.strptime(date_debut, '%Y-%m-%d')
                queryset = queryset.filter(annee__gte=date_obj.year)
            except ValueError:
                pass
        
        if date_fin:
            try:
                date_obj = datetime.strptime(date_fin, '%Y-%m-%d')
                queryset = queryset.filter(annee__lte=date_obj.year)
            except ValueError:
                pass
        
        summary = queryset.aggregate(
            # Collectes
            total_collectes=Sum('nombre_collectes'),
            taux_cloture_moyen=Avg('taux_cloture_pct'),
            taux_recouvrement_moyen=Avg('taux_recouvrement_global_pct'),
            
            # Attributions
            total_demandes=Sum('nombre_demandes'),
            total_approuvees=Sum('demandes_approuvees'),
            taux_approbation_moyen=Avg('taux_approbation_pct'),
            
            # Facturation
            total_factures=Sum('nombre_factures_emises'),
            total_payees=Sum('factures_payees'),
        )
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get monthly trends for the current year"""
        annee = request.query_params.get('annee')
        
        queryset = self.get_queryset()
        if annee:
            queryset = queryset.filter(annee=annee)
        else:
            # Get latest year
            latest = queryset.order_by('-annee').first()
            if latest:
                queryset = queryset.filter(annee=latest.annee)
        
        data = queryset.order_by('trimestre').values(
            'nom_mois', 'trimestre',
            'taux_recouvrement_global_pct',
            'taux_approbation_pct',
            'nombre_factures_emises',
            'montant_total_facture'
        )
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def performance_collectes(self, request):
        """Analyse détaillée de la performance des collectes"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Agrégations par trimestre
        par_trimestre = queryset.values('annee', 'trimestre').annotate(
            total_collectes=Sum('nombre_collectes'),
            collectes_cloturees=Sum('collectes_cloturees'),
            taux_cloture=Avg('taux_cloture_pct'),
            taux_recouvrement=Avg('taux_recouvrement_global_pct'),
            duree_moyenne=Avg('duree_moyenne_collecte_jours'),
            montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
            montant_recouvre=Sum('montant_total_recouvre')
        ).order_by('annee', 'trimestre')
        
        # Agrégation globale
        global_stats = queryset.aggregate(
            total_collectes=Sum('nombre_collectes'),
            total_cloturees=Sum('collectes_cloturees'),
            total_ouvertes=Sum('collectes_ouvertes'),
            taux_cloture_moyen=Avg('taux_cloture_pct'),
            taux_recouvrement_moyen=Avg('taux_recouvrement_global_pct'),
            duree_moyenne_jours=Avg('duree_moyenne_collecte_jours'),
            montant_total_a_recouvrer=Sum('montant_total_a_recouvrer'),
            montant_total_recouvre=Sum('montant_total_recouvre')
        )
        
        return Response({
            'global': global_stats,
            'par_trimestre': list(par_trimestre)
        })
    
    @action(detail=False, methods=['get'])
    def performance_attributions(self, request):
        """Analyse détaillée de la performance des attributions"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Agrégations par trimestre
        par_trimestre = queryset.values('annee', 'trimestre').annotate(
            total_demandes=Sum('nombre_demandes'),
            demandes_approuvees=Sum('demandes_approuvees'),
            demandes_rejetees=Sum('demandes_rejetees'),
            demandes_en_attente=Sum('demandes_en_attente'),
            taux_approbation=Avg('taux_approbation_pct'),
            delai_moyen=Avg('delai_moyen_attribution_jours')
        ).order_by('annee', 'trimestre')
        
        # Agrégation globale
        global_stats = queryset.aggregate(
            total_demandes=Sum('nombre_demandes'),
            total_approuvees=Sum('demandes_approuvees'),
            total_rejetees=Sum('demandes_rejetees'),
            total_en_attente=Sum('demandes_en_attente'),
            taux_approbation_moyen=Avg('taux_approbation_pct'),
            delai_moyen_jours=Avg('delai_moyen_attribution_jours')
        )
        
        return Response({
            'global': global_stats,
            'par_trimestre': list(par_trimestre)
        })
    
    @action(detail=False, methods=['get'])
    def performance_facturation(self, request):
        """Analyse détaillée de la performance de facturation"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Agrégation globale simple (sans delai_moyen_paiement qui est interval)
            global_stats = queryset.aggregate(
                total_factures_emises=Sum('nombre_factures_emises'),
                total_factures_payees=Sum('factures_payees'),
                montant_total_facture=Sum('montant_total_facture'),
                montant_total_paye=Sum('montant_paye')
            )
            
            # Sécuriser les valeurs None et convertir Decimal en float
            def safe_float(val):
                if val is None:
                    return 0.0
                return float(val)
            
            total_factures_emises = safe_float(global_stats.get('total_factures_emises'))
            total_factures_payees = safe_float(global_stats.get('total_factures_payees'))
            montant_total_facture = safe_float(global_stats.get('montant_total_facture'))
            montant_total_paye = safe_float(global_stats.get('montant_total_paye'))
            delai_moyen = 0  # Pas de calcul de délai moyen global pour éviter les erreurs timedelta
            
            # Calcul des taux globaux
            taux_paiement_pct = (total_factures_payees / total_factures_emises * 100) if total_factures_emises > 0 else 0
            taux_recouvrement_pct = (montant_total_paye / montant_total_facture * 100) if montant_total_facture > 0 else 0
            
            # Agrégations par trimestre (sans delai_moyen)
            par_trimestre = list(queryset.values('annee', 'trimestre').annotate(
                factures_emises=Sum('nombre_factures_emises'),
                factures_payees=Sum('factures_payees'),
                montant_facture=Sum('montant_total_facture'),
                montant_paye=Sum('montant_paye')
            ).order_by('annee', 'trimestre'))
            
            # Calcul des taux pour chaque trimestre
            for item in par_trimestre:
                fe = safe_float(item.get('factures_emises'))
                fp = safe_float(item.get('factures_payees'))
                mf = safe_float(item.get('montant_facture'))
                mp = safe_float(item.get('montant_paye'))
                
                item['factures_emises'] = int(fe)
                item['factures_payees'] = int(fp)
                item['montant_facture'] = mf
                item['montant_paye'] = mp
                item['delai_moyen'] = 0  # Pas de délai moyen
                item['taux_paiement_pct'] = (fp / fe * 100) if fe > 0 else 0
                item['taux_recouvrement_pct'] = (mp / mf * 100) if mf > 0 else 0
            
            return Response({
                'global': {
                    'total_factures_emises': int(total_factures_emises),
                    'total_factures_payees': int(total_factures_payees),
                    'montant_total_facture': montant_total_facture,
                    'montant_total_paye': montant_total_paye,
                    'delai_moyen_paiement': delai_moyen,
                    'taux_paiement_pct': taux_paiement_pct,
                    'taux_recouvrement_pct': taux_recouvrement_pct
                },
                'par_trimestre': par_trimestre
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'global': {
                    'total_factures_emises': 0,
                    'total_factures_payees': 0,
                    'montant_total_facture': 0,
                    'montant_total_paye': 0,
                    'delai_moyen_paiement': 0,
                    'taux_paiement_pct': 0,
                    'taux_recouvrement_pct': 0
                },
                'par_trimestre': []
            })
    
    @action(detail=False, methods=['get'])
    def indicateurs_cles(self, request):
        """Indicateurs clés de performance opérationnelle"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Récupérer les données du dernier trimestre via values()
        latest_data = queryset.order_by('-annee', '-trimestre').values(
            'annee', 'trimestre'
        ).first()
        
        if not latest_data:
            return Response({
                'message': 'Aucune donnée disponible'
            })
        
        latest_annee = latest_data['annee']
        latest_trimestre = latest_data['trimestre']
        
        dernier_trimestre = queryset.filter(
            annee=latest_annee, 
            trimestre=latest_trimestre
        ).aggregate(
            # Collectes
            nombre_collectes=Sum('nombre_collectes'),
            taux_cloture=Avg('taux_cloture_pct'),
            taux_recouvrement=Avg('taux_recouvrement_global_pct'),
            duree_moyenne_collecte=Avg('duree_moyenne_collecte_jours'),
            
            # Attributions
            nombre_demandes=Sum('nombre_demandes'),
            taux_approbation=Avg('taux_approbation_pct'),
            delai_moyen_attribution=Avg('delai_moyen_attribution_jours'),
            
            # Facturation
            nombre_factures=Sum('nombre_factures_emises'),
            delai_moyen_paiement=Avg('delai_moyen_paiement_jours'),
            
            # Montants
            montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
            montant_recouvre=Sum('montant_total_recouvre')
        )
        
        # Comparer avec le trimestre précédent
        trimestre_precedent = None
        if latest_trimestre and latest_trimestre > 1:
            trimestre_precedent = queryset.filter(
                annee=latest_annee,
                trimestre=latest_trimestre - 1
            ).aggregate(
                taux_recouvrement=Avg('taux_recouvrement_global_pct'),
                taux_approbation=Avg('taux_approbation_pct'),
            )
        
        # Calculer les évolutions
        evolution = {}
        if trimestre_precedent:
            if trimestre_precedent['taux_recouvrement']:
                evolution['taux_recouvrement'] = dernier_trimestre['taux_recouvrement'] - trimestre_precedent['taux_recouvrement']
            if trimestre_precedent['taux_approbation']:
                evolution['taux_approbation'] = dernier_trimestre['taux_approbation'] - trimestre_precedent['taux_approbation']
        
        return Response({
            'periode': {
                'annee': latest_annee,
                'trimestre': latest_trimestre
            },
            'indicateurs': dernier_trimestre,
            'evolution': evolution
        })


# ==========================================
# Authentication Views
# ==========================================

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
import json


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint (Updated to support JWT and username/email)
    POST /api/auth/login/
    Body: {"username": "user@example.com" or "username", "password": "password"}
    """
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        
        data = json.loads(request.body)
        username = data.get('username')  # Can be email or username
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'error': 'Username/email et password requis'
            }, status=400)
        
        # Try to authenticate with username first
        user = authenticate(request, username=username, password=password)
        
        # If failed and username contains @, try with email
        if user is None and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None and user.is_active:
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Get user dashboards permissions
            from analytics.models import UserDashboardPermission
            dashboards = list(
                UserDashboardPermission.objects.filter(user=user).values_list('dashboard', flat=True)
            )
            
            return JsonResponse({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'dashboards': dashboards,
                }
            })
        else:
            return JsonResponse({
                'error': 'Identifiants invalides'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Format JSON invalide'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint
    POST /api/auth/logout/
    """
    try:
        # Supprimer le token
        request.user.auth_token.delete()
        logout(request)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current user information
    GET /api/auth/user/
    """
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
    })


class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Alerts
    
    Actions:
    - list: Get all alerts (filterable by status, severity, type)
    - retrieve: Get a specific alert
    - create: Create a new alert (usually done automatically)
    - update/partial_update: Update alert (e.g., acknowledge, resolve)
    - destroy: Delete an alert
    - active: Get only active alerts
    - acknowledge: Mark alert as acknowledged
    - resolve: Mark alert as resolved
    - check_thresholds: Check all thresholds and create alerts
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'severity', 'alert_type']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active (non-resolved) alerts"""
        active_alerts = self.queryset.filter(status='active')
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = request.user.username if hasattr(request, 'user') else 'system'
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = datetime.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_thresholds(self, request):
        """
        Check all active thresholds and create alerts if needed
        This would typically be called by a scheduler (Celery, cron, etc.)
        """
        from django.utils import timezone
        
        thresholds = AlertThreshold.objects.filter(is_active=True)
        alerts_created = []
        
        for threshold in thresholds:
            # Taux de recouvrement
            if threshold.alert_type == 'taux_recouvrement':
                recent_data = MartPerformanceFinanciere.objects.all().order_by('-annee', '-mois')[:1]
                if recent_data.exists():
                    data = recent_data.first()
                    if data.taux_recouvrement_moyen is not None:
                        taux = float(data.taux_recouvrement_moyen)
                        threshold_val = float(threshold.threshold_value)
                        
                        should_alert = False
                        if threshold.threshold_operator == '<' and taux < threshold_val:
                            should_alert = True
                        elif threshold.threshold_operator == '>' and taux > threshold_val:
                            should_alert = True
                        elif threshold.threshold_operator == '<=' and taux <= threshold_val:
                            should_alert = True
                        elif threshold.threshold_operator == '>=' and taux >= threshold_val:
                            should_alert = True
                        
                        if should_alert:
                            # Vérifier si une alerte similaire existe déjà (dernières 24h)
                            existing_alert = Alert.objects.filter(
                                alert_type='taux_recouvrement',
                                status='active',
                                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
                            ).first()
                            
                            if not existing_alert:
                                alert = Alert.objects.create(
                                    alert_type='taux_recouvrement',
                                    severity='high' if taux < 50 else 'medium',
                                    title=f"Taux de recouvrement critique: {taux:.1f}%",
                                    message=f"Le taux de recouvrement moyen ({taux:.1f}%) est en dessous du seuil de {threshold_val}%. Action immédiate requise.",
                                    threshold_value=threshold_val,
                                    actual_value=taux,
                                    context_data={
                                        'annee': data.annee,
                                        'mois': data.mois,
                                        'zone': data.nom_zone
                                    }
                                )
                                alerts_created.append(alert.id)
            
            # Factures impayées anciennes
            elif threshold.alert_type == 'facture_impayee':
                old_invoices = MartPerformanceFinanciere.objects.filter(
                    montant_impaye__gt=0,
                    delai_moyen_paiement__gt=threshold.threshold_value
                )
                
                if old_invoices.exists():
                    total_impaye = old_invoices.aggregate(total=Sum('montant_impaye'))['total']
                    
                    existing_alert = Alert.objects.filter(
                        alert_type='facture_impayee',
                        status='active',
                        created_at__gte=timezone.now() - timezone.timedelta(days=7)
                    ).first()
                    
                    if not existing_alert:
                        alert = Alert.objects.create(
                            alert_type='facture_impayee',
                            severity='critical',
                            title=f"{old_invoices.count()} factures impayées anciennes",
                            message=f"Il y a {old_invoices.count()} factures avec un délai de paiement > {threshold.threshold_value} jours. Montant total impayé: {total_impaye:,.0f} F CFA",
                            threshold_value=threshold.threshold_value,
                            actual_value=old_invoices.count(),
                            context_data={
                                'count': old_invoices.count(),
                                'total_impaye': float(total_impaye) if total_impaye else 0
                            }
                        )
                        alerts_created.append(alert.id)
            
            # Occupation faible
            elif threshold.alert_type == 'occupation_faible':
                low_occupation_zones = MartOccupationZones.objects.filter(
                    taux_occupation_pct__lt=threshold.threshold_value
                )
                
                for zone in low_occupation_zones:
                    existing_alert = Alert.objects.filter(
                        alert_type='occupation_faible',
                        status='active',
                        context_data__zone_id=zone.zone_id,
                        created_at__gte=timezone.now() - timezone.timedelta(days=7)
                    ).first()
                    
                    if not existing_alert:
                        alert = Alert.objects.create(
                            alert_type='occupation_faible',
                            severity='medium',
                            title=f"Taux d'occupation faible: {zone.nom_zone}",
                            message=f"La zone {zone.nom_zone} a un taux d'occupation de {zone.taux_occupation_pct:.1f}%, en dessous du seuil de {threshold.threshold_value}%.",
                            threshold_value=threshold.threshold_value,
                            actual_value=zone.taux_occupation_pct,
                            context_data={
                                'zone_id': zone.zone_id,
                                'zone_nom': zone.nom_zone,
                                'lots_disponibles': zone.lots_disponibles
                            }
                        )
                        alerts_created.append(alert.id)
            
            # Mettre à jour last_checked
            threshold.last_checked = timezone.now()
            threshold.save()
        
        return Response({
            'success': True,
            'alerts_created': len(alerts_created),
            'alert_ids': alerts_created
        })


class AlertThresholdViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Alert Thresholds Configuration
    
    Actions:
    - list: Get all configured thresholds
    - retrieve: Get a specific threshold
    - create: Create a new threshold
    - update/partial_update: Update threshold configuration
    - destroy: Delete a threshold
    - toggle: Enable/disable a threshold
    """
    queryset = AlertThreshold.objects.all()
    serializer_class = AlertThresholdSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'alert_type']
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle threshold active status"""
        threshold = self.get_object()
        threshold.is_active = not threshold.is_active
        threshold.save()
        
        serializer = self.get_serializer(threshold)
        return Response(serializer.data)


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """Manage scheduled report generation and sending"""

    queryset = ReportSchedule.objects.all().order_by('-scheduled_at')
    serializer_class = ReportScheduleSerializer

    def _save_pdfs(self, report_instance, pdfs_from_request):
        """Sauvegarde les PDFs dans le système de fichiers et met à jour pdfs_data"""
        if not pdfs_from_request:
            return
        
        # Créer le répertoire pour ce rapport
        report_dir = Path(settings.MEDIA_ROOT) / 'reports' / str(report_instance.id)
        report_dir.mkdir(parents=True, exist_ok=True)
        
        pdfs_data = {}
        
        # Sauvegarder chaque PDF
        for key, file in pdfs_from_request.items():
            if key.startswith('pdf_'):
                dashboard_name = key.replace('pdf_', '')
                # Valider le type de fichier
                if file.content_type != 'application/pdf':
                    continue
                
                # Limiter la taille (par exemple 50MB)
                if file.size > 50 * 1024 * 1024:
                    continue
                
                # Nom du fichier
                filename = f"{dashboard_name}.pdf"
                file_path = report_dir / filename
                
                # Sauvegarder le fichier
                with open(file_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                
                # Stocker le chemin relatif dans pdfs_data
                relative_path = f"reports/{report_instance.id}/{filename}"
                pdfs_data[dashboard_name] = relative_path
        
        # Mettre à jour pdfs_data
        if pdfs_data:
            report_instance.pdfs_data = pdfs_data
            report_instance.save(update_fields=['pdfs_data'])

    def _cleanup_pdfs(self, report_instance):
        """Supprime les PDFs stockés pour ce rapport"""
        if not report_instance.pdfs_data:
            return
        
        report_dir = Path(settings.MEDIA_ROOT) / 'reports' / str(report_instance.id)
        if report_dir.exists():
            # Supprimer tous les fichiers dans le répertoire
            for file_path in report_dir.glob('*.pdf'):
                try:
                    file_path.unlink()
                except Exception:
                    pass
            
            # Supprimer le répertoire s'il est vide
            try:
                report_dir.rmdir()
            except Exception:
                pass

    def perform_create(self, serializer):
        # attach user if authenticated
        user = self.request.user if self.request.user.is_authenticated else None
        report_instance = serializer.save(created_by=user)
        
        # Gérer les PDFs si présents dans la requête
        if self.request.FILES:
            pdfs_from_request = {k: v for k, v in self.request.FILES.items() if k.startswith('pdf_')}
            if pdfs_from_request:
                self._save_pdfs(report_instance, pdfs_from_request)

    def perform_update(self, serializer):
        # Récupérer l'instance avant la mise à jour pour nettoyer les anciens PDFs
        old_instance = serializer.instance
        
        # Si on modifie un rapport récurrent parent, supprimer les occurrences futures non envoyées
        # car elles seront recréées avec la nouvelle configuration
        if old_instance.is_recurring and not old_instance.parent_schedule:
            occurrences = ReportSchedule.objects.filter(
                parent_schedule=old_instance,
                sent=False
            )
            for occurrence in occurrences:
                self._cleanup_pdfs(occurrence)
                occurrence.delete()
        
        # Sauvegarder les modifications
        report_instance = serializer.save()
        
        # Si de nouveaux PDFs sont fournis, nettoyer les anciens et sauvegarder les nouveaux
        if self.request.FILES:
            pdfs_from_request = {k: v for k, v in self.request.FILES.items() if k.startswith('pdf_')}
            if pdfs_from_request:
                # Nettoyer les anciens PDFs
                self._cleanup_pdfs(old_instance)
                # Sauvegarder les nouveaux PDFs
                self._save_pdfs(report_instance, pdfs_from_request)

    def perform_destroy(self, instance):
        """Nettoie les PDFs avant de supprimer le rapport. 
        Si c'est un rapport récurrent parent, supprime aussi toutes les occurrences futures."""
        # Si c'est un rapport parent récurrent, supprimer toutes les occurrences futures non envoyées
        if instance.is_recurring and not instance.parent_schedule:
            # Supprimer toutes les occurrences futures non envoyées
            occurrences = ReportSchedule.objects.filter(
                parent_schedule=instance,
                sent=False
            )
            for occurrence in occurrences:
                self._cleanup_pdfs(occurrence)
                occurrence.delete()
        elif instance.parent_schedule:
            # Si c'est une occurrence, supprimer seulement celle-ci
            pass
        
        # Nettoyer les PDFs et supprimer
        self._cleanup_pdfs(instance)
        instance.delete()

    @action(detail=True, methods=['get'])
    def next_occurrence(self, request, pk=None):
        """Retourne la prochaine occurrence calculée pour un rapport récurrent"""
        from analytics.recurrence import RecurrenceCalculator
        
        report = self.get_object()
        if not report.is_recurring or report.recurrence_type == 'none':
            return Response({
                'error': 'Ce rapport n\'est pas récurrent'
            }, status=400)
        
        next_dt = RecurrenceCalculator.calculate_next_occurrence(report)
        if not next_dt:
            return Response({
                'next_occurrence': None,
                'message': 'Aucune occurrence future (date de fin atteinte)'
            })
        
        return Response({
            'next_occurrence': next_dt.isoformat(),
            'occurrence_number': report.occurrence_number + 1
        })

    @action(detail=False, methods=['post'])
    def send_scheduled(self, request):
        """
        Envoie automatiquement tous les rapports programmés dont la date/heure est arrivée.
        Cette action peut être appelée manuellement ou par un scheduler.
        """
        now = timezone.now()
        scheduled_reports = ReportSchedule.objects.filter(
            scheduled_at__lte=now,
            sent=False
        ).order_by('scheduled_at')
        
        if not scheduled_reports.exists():
            return Response({
                'success': True,
                'message': 'Aucun rapport programmé à envoyer',
                'sent_count': 0
            })
        
        # Utiliser la logique du management command
        sent_count = 0
        failed_count = 0
        errors = []
        
        for report in scheduled_reports:
            try:
                recipients = [r.strip() for r in (report.recipients or '').split(',') if r.strip()]
                if not recipients:
                    continue
                
                dashboards_list = report.get_dashboards_list()
                mail_ctx = build_email_connection()
                
                try:
                    connection = mail_ctx['connection']
                    
                    if len(dashboards_list) > 1:
                        subject = f"SIGETI - Report: {report.name}"
                        body = f"Veuillez trouver ci-joints les rapports PDF pour les tableaux de bord suivants : {', '.join(dashboards_list)}."
                        
                        msg = EmailMessage(
                            subject=subject,
                            body=body,
                            from_email=mail_ctx['from_email'],
                            to=recipients,
                            connection=connection,
                        )
                        
                        for dashboard in dashboards_list:
                            pdf_bytes = generate_dashboard_report_pdf(dashboard)
                            filename = f"report_{dashboard}_{report.id}.pdf"
                            msg.attach(filename, pdf_bytes, 'application/pdf')
                    else:
                        dashboard = dashboards_list[0] if dashboards_list else report.dashboard
                        pdf_bytes = generate_dashboard_report_pdf(dashboard)
                        
                        subject = f"SIGETI - Report: {report.name}"
                        body = f"Veuillez trouver ci-joint le rapport PDF pour le tableau de bord '{dashboard}'."
                        
                        msg = EmailMessage(
                            subject=subject,
                            body=body,
                            from_email=mail_ctx['from_email'],
                            to=recipients,
                            connection=connection,
                        )
                        
                        filename = f"report_{dashboard}_{report.id}.pdf"
                        msg.attach(filename, pdf_bytes, 'application/pdf')
                    
                    msg.send()
                    report.sent = True
                    report.sent_at = timezone.now()
                    if mail_ctx['instance']:
                        mail_ctx['instance'].mark_test_result(True)
                    sent_count += 1
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Erreur lors de l'envoi du rapport {report.id}: {str(e)}")
                    report.sent = True  # Marquer comme envoyé pour éviter les tentatives infinies
                    report.sent_at = timezone.now()
                    failed_count += 1
                    errors.append(f"Rapport {report.id} ({report.name}): {str(e)}")
                
                report.save()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erreur lors du traitement du rapport {report.id}: {str(e)}")
                failed_count += 1
                errors.append(f"Rapport {report.id}: {str(e)}")
        
        return Response({
            'success': True,
            'message': f'{sent_count} rapport(s) envoyé(s) avec succès',
            'sent_count': sent_count,
            'failed_count': failed_count,
            'errors': errors if errors else None
        })

    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        schedule = self.get_object()
        recipients = [r.strip() for r in (schedule.recipients or '').split(',') if r.strip()]

        if not recipients:
            return Response(
                {
                    'success': False,
                    'message': "Aucun destinataire n'a été défini pour ce rapport.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Génération du rapport au format PDF avec graphiques
        dashboards_list = schedule.get_dashboards_list()
        
        # Send email with error handling
        mail_ctx = build_email_connection()

        try:
            connection = mail_ctx['connection']
            
            # Vérifier si des PDFs sont envoyés depuis le frontend (react-pdf)
            pdfs_from_frontend = {}
            if request.FILES:
                # Les PDFs sont envoyés avec des noms comme "pdf_dashboard", "pdf_financier", etc.
                for key, file in request.FILES.items():
                    if key.startswith('pdf_'):
                        dashboard_name = key.replace('pdf_', '')
                        pdfs_from_frontend[dashboard_name] = file.read()
            
            # Générer un PDF séparé pour chaque dashboard
            if len(dashboards_list) > 1:
                # Plusieurs dashboards : envoyer plusieurs PDFs séparés
                subject = f"SIGETI - Report: {schedule.name}"
                body = f"Veuillez trouver ci-joints les rapports PDF pour les tableaux de bord suivants : {', '.join(dashboards_list)}."
                
                msg = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=mail_ctx['from_email'],
                    to=recipients,
                    connection=connection,
                )
                
                # Attacher un PDF pour chaque dashboard
                for dashboard in dashboards_list:
                    # Utiliser le PDF du frontend si disponible, sinon générer avec matplotlib
                    if dashboard in pdfs_from_frontend:
                        pdf_bytes = pdfs_from_frontend[dashboard]
                    else:
                        pdf_bytes = generate_dashboard_report_pdf(dashboard)
                    filename = f"report_{dashboard}_{schedule.id}.pdf"
                    msg.attach(
                        filename,
                        pdf_bytes,
                        'application/pdf',
                    )
            else:
                # Un seul dashboard : envoyer un seul PDF
                dashboard = dashboards_list[0] if dashboards_list else schedule.dashboard
                
                # Utiliser le PDF du frontend si disponible, sinon générer avec matplotlib
                if dashboard in pdfs_from_frontend:
                    pdf_bytes = pdfs_from_frontend[dashboard]
                elif pdfs_from_frontend and len(pdfs_from_frontend) > 0:
                    # Si un seul PDF est envoyé sans nom spécifique
                    pdf_bytes = list(pdfs_from_frontend.values())[0]
                else:
                    pdf_bytes = generate_dashboard_report_pdf(dashboard)
                
                subject = f"SIGETI - Report: {schedule.name}"
                body = f"Veuillez trouver ci-joint le rapport PDF pour le tableau de bord '{dashboard}'."
                
                msg = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=mail_ctx['from_email'],
                    to=recipients,
                    connection=connection,
                )
                
                filename = f"report_{dashboard}_{schedule.id}.pdf"
                msg.attach(
                    filename,
                    pdf_bytes,
                    'application/pdf',
                )
            
            msg.send()
            email_status = 'sent'
        except Exception as e:
            # Log the error mais on remonte l'info au client
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Email sending failed for report {schedule.id}: {str(e)}")
            if mail_ctx['instance']:
                mail_ctx['instance'].mark_test_result(False, str(e))
            email_status = 'failed'

        if email_status == 'sent':
            schedule.sent = True
            schedule.sent_at = timezone.now()
            if mail_ctx['instance']:
                mail_ctx['instance'].mark_test_result(True)

        schedule.save()

        return Response({
            'success': True, 
            'sent_to': recipients,
            'email_status': email_status,
            'smtp_source': mail_ctx['source'],
            'message': 'Rapport envoyé avec succès' if email_status == 'sent' else "Échec de l'envoi du rapport"
        })


class SMTPConfigurationViewSet(viewsets.ModelViewSet):
    """CRUD + diagnostics pour la configuration SMTP."""

    queryset = SMTPConfiguration.objects.all().order_by('-updated_at')
    serializer_class = SMTPConfigurationSerializer
    permission_classes = [IsAdminUser]

    def _ensure_single_active(self, instance):
        """Désactive les autres configurations actives."""
        if instance.is_active:
            SMTPConfiguration.objects.exclude(pk=instance.pk).update(is_active=False)

    def perform_create(self, serializer):
        instance = serializer.save()
        self._ensure_single_active(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._ensure_single_active(instance)

    @action(detail=False, methods=['get'])
    def status(self, request):
        config_dict, source, instance = get_effective_email_settings()
        return Response({
            'source': source,
            'active_configuration_id': instance.id if instance else None,
            'host': config_dict['host'],
            'port': config_dict['port'],
            'use_tls': config_dict['use_tls'],
            'use_ssl': config_dict['use_ssl'],
            'default_from_email': config_dict['default_from_email'],
            'last_test_status': instance.last_test_status if instance else 'unknown',
            'last_tested_at': instance.last_tested_at if instance else None,
        })

    @action(detail=False, methods=['post'])
    def test(self, request):
        """Envoie un email de test vers l'adresse fournie."""
        to_email = request.data.get('to') or request.user.email or settings.DEFAULT_FROM_EMAIL
        subject = request.data.get('subject', 'Test SMTP SIGETI BI')
        message = request.data.get('message', "Ceci est un email de test envoyé par SIGETI BI.")

        mail_ctx = build_email_connection()

        try:
            msg = EmailMessage(
                subject=subject,
                body=message,
                from_email=mail_ctx['from_email'],
                to=[to_email],
                connection=mail_ctx['connection'],
            )
            msg.send()
            if mail_ctx['instance']:
                mail_ctx['instance'].mark_test_result(True)
            return Response({
                'success': True,
                'message': f'Email de test envoyé à {to_email}',
                'source': mail_ctx['source'],
            })
        except Exception as exc:
            if mail_ctx['instance']:
                mail_ctx['instance'].mark_test_result(False, str(exc))
            return Response({
                'success': False,
                'message': str(exc),
            }, status=status.HTTP_400_BAD_REQUEST)


def generate_dashboard_report_csv(dashboard):
    """
    Ancienne génération CSV – conservée pour debug éventuel.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['message'])
    writer.writerow(['Ce rapport est maintenant généré en PDF avec graphiques.'])
    return output.getvalue().encode('utf-8')


def generate_dashboard_report_pdf(dashboard: str) -> bytes:
    """
    Génère un PDF avec graphiques simplifiés pour le tableau de bord demandé.

    - 'dashboard'     : synthèse générale (financier + occupation + clients + opérationnel)
    - 'financier'     : CA, top zones, tendances
    - 'occupation'    : top zones par lots
    - 'clients'       : segmentation et risque clients
    - 'operationnel'  : performance collectes / attributions / facturation
    - 'alerts'        : répartition et historique des alertes
    - autres          : message générique
    """
    if not MATPLOTLIB_AVAILABLE:
        # Fallback très simple : PDF texte sans graph si matplotlib absent
        buffer = io.BytesIO()
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.pdfgen import canvas    # type: ignore

        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, f"Rapport SIGETI - {dashboard}")
        c.setFont("Helvetica", 12)
        c.drawString(72, height - 110, "Les graphiques détaillés nécessitent Matplotlib sur le serveur.")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        # Page 1 : Titre
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 portrait
        ax.axis('off')
        ax.text(
            0.5,
            0.8,
            f"Rapport SIGETI - Tableau de bord : {dashboard}",
            ha='center',
            fontsize=18,
            weight='bold',
        )
        ax.text(
            0.5,
            0.7,
            f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}",
            ha='center',
            fontsize=11,
        )
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2+ : contenu spécifique à chaque tableau
        if dashboard == 'dashboard':
            # Tableau de bord général : on assemble quelques KPIs clés
            from analytics.models import (
                MartPerformanceFinanciere,
                MartOccupationZones,
                MartKPIOperationnels,
            )

            # Helpers
            def _fmt_int(value: float) -> str:
                return f"{value:,.0f}".replace(",", " ")

            def _fmt_pct(value: float) -> str:
                return f"{value:.1f}%"

            # --- Bloc Financier (aligne avec les 4 cartes du dashboard) ---
            fin_summary = MartPerformanceFinanciere.objects.aggregate(
                ca_total=Sum('montant_total_facture'),
                ca_paye=Sum('montant_paye'),
                ca_impaye=Sum('montant_impaye'),
                taux_paiement_moyen=Avg('taux_paiement_pct'),
            )
            ca_total = float(fin_summary.get('ca_total') or 0)
            ca_paye = float(fin_summary.get('ca_paye') or 0)
            ca_impaye = float(fin_summary.get('ca_impaye') or 0)
            # Si le champ d'agrégat n'est pas fiable, on recalcule un taux global
            if ca_total:
                taux_paiement = (ca_paye / ca_total) * 100.0
            else:
                taux_paiement = float(fin_summary.get('taux_paiement_moyen') or 0)

            # --- Bloc Occupation des Zones ---
            occ_summary = MartOccupationZones.objects.aggregate(
                total_lots=Sum('nombre_total_lots'),
                lots_disponibles=Sum('lots_disponibles'),
                lots_attribues=Sum('lots_attribues'),
            )
            total_lots = float(occ_summary.get('total_lots') or 0)
            lots_disponibles = float(occ_summary.get('lots_disponibles') or 0)
            lots_attribues = float(occ_summary.get('lots_attribues') or 0)
            taux_occupation = (lots_attribues / total_lots * 100.0) if total_lots else 0.0

            # --- Bloc Opérationnel : on aligne sur les 4 cartes du dashboard ---
            # On évite d'agréger les champs de durée (timedelta) pour ne pas casser les agrégats.
            op_summary = MartKPIOperationnels.objects.aggregate(
                total_collectes=Sum('nombre_collectes'),
                total_demandes=Sum('nombre_demandes'),
                taux_approbation_moyen=Avg('taux_approbation_pct'),
                taux_recouvrement_global=Avg('taux_recouvrement_global_pct'),
            )
            total_collectes = float(op_summary.get('total_collectes') or 0)
            total_demandes = float(op_summary.get('total_demandes') or 0)
            taux_approbation = float(op_summary.get('taux_approbation_moyen') or 0)
            taux_recouvrement = float(op_summary.get('taux_recouvrement_global') or 0)

            # Page 2 : synthèse structurée comme le dashboard
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis('off')

            text_lines = [
                "Synthèse Générale SIGETI",
                "",
                "Performance Financière",
                f" - CA Facturé : {_fmt_int(ca_total)} FCFA",
                f" - CA Payé : {_fmt_int(ca_paye)} FCFA",
                f" - Créances : {_fmt_int(ca_impaye)} FCFA",
                f" - Taux de Paiement : {_fmt_pct(taux_paiement)}",
                "",
                "Occupation des Zones",
                f" - Total Lots : {_fmt_int(total_lots)}",
                f" - Lots Disponibles : {_fmt_int(lots_disponibles)}",
                f" - Lots Attribués : {_fmt_int(lots_attribues)}",
                f" - Taux d'Occupation : {_fmt_pct(taux_occupation)}",
                "",
                "Performance Opérationnelle",
                f" - Collectes : {_fmt_int(total_collectes)}",
                f" - Demandes : {_fmt_int(total_demandes)}",
                f" - Taux Approbation : {_fmt_pct(taux_approbation)}",
                f" - Taux Recouvrement : {_fmt_pct(taux_recouvrement)}",
            ]

            y = 0.85
            for line in text_lines:
                ax.text(0.1, y, line, fontsize=11, va='top')
                y -= 0.05

            pdf.savefig(fig)
            plt.close(fig)

        elif dashboard == 'financier':
            from analytics.models import MartPerformanceFinanciere

            summary = MartPerformanceFinanciere.objects.aggregate(
                total_factures=Sum('nombre_factures'),
                ca_total=Sum('montant_total_facture'),
                ca_paye=Sum('montant_paye'),
                ca_impaye=Sum('montant_impaye'),
                montant_recouvre=Sum('montant_total_recouvre'),
                montant_a_recouvrer=Sum('montant_total_a_recouvrer'),
                taux_recouvrement=Avg('taux_recouvrement_moyen'),
                collectes=Sum('nombre_collectes'),
            )

            ca_total = float(summary.get('ca_total') or 0)
            ca_paye = float(summary.get('ca_paye') or 0)
            ca_impaye = float(summary.get('ca_impaye') or 0)
            montant_recouvre = float(summary.get('montant_recouvre') or 0)
            montant_a_recouvrer = float(summary.get('montant_a_recouvrer') or 0)
            taux_recouvrement = float(summary.get('taux_recouvrement') or 0)
            total_factures = int(summary.get('total_factures') or 0)
            total_collectes = int(summary.get('collectes') or 0)

            def _fmt_currency_short(value: float) -> str:
                abs_v = abs(value)
                if abs_v >= 1_000_000_000:
                    return f"{value / 1_000_000_000:.1f} Md FCFA"
                if abs_v >= 1_000_000:
                    return f"{value / 1_000_000:.1f} M FCFA"
                if abs_v >= 1_000:
                    return f"{value / 1_000:.1f} K FCFA"
                return f"{value:,.0f} FCFA"

            # ---- Page 2 : Performance Financière et Analyse du Recouvrement (texte simple) ----
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

            # Titre principal
            ax.text(0.05, 0.95, "Performance Financière", fontsize=18, fontweight='bold', color='#111827', transform=ax.transAxes)
            ax.text(0.05, 0.90, "Vue d'ensemble des indicateurs clés", fontsize=10, color='#6B7280', transform=ax.transAxes)

            # Vue d'ensemble - affichage texte simple
            y_pos = 0.82
            overview_items = [
                ("CA Facturé", _fmt_currency_short(ca_total), f"{ca_total:,.0f} FCFA"),
                ("CA Payé", _fmt_currency_short(ca_paye), f"{ca_paye:,.0f} FCFA"),
                ("Créances", _fmt_currency_short(ca_impaye), f"{ca_impaye:,.0f} FCFA"),
                ("Nombre Factures", f"{total_factures}", "Factures émises"),
            ]
            for title, value, detail in overview_items:
                ax.text(0.05, y_pos, f"{title}: {value}", fontsize=11, fontweight='bold', color='#111827', transform=ax.transAxes)
                ax.text(0.05, y_pos - 0.04, detail, fontsize=9, color='#6B7280', transform=ax.transAxes)
                y_pos -= 0.10

            # Analyse du Recouvrement
            ax.text(0.05, 0.45, "Analyse du Recouvrement", fontsize=18, fontweight='bold', color='#111827', transform=ax.transAxes)
            ax.text(0.05, 0.40, "Focus sur les collectes et objectifs", fontsize=10, color='#6B7280', transform=ax.transAxes)

            y_pos = 0.32
            recovery_items = [
                ("Montant Recouvré", _fmt_currency_short(montant_recouvre), f"{total_collectes} collectes"),
                ("Taux de Recouvrement", f"{taux_recouvrement:.1f}%", "Sur créances totales"),
                ("Montant à Recouvrer", _fmt_currency_short(montant_a_recouvrer), "Objectif collectif"),
            ]
            for title, value, detail in recovery_items:
                ax.text(0.05, y_pos, f"{title}: {value}", fontsize=11, fontweight='bold', color='#111827', transform=ax.transAxes)
                ax.text(0.05, y_pos - 0.04, detail, fontsize=9, color='#6B7280', transform=ax.transAxes)
                y_pos -= 0.10

            fig.tight_layout(pad=1.0)
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 3 : Évolution mensuelle + Performance trimestrielle ----
            tendances_mois = (
                MartPerformanceFinanciere.objects
                .values('annee', 'mois')
                .annotate(
                    ca_facture=Sum('montant_total_facture'),
                    ca_paye=Sum('montant_paye'),
                )
                .order_by('annee', 'mois')
            )
            tendances_mois = list(tendances_mois)[-12:]
            mois_labels = [f"{t['mois']}/{t['annee']}" for t in tendances_mois]
            mois_ca = [float(t['ca_facture'] or 0) for t in tendances_mois]
            mois_paye = [float(t['ca_paye'] or 0) for t in tendances_mois]
            current_year = tendances_mois[-1]['annee'] if tendances_mois else timezone.now().year

            tendances_tri = (
                MartPerformanceFinanciere.objects
                .values('annee', 'trimestre')
                .annotate(
                    ca_facture=Sum('montant_total_facture'),
                    ca_paye=Sum('montant_paye'),
                    ca_impaye=Sum('montant_impaye'),
                )
                .order_by('annee', 'trimestre')
            )
            tendances_tri = list(tendances_tri)
            tri_labels = [f"T{t['trimestre']} {t['annee']}" for t in tendances_tri]
            tri_facture = [float(t['ca_facture'] or 0) for t in tendances_tri]
            tri_paye = [float(t['ca_paye'] or 0) for t in tendances_tri]
            tri_impaye = [float(t['ca_impaye'] or 0) for t in tendances_tri]

            fig, axes = plt.subplots(2, 1, figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')

            # Évolution mensuelle
            ax_month = axes[0]
            ax_month.set_facecolor('#F9FAFB')
            ax_month.fill_between(mois_labels, mois_ca, step='mid', alpha=0.2, color='#2563EB', label='CA facturé')
            ax_month.plot(mois_labels, mois_ca, marker='o', markersize=4, linewidth=1.5, color='#2563EB')
            ax_month.plot(mois_labels, mois_paye, marker='o', markersize=4, linewidth=1.5, color='#10B981', label='CA payé')
            ax_month.set_title(f"Évolution Mensuelle {current_year}", fontsize=16, fontweight='bold')
            ax_month.set_ylabel("Montant (FCFA)")
            ax_month.yaxis.grid(True, linestyle='--', alpha=0.4)
            ax_month.legend(loc='upper right', framealpha=0.9)  # Déplacé en haut à droite pour ne pas cacher les lignes
            plt.setp(ax_month.get_xticklabels(), rotation=45, ha='right')

            # Performance trimestrielle
            ax_tri = axes[1]
            ax_tri.set_facecolor('#F9FAFB')
            if tri_labels:
                x = range(len(tri_labels))
                width = 0.25
                bars1 = ax_tri.bar([i - width for i in x], tri_facture, width=width, label='CA facturé', color='#2563EB')
                bars2 = ax_tri.bar(x, tri_paye, width=width, label='CA payé', color='#10B981')
                bars3 = ax_tri.bar([i + width for i in x], tri_impaye, width=width, label='Créances', color='#F97316')
                for bars in (bars1, bars2, bars3):
                    for bar in bars:
                        height = bar.get_height()
                        if height <= 0:
                            continue
                        # Montant juste au-dessus de la barre (position d'origine)
                        ax_tri.text(
                            bar.get_x() + bar.get_width() / 2,
                            height,
                            f"{height:,.0f}",
                            ha='center',
                            va='bottom',
                            fontsize=8,
                        )
                ax_tri.set_xticks(list(x))
                ax_tri.set_xticklabels(tri_labels, rotation=45, ha='right')
            else:
                ax_tri.text(0.5, 0.5, "Aucune donnée trimestrielle disponible", ha='center', va='center')
            ax_tri.set_title("Performance Trimestrielle", fontsize=16, fontweight='bold')
            ax_tri.set_ylabel("Montant (FCFA)")
            ax_tri.yaxis.grid(True, linestyle='--', alpha=0.4)
            # Légende en bas à droite pour ne pas masquer les montants
            ax_tri.legend(loc='lower right', framealpha=0.9)

            fig.tight_layout(pad=2.0)
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 4 : Top zones / Meilleurs payeurs / Zones à risque ----
            qs_zones = list(
                MartPerformanceFinanciere.objects
                .values('nom_zone')
                .annotate(
                    ca_total=Sum('montant_total_facture'),
                    ca_paye=Sum('montant_paye'),
                    ca_impaye=Sum('montant_impaye'),
                )
                .exclude(nom_zone__isnull=True)
            )

            # Part de CA par zone (pour l'affichage "CA: 45.2%")
            total_ca_zones = sum(float(z['ca_total'] or 0) for z in qs_zones) or 1.0
            for z in qs_zones:
                ca_val = float(z['ca_total'] or 0)
                z['ca_share_pct'] = (ca_val / total_ca_zones * 100.0) if total_ca_zones else 0.0

            def _taux_paiement(item):
                ca_tot = float(item['ca_total'] or 0)
                ca_pay = float(item['ca_paye'] or 0)
                return (ca_pay / ca_tot * 100) if ca_tot else 0.0

            top_ca = sorted(qs_zones, key=lambda x: float(x['ca_total'] or 0), reverse=True)[:3]
            top_payeurs = sorted(qs_zones, key=_taux_paiement, reverse=True)[:3]
            zones_risque_all = [z for z in qs_zones if _taux_paiement(z) < 70]
            zones_risque = sorted(zones_risque_all, key=_taux_paiement)[:3]

            # ---- Page 4 : tableau unique récapitulatif des zones ----
            # Colonnes : Catégorie | Rang | Zone | CA | Part CA | Taux Paiement
            combined_rows: list[list[str]] = []

            # Top Zones par CA
            for idx, e in enumerate(top_ca[:3], start=1):
                zone = e['nom_zone'] or ''
                ca_val = _fmt_currency_short(float(e['ca_total'] or 0))
                part = f"{float(e.get('ca_share_pct', 0.0)):.1f}%"
                taux = f"{_taux_paiement(e):.1f}%"
                combined_rows.append(["Top CA", str(idx), zone, ca_val, part, taux])

            # Meilleurs payeurs
            for idx, e in enumerate(top_payeurs[:3], start=1):
                zone = e['nom_zone'] or ''
                ca_val = _fmt_currency_short(float(e['ca_total'] or 0))
                part = f"{float(e.get('ca_share_pct', 0.0)):.1f}%"
                taux = f"{_taux_paiement(e):.1f}%"
                combined_rows.append(["Meilleur payeur", str(idx), zone, ca_val, part, taux])

            # Zones à risque
            for idx, e in enumerate(zones_risque[:3], start=1):
                zone = e['nom_zone'] or ''
                ca_val = _fmt_currency_short(float(e['ca_total'] or 0))
                part = f"{float(e.get('ca_share_pct', 0.0)):.1f}%"
                taux = f"{_taux_paiement(e):.1f}%"
                combined_rows.append(["Zone à risque", str(idx), zone, ca_val, part, taux])

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')
            ax.axis('off')

            if combined_rows:
                table = ax.table(
                    cellText=combined_rows,
                    colLabels=["Catégorie", "#", "Zone", "CA", "Part CA", "Taux paiement"],
                    loc='center',
                    cellLoc='left',
                )
                table.auto_set_font_size(False)
                table.set_fontsize(9)
                table.scale(1.2, 2.2)  # Augmenter l'espacement horizontal et vertical
                
                # Ajuster les largeurs de colonnes pour donner plus d'espace à "Zone"
                num_rows = len(combined_rows) + 1  # +1 pour l'en-tête
                num_cols = len(combined_rows[0]) if combined_rows else 6
                
                # Largeurs relatives des colonnes (somme = 1.0)
                col_widths = [0.12, 0.04, 0.40, 0.15, 0.12, 0.17]  # Zone = 40%
                
                for row in range(num_rows):
                    for col in range(num_cols):
                        cell = table[(row, col)]
                        # Ajuster la largeur de la cellule
                        cell.set_width(col_widths[col])
                        
                        if row == 0:  # Ligne d'en-tête
                            cell.set_text_props(weight='bold', fontsize=10)
                        else:
                            # Police plus grande pour la colonne Zone
                            if col == 2:  # Colonne "Zone"
                                cell.set_text_props(fontsize=10)
                            else:
                                cell.set_text_props(fontsize=9)
                
                ax.set_title("Synthèse Zones (CA, payeurs, risques)", fontsize=14, fontweight='bold', pad=12)
            else:
                ax.text(
                    0.5,
                    0.5,
                    "Aucune donnée de zone disponible",
                    ha='center',
                    va='center',
                    fontsize=11,
                )

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        elif dashboard == 'occupation':
            from analytics.models import MartOccupationZones

            # ---- Page 2 : KPIs Principaux - Vue d'Ensemble ----
            summary = MartOccupationZones.objects.aggregate(
                nombre_zones=Count('zone_id', distinct=True),
                total_lots=Sum('nombre_total_lots'),
                lots_attribues=Sum('lots_attribues'),
                lots_disponibles=Sum('lots_disponibles'),
                lots_reserves=Sum('lots_reserves'),
                superficie_totale=Sum('superficie_totale'),
                superficie_attribuee=Sum('superficie_attribuee'),
                superficie_disponible=Sum('superficie_disponible'),
            )
            
            # Calcul du taux d'occupation moyen
            total_lots = float(summary.get('total_lots') or 0)
            lots_attribues = float(summary.get('lots_attribues') or 0)
            taux_occupation_moyen = (lots_attribues / total_lots * 100) if total_lots > 0 else 0.0

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis('off')
            
            # Titre
            ax.text(0.5, 0.95, "Vue d'Ensemble - Occupation des Zones", 
                   ha='center', fontsize=18, weight='bold', transform=ax.transAxes)
            
            # KPIs en grille
            y_pos = 0.80
            kpis = [
                ('Zones Industrielles', summary.get('nombre_zones', 0), 'zones actives'),
                ('Total Lots', summary.get('total_lots', 0), 'capacité totale'),
                ('Lots Attribués', summary.get('lots_attribues', 0), f'{taux_occupation_moyen:.1f}% occupés'),
                ('Lots Disponibles', summary.get('lots_disponibles', 0), 'prêts à l\'attribution'),
            ]
            
            for i, (title, value, subtitle) in enumerate(kpis):
                x_pos = 0.25 if i % 2 == 0 else 0.75
                if i >= 2:
                    y_pos = 0.50
                
                ax.text(x_pos, y_pos, title, ha='center', fontsize=14, weight='bold', 
                       transform=ax.transAxes)
                ax.text(x_pos, y_pos - 0.05, f"{value:,.0f}", ha='center', fontsize=20, 
                       color='#2563EB', weight='bold', transform=ax.transAxes)
                ax.text(x_pos, y_pos - 0.10, subtitle, ha='center', fontsize=10, 
                       style='italic', color='gray', transform=ax.transAxes)
            
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 3 : Statistiques de Surface ----
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis('off')
            
            ax.text(0.5, 0.95, "Statistiques de Surface", 
                   ha='center', fontsize=18, weight='bold', transform=ax.transAxes)
            
            surfaces = [
                ('Superficie Totale', summary.get('superficie_totale', 0), 'm²', 'surface industrielle'),
                ('Surface Attribuée', summary.get('superficie_attribuee', 0), 'm²', 'en exploitation'),
                ('Surface Disponible', summary.get('superficie_disponible', 0), 'm²', 'disponible'),
            ]
            
            y_start = 0.75
            for i, (title, value, unit, subtitle) in enumerate(surfaces):
                y_pos = y_start - (i * 0.20)
                ax.text(0.5, y_pos, title, ha='center', fontsize=14, weight='bold', 
                       transform=ax.transAxes)
                ax.text(0.5, y_pos - 0.05, f"{float(value or 0):,.0f} {unit}", 
                       ha='center', fontsize=18, color='#10B981', weight='bold', transform=ax.transAxes)
                ax.text(0.5, y_pos - 0.10, subtitle, ha='center', fontsize=10, 
                       style='italic', color='gray', transform=ax.transAxes)
            
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 4 : Alertes d'Occupation ----
            # Calculer zones saturées (>90%) et sous-occupées (<50%)
            all_zones = MartOccupationZones.objects.all()
            zones_saturees = 0
            zones_faible_occupation = 0
            
            for zone in all_zones:
                taux = float(zone.taux_occupation_pct or 0)
                if taux >= 90:
                    zones_saturees += 1
                elif taux < 50:
                    zones_faible_occupation += 1

            fig, axes = plt.subplots(2, 1, figsize=(8.27, 11.69))
            
            # Taux d'occupation moyen (jauge)
            axes[0].axis('off')
            axes[0].text(0.5, 0.8, "Taux d'Occupation Moyen", 
                        ha='center', fontsize=16, weight='bold', transform=axes[0].transAxes)
            axes[0].text(0.5, 0.5, f"{taux_occupation_moyen:.1f}%", 
                        ha='center', fontsize=48, weight='bold', 
                        color='#2563EB' if taux_occupation_moyen < 50 else 
                              '#F59E0B' if taux_occupation_moyen < 70 else 
                              '#10B981' if taux_occupation_moyen < 90 else '#EF4444',
                        transform=axes[0].transAxes)
            
            # Zones saturées et sous-occupées
            axes[1].axis('off')
            axes[1].text(0.5, 0.9, "Alertes d'Occupation", 
                        ha='center', fontsize=16, weight='bold', transform=axes[1].transAxes)
            
            alertes_data = [
                ('Zones Saturées', zones_saturees, 'Occupation > 90%', '#EF4444'),
                ('Zones Sous-Occupées', zones_faible_occupation, 'Occupation < 50%', '#3B82F6'),
            ]
            
            y_pos = 0.65
            for title, value, subtitle, color in alertes_data:
                axes[1].text(0.5, y_pos, title, ha='center', fontsize=14, weight='bold', 
                            transform=axes[1].transAxes)
                axes[1].text(0.5, y_pos - 0.08, f"{value}", ha='center', fontsize=32, 
                            weight='bold', color=color, transform=axes[1].transAxes)
                axes[1].text(0.5, y_pos - 0.15, subtitle, ha='center', fontsize=10, 
                            style='italic', color='gray', transform=axes[1].transAxes)
                y_pos -= 0.30
            
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 5 : Top Zones par Nombre de Lots (graphique amélioré) ----
            rows = (
                MartOccupationZones.objects
                .values('nom_zone')
                .annotate(total=Sum('nombre_total_lots'))
                .order_by('-total')[:10]
            )

            if rows:
                labels = [r['nom_zone'] for r in rows]
                values = [float(r['total'] or 0) for r in rows]

                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                fig.patch.set_facecolor("white")
                ax.set_facecolor("#F9FAFB")

                ax.barh(labels, values, color='#2196F3')
                ax.invert_yaxis()  # la zone avec le plus de lots en haut
                ax.set_title("Top 10 Zones par Nombre Total de Lots", fontsize=16, fontweight='bold')
                ax.set_xlabel("Nombre de lots", fontsize=12)
                ax.xaxis.grid(True, linestyle='--', alpha=0.4)

                for i, v in enumerate(values):
                    ax.text(v, i, f"{v:,.0f}", va='center', ha='left', fontsize=9, fontweight='bold')

                fig.tight_layout(pad=2.0)
                pdf.savefig(fig)
                plt.close(fig)

            # ---- Page 6 : Zones les Plus Occupées ----
            zones_plus_occupees = (
                MartOccupationZones.objects
                .exclude(taux_occupation_pct__isnull=True)
                .order_by('-taux_occupation_pct')[:5]
            )

            if zones_plus_occupees:
                labels = [z.nom_zone for z in zones_plus_occupees]
                values = [float(z.taux_occupation_pct or 0) for z in zones_plus_occupees]

                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                fig.patch.set_facecolor("white")
                ax.set_facecolor("#F9FAFB")

                colors = ['#EF4444' if v >= 90 else '#F59E0B' if v >= 70 else '#10B981' for v in values]
                ax.barh(labels, values, color=colors)
                ax.invert_yaxis()
                ax.set_title("Top 5 Zones les Plus Occupées", fontsize=16, fontweight='bold')
                ax.set_xlabel("Taux d'occupation (%)", fontsize=12)
                ax.set_xlim(0, 100)
                ax.xaxis.grid(True, linestyle='--', alpha=0.4)

                for i, v in enumerate(values):
                    ax.text(v, i, f"{v:.1f}%", va='center', ha='left', fontsize=10, fontweight='bold')

                fig.tight_layout(pad=2.0)
                pdf.savefig(fig)
                plt.close(fig)

            # ---- Page 7 : Zones les Moins Occupées ----
            zones_moins_occupees = (
                MartOccupationZones.objects
                .exclude(taux_occupation_pct__isnull=True)
                .order_by('taux_occupation_pct')[:5]
            )

            if zones_moins_occupees:
                labels = [z.nom_zone for z in zones_moins_occupees]
                values = [float(z.taux_occupation_pct or 0) for z in zones_moins_occupees]

                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                fig.patch.set_facecolor("white")
                ax.set_facecolor("#F9FAFB")

                colors = ['#3B82F6' if v < 50 else '#10B981' if v < 70 else '#F59E0B' for v in values]
                ax.barh(labels, values, color=colors)
                ax.invert_yaxis()
                ax.set_title("Top 5 Zones les Moins Occupées", fontsize=16, fontweight='bold')
                ax.set_xlabel("Taux d'occupation (%)", fontsize=12)
                ax.set_xlim(0, 100)
                ax.xaxis.grid(True, linestyle='--', alpha=0.4)

                for i, v in enumerate(values):
                    ax.text(v, i, f"{v:.1f}%", va='center', ha='left', fontsize=10, fontweight='bold')

                fig.tight_layout(pad=2.0)
                pdf.savefig(fig)
                plt.close(fig)

            # ---- Page 8+ : Tableau Détaillé des Zones (par pages de 15 zones) ----
            all_zones_detailed = (
                MartOccupationZones.objects
                .order_by('nom_zone')
                .values('nom_zone', 'taux_occupation_pct', 'nombre_total_lots', 
                       'lots_attribues', 'lots_disponibles', 'lots_reserves', 
                       'superficie_totale')
            )
            
            zones_list = list(all_zones_detailed)
            zones_per_page = 15
            
            for page_idx in range(0, len(zones_list), zones_per_page):
                page_zones = zones_list[page_idx:page_idx + zones_per_page]
                
                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                ax.axis('off')
                
                # Titre
                ax.text(0.5, 0.98, f"Détails par Zone - Page {page_idx // zones_per_page + 1}", 
                       ha='center', fontsize=16, weight='bold', transform=ax.transAxes)
                
                # En-têtes du tableau
                headers = ['Zone', 'Taux Occ.', 'Lots Total', 'Attribués', 'Disponibles', 'Réservés', 'Superficie (m²)']
                col_widths = [0.20, 0.12, 0.10, 0.10, 0.12, 0.10, 0.15]
                x_positions = [0.05]
                for i in range(1, len(headers)):
                    x_positions.append(x_positions[i-1] + col_widths[i-1] + 0.02)
                
                y_start = 0.92
                # En-têtes
                for i, (header, x_pos) in enumerate(zip(headers, x_positions)):
                    ax.text(x_pos, y_start, header, ha='left', fontsize=9, weight='bold', 
                           transform=ax.transAxes)
                
                # Lignes de données
                y_pos = y_start - 0.05
                for zone in page_zones:
                    if y_pos < 0.05:  # Nouvelle page si nécessaire
                        pdf.savefig(fig)
                        plt.close(fig)
                        fig, ax = plt.subplots(figsize=(8.27, 11.69))
                        ax.axis('off')
                        y_pos = 0.92
                    
                    nom = zone['nom_zone'] or 'N/A'
                    taux = float(zone['taux_occupation_pct'] or 0)
                    total = int(zone['nombre_total_lots'] or 0)
                    attribues = int(zone['lots_attribues'] or 0)
                    disponibles = int(zone['lots_disponibles'] or 0)
                    reserves = int(zone['lots_reserves'] or 0)
                    superficie = float(zone['superficie_totale'] or 0)
                    
                    row_data = [
                        nom[:20],  # Tronquer si trop long
                        f"{taux:.1f}%",
                        f"{total}",
                        f"{attribues}",
                        f"{disponibles}",
                        f"{reserves}",
                        f"{superficie:,.0f}" if superficie > 0 else "N/A"
                    ]
                    
                    for i, (data, x_pos) in enumerate(zip(row_data, x_positions)):
                        ax.text(x_pos, y_pos, str(data), ha='left', fontsize=8, 
                               transform=ax.transAxes)
                    
                    y_pos -= 0.055
                
                pdf.savefig(fig)
                plt.close(fig)

        elif dashboard == 'clients':
            from analytics.models import MartPortefeuilleClients

            # Agrégation des KPIs principaux
            summary = MartPortefeuilleClients.objects.aggregate(
                total_clients=Count('entreprise_id', distinct=True),
                creances_totales=Sum('ca_impaye'),
                ca_total=Sum('chiffre_affaires_total'),
                factures_retard=Sum('nombre_factures_retard'),
                delai_moyen=Avg('delai_moyen_paiement'),
            )

            total_clients = int(summary.get('total_clients') or 0)
            creances_totales = float(summary.get('creances_totales') or 0)
            ca_total = float(summary.get('ca_total') or 0)
            factures_retard = int(summary.get('factures_retard') or 0)
            
            # Calcul du délai moyen en jours (si DurationField)
            delai_moyen_jours = 0
            if summary.get('delai_moyen'):
                try:
                    delai_moyen_jours = int(summary['delai_moyen'].total_seconds() / 86400)
                except:
                    delai_moyen_jours = 0

            def _fmt_currency_short(value: float) -> str:
                abs_v = abs(value)
                if abs_v >= 1_000_000_000:
                    return f"{value / 1_000_000_000:.1f} Md FCFA"
                if abs_v >= 1_000_000:
                    return f"{value / 1_000_000:.1f} M FCFA"
                if abs_v >= 1_000:
                    return f"{value / 1_000:.1f} K FCFA"
                return f"{value:,.0f} FCFA"

            # ---- Page 2 : Vue d'Ensemble du Portefeuille (texte simple) ----
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

            ax.text(0.05, 0.95, "Vue d'Ensemble du Portefeuille", fontsize=18, fontweight='bold', color='#111827', transform=ax.transAxes)

            y_pos = 0.85
            kpi_items = [
                ("Total Clients", f"{total_clients}", "Entreprises actives"),
                ("Créances Totales", _fmt_currency_short(creances_totales), f"{(creances_totales/ca_total*100) if ca_total else 0:.1f}% du CA"),
                ("Délai Moyen Paiement", f"{delai_moyen_jours} jours", "Moyenne par client"),
                ("Factures en Retard", f"{factures_retard}", "À relancer"),
            ]
            for title, value, detail in kpi_items:
                ax.text(0.05, y_pos, f"{title}: {value}", fontsize=11, fontweight='bold', color='#111827', transform=ax.transAxes)
                ax.text(0.05, y_pos - 0.04, detail, fontsize=9, color='#6B7280', transform=ax.transAxes)
                y_pos -= 0.10

            fig.tight_layout(pad=1.0)
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 3 : Segmentation du Portefeuille (avec détails) ----
            seg_qs = (
                MartPortefeuilleClients.objects
                .values('segment_client')
                .annotate(
                    nb=Count('entreprise_id'),
                    ca_total=Sum('chiffre_affaires_total'),
                )
                .order_by('-ca_total')
            )

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')
            ax.axis('off')

            ax.text(0.5, 0.95, "Segmentation du Portefeuille", fontsize=16, fontweight='bold', ha='center', transform=ax.transAxes)

            if seg_qs:
                # Graphique camembert
                ax_pie = fig.add_axes([0.25, 0.5, 0.5, 0.4])
                labels_seg = [row['segment_client'] or 'Non défini' for row in seg_qs]
                sizes_seg = [float(row['ca_total'] or 0) for row in seg_qs]
                colors = ['#2563EB', '#10B981', '#F97316', '#9333EA', '#EF4444']
                wedges, texts, autotexts = ax_pie.pie(
                    sizes_seg,
                    labels=labels_seg,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors[:len(sizes_seg)],
                )
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')

                # Légende détaillée sous le graphique
                y_leg = 0.40
                for idx, row in enumerate(seg_qs):
                    segment = row['segment_client'] or 'Non défini'
                    nb = int(row['nb'] or 0)
                    ca = float(row['ca_total'] or 0)
                    desc = f"{nb} client{'s' if nb > 1 else ''} {'> 100 M' if 'Grand' in segment or 'grand' in segment else '< 100 M' if 'Moyen' in segment or 'moyen' in segment else '< 10 M' if 'Petit' in segment or 'petit' in segment else ''}"
                    ax.text(0.1, y_leg, f"{segment}:", fontsize=11, fontweight='bold', transform=ax.transAxes)
                    ax.text(0.1, y_leg - 0.04, f"  {desc}, valeur: {_fmt_currency_short(ca)}", fontsize=10, color='#6B7280', transform=ax.transAxes)
                    y_leg -= 0.10
            else:
                ax.text(0.5, 0.5, "Aucune donnée de segmentation", ha='center', va='center', transform=ax.transAxes)

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 4 : Répartition par Niveau de Risque (avec détails) ----
            risk_qs = (
                MartPortefeuilleClients.objects
                .values('niveau_risque')
                .annotate(
                    nb_clients=Count('entreprise_id'),
                    ca_total=Sum('chiffre_affaires_total'),
                    creances=Sum('ca_impaye'),
                )
                .exclude(niveau_risque__isnull=True)
            )

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')

            if risk_qs:
                labels_risk = [row['niveau_risque'] or 'Non défini' for row in risk_qs]
                values_risk = [int(row['nb_clients'] or 0) for row in risk_qs]
                
                ax.barh(labels_risk, values_risk, color='#2563EB')
                ax.set_title("Répartition par Niveau de Risque", fontsize=16, fontweight='bold')
                ax.set_xlabel("Nombre de clients", fontsize=12)
                ax.xaxis.grid(True, linestyle='--', alpha=0.4)
                ax.invert_yaxis()
                
                for i, (v, row) in enumerate(zip(values_risk, risk_qs)):
                    ax.text(v, i, str(v), va='center', ha='left', fontsize=10, fontweight='bold')
                    # Détails sous chaque barre
                    ca_val = float(row['ca_total'] or 0)
                    creances_val = float(row['creances'] or 0)
                    ax.text(
                        ax.get_xlim()[1] * 0.6,
                        i,
                        f"CA: {_fmt_currency_short(ca_val)}, Créances: {_fmt_currency_short(creances_val)}",
                        va='center',
                        fontsize=9,
                        color='#6B7280',
                    )
            else:
                ax.text(0.5, 0.5, "Aucune donnée de risque", ha='center', va='center')
                ax.axis('off')

            fig.tight_layout(pad=2.0)
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 5 : Top Clients par CA (tableau détaillé) ----
            top_clients = (
                MartPortefeuilleClients.objects
                .order_by('-chiffre_affaires_total')[:10]
            )

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')
            ax.axis('off')

            ax.text(0.5, 0.95, "Top Clients par CA", fontsize=16, fontweight='bold', ha='center', transform=ax.transAxes)

            if top_clients:
                top_rows = []
                for idx, client in enumerate(top_clients, start=1):
                    raison = (client.raison_sociale or '')[:50]
                    ca = _fmt_currency_short(float(client.chiffre_affaires_total or 0))
                    ca_full = f"{float(client.chiffre_affaires_total or 0):,.0f} FCFA"
                    taux = f"{float(client.taux_paiement_pct or 0):.1f}%"
                    top_rows.append([str(idx), raison, ca, ca_full, taux])

                table1 = ax.table(
                    cellText=top_rows,
                    colLabels=["#", "CLIENT", "CA TOTAL", "CA (détail)", "TAUX PAIEMENT"],
                    loc='center',
                    cellLoc='left',
                )
                table1.auto_set_font_size(False)
                table1.set_fontsize(9)
                table1.scale(1.0, 1.8)
                
                # Mettre en gras les en-têtes
                num_rows = len(top_rows) + 1
                num_cols = 5
                for row in range(num_rows):
                    for col in range(num_cols):
                        cell = table1[(row, col)]
                        if row == 0:
                            cell.set_text_props(weight='bold', fontsize=10)
                        else:
                            if col == 1:  # Colonne CLIENT
                                cell.set_text_props(fontsize=9)
                            else:
                                cell.set_text_props(fontsize=9)
            else:
                ax.text(0.5, 0.5, "Aucun client disponible", ha='center', va='center', transform=ax.transAxes)

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 6 : Clients à Risque (tableau détaillé) ----
            clients_risque = (
                MartPortefeuilleClients.objects
                .filter(taux_paiement_pct__lt=70)
                .order_by('taux_paiement_pct')[:10]
            )

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')
            ax.axis('off')

            ax.text(0.5, 0.95, "Clients à Risque", fontsize=16, fontweight='bold', ha='center', transform=ax.transAxes)

            if clients_risque:
                risk_rows = []
                for idx, client in enumerate(clients_risque, start=1):
                    raison = (client.raison_sociale or '')[:50]
                    creances = _fmt_currency_short(float(client.ca_impaye or 0))
                    creances_full = f"{float(client.ca_impaye or 0):,.0f} FCFA"
                    taux = f"{float(client.taux_paiement_pct or 0):.1f}%"
                    risk_rows.append([str(idx), raison, creances, creances_full, taux])

                table2 = ax.table(
                    cellText=risk_rows,
                    colLabels=["#", "CLIENT", "CRÉANCES", "CRÉANCES (détail)", "TAUX PAIEMENT"],
                    loc='center',
                    cellLoc='left',
                )
                table2.auto_set_font_size(False)
                table2.set_fontsize(9)
                table2.scale(1.0, 1.8)
                
                # Mettre en gras les en-têtes
                num_rows = len(risk_rows) + 1
                num_cols = 5
                for row in range(num_rows):
                    for col in range(num_cols):
                        cell = table2[(row, col)]
                        if row == 0:
                            cell.set_text_props(weight='bold', fontsize=10)
                        else:
                            if col == 1:  # Colonne CLIENT
                                cell.set_text_props(fontsize=9)
                            else:
                                cell.set_text_props(fontsize=9)
            else:
                ax.text(0.5, 0.5, "Aucun client à risque", ha='center', va='center', transform=ax.transAxes)

            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 7 : Analyse de l'Occupation des Lots Industriels ----
            clients_avec_lots = MartPortefeuilleClients.objects.filter(nombre_lots_attribues__gt=0)
            clients_sans_lots = MartPortefeuilleClients.objects.filter(nombre_lots_attribues=0)

            nb_avec_lots = clients_avec_lots.count()
            nb_sans_lots = clients_sans_lots.count()
            superficie_totale = float(clients_avec_lots.aggregate(Sum('superficie_totale_attribuee')).get('superficie_totale_attribuee__sum') or 0)
            ca_moyen_avec_lots = float(clients_avec_lots.aggregate(avg=Avg('chiffre_affaires_total')).get('avg') or 0)
            ca_moyen_sans_lots = float(clients_sans_lots.aggregate(avg=Avg('chiffre_affaires_total')).get('avg') or 0)

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

            ax.text(0.05, 0.95, "Analyse de l'Occupation des Lots Industriels", fontsize=16, fontweight='bold', color='#111827', transform=ax.transAxes)
            
            y_occ = 0.82
            occ_items = [
                (f"{nb_avec_lots}", "Clients avec Lots", f"1 Lots > {superficie_totale:,.0f} m²"),
                (f"{nb_sans_lots}", "Clients sans Lots", "Prospects potentiels"),
                (_fmt_currency_short(ca_moyen_avec_lots), "CA Moyen (avec lots)", "Par client occupant"),
                (_fmt_currency_short(ca_moyen_sans_lots), "CA Moyen (sans lots)", "Par client non-occupant"),
            ]
            for value, title, detail in occ_items:
                ax.text(0.05, y_occ, f"{title}: {value}", fontsize=12, fontweight='bold', color='#111827', transform=ax.transAxes)
                ax.text(0.05, y_occ - 0.05, detail, fontsize=10, color='#6B7280', transform=ax.transAxes)
                y_occ -= 0.15

            fig.tight_layout(pad=1.0)
            pdf.savefig(fig)
            plt.close(fig)

            # ---- Page 8 : Top Secteurs d'Activité ----
            secteurs_qs = (
                MartPortefeuilleClients.objects
                .values('secteur_activite')
                .annotate(
                    nb_clients=Count('entreprise_id'),
                    ca_total=Sum('chiffre_affaires_total'),
                )
                .exclude(secteur_activite__isnull=True)
                .order_by('-ca_total')[:10]
            )

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('white')

            if secteurs_qs:
                secteurs = [row['secteur_activite'] or 'Non défini' for row in secteurs_qs]
                nb_clients = [int(row['nb_clients'] or 0) for row in secteurs_qs]
                ca_tot = [float(row['ca_total'] or 0) for row in secteurs_qs]

                # Normaliser les valeurs pour l'affichage (CA en millions pour la cohérence)
                ca_tot_norm = [c / 1_000_000 for c in ca_tot]  # Convertir en millions

                y = range(len(secteurs))
                height = 0.35
                bars1 = ax.barh([i - height/2 for i in y], nb_clients, height=height, label='Nombre de clients', color='#2563EB')
                bars2 = ax.barh([i + height/2 for i in y], ca_tot_norm, height=height, label='CA Total (M FCFA)', color='#10B981')
                
                ax.set_yticks(list(y))
                ax.set_yticklabels(secteurs, fontsize=9)
                ax.set_xlabel("Valeur", fontsize=12)
                ax.set_title("Top Secteurs d'Activité", fontsize=16, fontweight='bold')
                ax.legend(loc='lower right', framealpha=0.9, fontsize=10)
                ax.xaxis.grid(True, linestyle='--', alpha=0.4)
                
                # Ajouter les valeurs sur les barres
                for i, (nb, ca) in enumerate(zip(nb_clients, ca_tot_norm)):
                    if nb > 0:
                        ax.text(nb, i - height/2, str(nb), va='center', ha='left', fontsize=8)
                    if ca > 0:
                        ax.text(ca, i + height/2, f"{ca:.1f}M", va='center', ha='left', fontsize=8)
            else:
                ax.text(0.5, 0.5, "Aucune donnée de secteur disponible", ha='center', va='center')
                ax.axis('off')

            fig.tight_layout(pad=2.0)
            pdf.savefig(fig)
            plt.close(fig)

        elif dashboard == 'operationnel':
            from analytics.models import MartKPIOperationnels

            # Page 2 : performance trimestrielle (collectes + recouvrement)
            rows = (
                MartKPIOperationnels.objects
                .values('annee', 'trimestre')
                .annotate(
                    total_collectes=Sum('nombre_collectes'),
                    taux_recouvrement=Sum('taux_recouvrement_global_pct'),
                )
                .order_by('annee', 'trimestre')
            )

            if rows:
                labels = [f"T{r['trimestre']} {r['annee']}" for r in rows]
                collectes = [float(r['total_collectes'] or 0) for r in rows]
                taux = [float(r['taux_recouvrement'] or 0) for r in rows]

                fig, ax1 = plt.subplots(figsize=(8.27, 11.69))
                ax2 = ax1.twinx()

                x = range(len(labels))
                ax1.bar(x, collectes, color='#2563EB', alpha=0.7, label='Collectes')
                ax2.plot(x, taux, color='#16A34A', marker='o', label='Taux de recouvrement (%)')

                ax1.set_xticks(list(x))
                ax1.set_xticklabels(labels, rotation=45, ha='right')
                ax1.set_ylabel("Nombre de collectes")
                ax2.set_ylabel("Taux (%)")
                ax1.set_title("Performance opérationnelle par trimestre")

                lines, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines + lines2, labels1 + labels2, loc='upper left')

                fig.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)

        elif dashboard == 'alerts':
            from analytics.models import Alert

            # Page 2 : répartition des alertes par sévérité
            severities = ['critical', 'high', 'medium', 'low']
            labels = ['Critique', 'Élevé', 'Moyen', 'Faible']
            counts = [Alert.objects.filter(severity=sev).count() for sev in severities]

            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.bar(labels, counts, color=['#EF4444', '#F97316', '#EAB308', '#3B82F6'])
            ax.set_title("Répartition des alertes par sévérité")
            ax.set_ylabel("Nombre d'alertes")
            for i, v in enumerate(counts):
                ax.text(i, v, str(v), ha='center', va='bottom')
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        else:
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis('off')
            ax.text(
                0.5,
                0.5,
                "Ce type de rapport n'est pas encore implémenté en PDF.\n"
                "Veuillez choisir le tableau de bord 'financier' ou 'occupation'.",
                ha='center',
                va='center',
                fontsize=12,
            )
            pdf.savefig(fig)    
            plt.close(fig)

    buffer.seek(0)
    return buffer.getvalue()


def generate_multiple_dashboards_report_pdf(dashboards: list) -> bytes:
    """
    Génère un PDF combiné pour plusieurs dashboards.
    Chaque dashboard est inclus dans le PDF avec ses propres pages.
    
    Args:
        dashboards: Liste des noms de dashboards à inclure
        
    Returns:
        bytes: PDF combiné contenant tous les dashboards
    """
    if not dashboards or len(dashboards) == 0:
        raise ValueError("Au moins un dashboard doit être fourni")
    
    # Si un seul dashboard, on utilise la fonction existante
    if len(dashboards) == 1:
        return generate_dashboard_report_pdf(dashboards[0])
    
    if not MATPLOTLIB_AVAILABLE:
        # Fallback simple
        buffer = io.BytesIO()
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, f"Rapport SIGETI - {', '.join(dashboards)}")
        c.setFont("Helvetica", 12)
        c.drawString(72, height - 110, "Les graphiques détaillés nécessitent Matplotlib sur le serveur.")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    # Combiner les PDFs de chaque dashboard
    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        # Page de titre globale
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis('off')
        
        # Titre principal
        ax.text(
            0.5,
            0.85,
            "Rapport SIGETI - Tableaux de bord combinés",
            ha='center',
            fontsize=18,
            weight='bold',
        )
        
        # Liste des dashboards inclus
        dashboard_labels = {
            'dashboard': 'Tableau de bord',
            'financier': 'Performance Financière',
            'occupation': 'Occupation Zones',
            'clients': 'Portefeuille Clients',
            'operationnel': 'KPI Opérationnels',
            'alerts': 'Alerts Analytics',
        }
        
        dashboards_text = "\n".join([f"  • {dashboard_labels.get(d, d)}" for d in dashboards])
        ax.text(
            0.5,
            0.65,
            "Dashboards inclus:\n" + dashboards_text,
            ha='center',
            fontsize=12,
            va='top',
        )
        
        ax.text(
            0.5,
            0.3,
            f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}",
            ha='center',
            fontsize=11,
        )
        
        pdf.savefig(fig)
        plt.close(fig)
    
    # Maintenant, on combine les PDFs générés
    try:
        from PyPDF2 import PdfReader, PdfWriter
        
        # Créer un writer pour le PDF final
        writer = PdfWriter()
        
        # Ajouter la page de titre qu'on vient de créer
        buffer.seek(0)
        title_reader = PdfReader(buffer)
        for page in title_reader.pages:
            writer.add_page(page)
        
        # Ajouter les pages de chaque dashboard (sauf la première page de titre de chaque dashboard)
        for dashboard in dashboards:
            dashboard_pdf_bytes = generate_dashboard_report_pdf(dashboard)
            dashboard_buffer = io.BytesIO(dashboard_pdf_bytes)
            dashboard_reader = PdfReader(dashboard_buffer)
            
            # Ajouter toutes les pages du dashboard
            for page in dashboard_reader.pages:
                writer.add_page(page)
        
        # Écrire le PDF final
        final_buffer = io.BytesIO()
        writer.write(final_buffer)
        final_buffer.seek(0)
        return final_buffer.getvalue()
        
    except ImportError:
        # Si PyPDF2 n'est pas disponible, on génère simplement le premier dashboard
        # avec une note indiquant que plusieurs dashboards ont été demandés
        return generate_dashboard_report_pdf(dashboards[0])


# User Management & Permissions
from django.contrib.auth.models import User

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for User management
    
    List all users, create new user, update user, delete user
    Only admins can access this endpoint
    
    Protection: Admin SIGETI (@admin) cannot be deleted or modified
    """
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Return appropriate serializer"""
        from .serializers import UserSerializer as US
        return US

    def perform_destroy(self, instance):
        """Prevent deletion of admin SIGETI"""
        if instance.username == 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "L'administrateur SIGETI (@admin) ne peut pas être supprimé"
            )
        instance.delete()

    def perform_create(self, serializer):
        """Create new user with password and dashboards"""
        serializer.save()

    def perform_update(self, serializer):
        """Update user, handling password and dashboards"""
        serializer.save()

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Set password for user"""
        user = self.get_object()
        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.save()
            return Response({'status': 'password set'})
        return Response(
            {'error': 'password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class MartImplantationSuiviViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Implantation Suivi Mart
    
    Filters available:
    - zone_id: Filter by zone ID
    - annee: Filter by year
    - mois: Filter by month
    """
    queryset = MartImplantationSuivi.objects.all()
    serializer_class = MartImplantationSuiviSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['zone_id', 'annee', 'mois']
    ordering_fields = ['annee', 'mois', 'nombre_implantations']
    ordering = ['-annee', '-mois']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('implantation_summary', timeout=300)
    def summary(self, request):
        """Get implantation summary statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary_data = queryset.aggregate(
            total_implantations=Sum('nombre_implantations'),
            total_etapes=Sum('nombre_etapes'),
            total_terminees=Sum('etapes_terminees'),
            total_en_retard=Sum('etapes_en_retard'),
            avg_completude=Avg('taux_completude_pct'),
            zones_count=Count('zone_id', distinct=True)
        )
        
        return Response(summary_data)


class MartIndemnisationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Indemnisations Mart
    
    Filters available:
    - zone_id: Filter by zone ID
    - annee: Filter by year
    - mois: Filter by month
    - statut: Filter by status
    """
    queryset = MartIndemnisations.objects.all()
    serializer_class = MartIndemnisationsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['zone_id', 'annee', 'mois', 'statut']
    ordering_fields = ['annee', 'mois', 'nombre_indemnisations', 'montant_total_restant']
    ordering = ['-annee', '-mois']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('indemnisations_summary', timeout=300)
    def summary(self, request):
        """Get indemnisations summary statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary_data = queryset.aggregate(
            total_indemnisations=Sum('nombre_indemnisations'),
            total_beneficiaires=Sum('nombre_beneficiaires'),
            total_montant_restant=Sum('montant_total_restant'),
            montant_moyen=Avg('montant_moyen'),
            zones_count=Count('zone_id', distinct=True)
        )
        
        return Response(summary_data)


class MartEmploisCreesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Emplois Créés Mart
    
    Filters available:
    - zone_id: Filter by zone ID
    - annee: Filter by year
    - mois: Filter by month
    """
    queryset = MartEmploisCrees.objects.all()
    serializer_class = MartEmploisCreesSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['zone_id', 'annee', 'mois']
    ordering_fields = ['annee', 'mois', 'nombre_emplois_crees']
    ordering = ['-annee', '-mois']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('emplois_summary', timeout=300)
    def summary(self, request):
        """Get emplois summary statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary_data = queryset.aggregate(
            total_emplois_crees=Sum('nombre_emplois_crees'),
            total_cdi=Sum('nombre_cdi'),
            total_cdd=Sum('nombre_cdd'),
            total_montant_salaires=Sum('montant_salaires'),
            zones_count=Count('zone_id', distinct=True)
        )
        
        return Response(summary_data)


class MartCreancesAgeesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Créances Âgées Mart
    
    Filters available:
    - zone_id: Filter by zone ID
    - annee: Filter by year
    - mois: Filter by month
    """
    queryset = MartCreancesAgees.objects.all()
    serializer_class = MartCreancesAgeesSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['zone_id', 'annee', 'mois']
    ordering_fields = ['annee', 'mois', 'montant_creances']
    ordering = ['-annee', '-mois']
    
    @action(detail=False, methods=['get'])
    @cache_api_response('creances_summary', timeout=300)
    def summary(self, request):
        """Get créances summary statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary_data = queryset.aggregate(
            total_creances=Sum('nombre_creances'),
            total_montant_creances=Sum('montant_creances'),
            total_montant_recouvre=Sum('montant_recouvre'),
            avg_taux_recouvrement=Avg('taux_recouvrement_pct'),
            zones_count=Count('zone_id', distinct=True)
        )
        
        return Response(summary_data)