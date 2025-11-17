"""
API Views for SIGETI BI
"""
from datetime import datetime
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count, Q
from rest_framework.decorators import action
from rest_framework.response import Response

from analytics.models import (
    MartPerformanceFinanciere,
    MartOccupationZones,
    MartPortefeuilleClients,
    MartKPIOperationnels,
    Alert,
    AlertThreshold
)
from .serializers import (
    MartPerformanceFinanciereSerializer,
    MartOccupationZonesSerializer,
    MartPortefeuilleClientsSerializer,
    MartKPIOperationnelsSerializer,
    AlertSerializer,
    AlertThresholdSerializer
)
from .cache_decorators import cache_api_response


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
        
        # Aggregate everything except delai_moyen_paiement — compute that one separately
        # to avoid issues when the database returns an interval (timedelta) while the
        # Django model expects a Decimal. Doing it separately makes conversion robust.
        summary = queryset.aggregate(
            total_factures=Sum('nombre_factures'),
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
            taux_paiement_moyen=Avg('taux_paiement_pct'),
            # delai_moyen_paiement handled below
            total_collectes=Sum('nombre_collectes'),
            montant_recouvre=Sum('montant_total_recouvre'),
        )
        # Try to get average of delai_moyen_paiement separately and normalize to days.
        avg_delai = None
        try:
            avg_delai = queryset.aggregate(avg_delai=Avg('delai_moyen_paiement'))['avg_delai']
        except TypeError:
            # DB sometimes returns an interval (datetime.timedelta) or other types
            # that lead Django internals to fail; fall back to manual computation below.
            avg_delai = None

        # Normalize avg_delai: accept timedelta, Decimal or float
        if isinstance(avg_delai, (int, float)) and avg_delai is not None:
            # Assume avg_delai is number of days already (or units used in DWH)
            summary['delai_moyen_paiement'] = float(avg_delai)
        elif hasattr(avg_delai, 'total_seconds'):
            summary['delai_moyen_paiement'] = avg_delai.total_seconds() / 86400
        elif avg_delai is None:
            # As a fallback — compute manually using values from the queryset.
            values = list(queryset.values_list('delai_moyen_paiement', flat=True))
            # Filter out None
            values = [v for v in values if v is not None]
            if values:
                total_days = 0.0
                count = 0
                for v in values:
                    if hasattr(v, 'total_seconds'):
                        total_days += v.total_seconds() / 86400
                    else:
                        try:
                            total_days += float(v)
                        except Exception:
                            # ignore values we can't parse
                            continue
                    count += 1
                summary['delai_moyen_paiement'] = (total_days / count) if count else 0
            else:
                summary['delai_moyen_paiement'] = 0
        else:
            try:
                summary['delai_moyen_paiement'] = float(avg_delai)
            except Exception:
                summary['delai_moyen_paiement'] = 0
        
        # Calculs additionnels
        if summary['ca_total']:
            summary['taux_impaye_pct'] = (summary['ca_impaye'] or 0) / summary['ca_total'] * 100
            summary['taux_recouvrement_pct'] = (summary['montant_recouvre'] or 0) / summary['ca_impaye'] * 100 if summary['ca_impaye'] else 0
        else:
            summary['taux_impaye_pct'] = 0
            summary['taux_recouvrement_pct'] = 0
        
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
            taux_paiement=Avg('taux_paiement_pct'),
            nombre_factures=Sum('nombre_factures'),
        ).order_by('-total_facture')
        
        return Response(data)
    
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
            taux_paiement=Avg('taux_paiement_pct'),
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
            taux_paiement=Avg('taux_paiement_pct'),
        ).order_by('trimestre')
        
        result = []
        for item in tendances:
            item['nom_trimestre'] = f"T{item['trimestre']}"
            result.append(item)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def analyse_recouvrement(self, request):
        """Detailed recovery analysis"""
        annee = request.query_params.get('annee')
        queryset = self.get_queryset()
        
        if annee:
            queryset = queryset.filter(annee=annee)
        
        analysis = {
            'total_creances': queryset.aggregate(Sum('montant_impaye'))['montant_impaye__sum'] or 0,
            'montant_recouvre': queryset.aggregate(Sum('montant_total_recouvre'))['montant_total_recouvre__sum'] or 0,
            'nombre_collectes': queryset.aggregate(Sum('nombre_collectes'))['nombre_collectes__sum'] or 0,
        }
        
        # Taux de recouvrement
        if analysis['total_creances'] > 0:
            analysis['taux_recouvrement'] = (analysis['montant_recouvre'] / analysis['total_creances']) * 100
        else:
            analysis['taux_recouvrement'] = 0
        
        # Créances restantes
        analysis['creances_restantes'] = analysis['total_creances'] - analysis['montant_recouvre']
        
        # Performance par zone
        analysis['par_zone'] = list(queryset.values('nom_zone').annotate(
            creances=Sum('montant_impaye'),
            recouvre=Sum('montant_total_recouvre'),
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
            taux_paiement=Avg('taux_paiement_pct'),
        ).order_by('-ca_total')[:limit])
        
        # Top zones par taux de paiement
        top_paiement = list(queryset.values('nom_zone').annotate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            taux_paiement=Avg('taux_paiement_pct'),
        ).order_by('-taux_paiement')[:limit])
        
        # Zones à risque (faible taux de paiement)
        zones_risque = list(queryset.values('nom_zone').annotate(
            ca_total=Sum('montant_total_facture'),
            ca_impaye=Sum('montant_impaye'),
            taux_paiement=Avg('taux_paiement_pct'),
        ).filter(taux_paiement__lt=70).order_by('taux_paiement')[:limit])
        
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
        
        # Données année actuelle
        current = self.get_queryset().filter(annee=annee_actuelle).aggregate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
            taux_paiement=Avg('taux_paiement_pct'),
        )
        
        # Données année précédente
        previous = self.get_queryset().filter(annee=annee_precedente).aggregate(
            ca_total=Sum('montant_total_facture'),
            ca_paye=Sum('montant_paye'),
            ca_impaye=Sum('montant_impaye'),
            taux_paiement=Avg('taux_paiement_pct'),
        )
        
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
            taux_occupation_moyen=Avg('taux_occupation_pct'),
            valeur_totale=Sum('valeur_totale_lots'),
        )
        
        # Calculer le nombre de zones
        summary['nombre_zones'] = queryset.count()
        
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
            delai_moyen_paiement=Avg('delai_moyen_paiement'),
            factures_retard_total=Sum('nombre_factures_retard'),
        )
        
        # Convert timedelta to days for delai_moyen_paiement
        if summary['delai_moyen_paiement'] and isinstance(summary['delai_moyen_paiement'], timedelta):
            summary['delai_moyen_paiement'] = summary['delai_moyen_paiement'].days
        elif summary['delai_moyen_paiement'] is None:
            summary['delai_moyen_paiement'] = 0
        
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
        
        # Payment behavior distribution
        comportement = []
        
        # Excellent payers (>95%)
        excellent = queryset.filter(taux_paiement_pct__gte=95).aggregate(
            count=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            delai_moyen=Avg('delai_moyen_paiement')
        )
        # Convert timedelta to days
        if excellent['delai_moyen'] and isinstance(excellent['delai_moyen'], timedelta):
            excellent['delai_moyen'] = excellent['delai_moyen'].days
        excellent['categorie'] = 'Excellent (>95%)'
        excellent['min_taux'] = 95
        excellent['max_taux'] = 100
        comportement.append(excellent)
        
        # Good payers (80-95%)
        bon = queryset.filter(taux_paiement_pct__gte=80, taux_paiement_pct__lt=95).aggregate(
            count=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            delai_moyen=Avg('delai_moyen_paiement')
        )
        if bon['delai_moyen'] and isinstance(bon['delai_moyen'], timedelta):
            bon['delai_moyen'] = bon['delai_moyen'].days
        bon['categorie'] = 'Bon (80-95%)'
        bon['min_taux'] = 80
        bon['max_taux'] = 95
        comportement.append(bon)
        
        # Average payers (60-80%)
        moyen = queryset.filter(taux_paiement_pct__gte=60, taux_paiement_pct__lt=80).aggregate(
            count=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            delai_moyen=Avg('delai_moyen_paiement')
        )
        if moyen['delai_moyen'] and isinstance(moyen['delai_moyen'], timedelta):
            moyen['delai_moyen'] = moyen['delai_moyen'].days
        moyen['categorie'] = 'Moyen (60-80%)'
        moyen['min_taux'] = 60
        moyen['max_taux'] = 80
        comportement.append(moyen)
        
        # Poor payers (<60%)
        faible = queryset.filter(taux_paiement_pct__lt=60).aggregate(
            count=Count('entreprise_id'),
            ca_total=Sum('chiffre_affaires_total'),
            delai_moyen=Avg('delai_moyen_paiement')
        )
        if faible['delai_moyen'] and isinstance(faible['delai_moyen'], timedelta):
            faible['delai_moyen'] = faible['delai_moyen'].days
        faible['categorie'] = 'Faible (<60%)'
        faible['min_taux'] = 0
        faible['max_taux'] = 60
        comportement.append(faible)
        
        # Payment delay analysis (using timedelta for filters)
        delai_ranges = [
            {'min': 0, 'max': 30, 'label': '0-30 jours'},
            {'min': 30, 'max': 60, 'label': '30-60 jours'},
            {'min': 60, 'max': 90, 'label': '60-90 jours'},
            {'min': 90, 'max': 999, 'label': '>90 jours'}
        ]
        
        par_delai = []
        for range_def in delai_ranges:
            stats = queryset.filter(
                delai_moyen_paiement__gte=timedelta(days=range_def['min']),
                delai_moyen_paiement__lt=timedelta(days=range_def['max'])
            ).aggregate(
                count=Count('entreprise_id'),
                ca_total=Sum('chiffre_affaires_total'),
                taux_paiement_moyen=Avg('taux_paiement_pct')
            )
            stats['plage_delai'] = range_def['label']
            par_delai.append(stats)
        
        return Response({
            'par_taux_paiement': comportement,
            'par_delai_paiement': par_delai
        })
    
    @action(detail=False, methods=['get'])
    def analyse_occupation(self, request):
        """Analyze client occupation of industrial lots"""
        queryset = self.get_queryset()
        
        # Clients with attributions
        avec_lots = queryset.filter(nombre_lots_attribues__gt=0)
        sans_lots = queryset.filter(Q(nombre_lots_attribues=0) | Q(nombre_lots_attribues__isnull=True))
        
        stats_avec_lots = avec_lots.aggregate(
            nombre_clients=Count('entreprise_id'),
            total_lots=Sum('nombre_lots_attribues'),
            superficie_totale=Sum('superficie_totale_attribuee'),
            ca_total=Sum('chiffre_affaires_total'),
            ca_moyen=Avg('chiffre_affaires_total')
        )
        
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
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtres personnalisés
        date_debut = request.query_params.get('date_debut')
        date_fin = request.query_params.get('date_fin')
        zone_id = request.query_params.get('zone_id')
        
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
