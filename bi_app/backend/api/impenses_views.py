"""
API Views for Impenses Dashboard
Provides comprehensive analytics for impenses workflow tracking
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum, Q, F
from django.db.models.functions import TruncMonth, TruncWeek

from analytics.models import MartSuiviImpenses
from .serializers import MartSuiviImpensesSerializer, MartSuiviImpensesSummarySerializer
from .cache_decorators import cache_api_response


class MartSuiviImpensesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Impenses Tracking Dashboard
    
    Provides:
    - List of all impenses with full details
    - Summary KPIs
    - Distribution by phase, zone, alert level
    - Performance metrics
    - SLA compliance tracking
    """
    queryset = MartSuiviImpenses.objects.all()
    serializer_class = MartSuiviImpensesSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = [
        'statut_actuel', 'phase_actuelle', 'niveau_alerte', 
        'zone_industrielle_code', 'est_en_retard', 'est_inactif',
        'mois_creation', 'trimestre_creation'
    ]
    search_fields = ['numero_dossier', 'nom_operateur', 'nom_entreprise']
    ordering_fields = [
        'date_creation', 'duree_totale_jours', 'nb_actions_total', 
        'score_sante_dossier', 'complexite_score'
    ]
    ordering = ['-date_creation']

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_summary', timeout=300)
    def summary(self, request):
        """
        Get summary KPIs for impenses dashboard
        Returns aggregated metrics for all impenses
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Total counts
        total = queryset.count()
        en_cours = queryset.filter(~Q(statut_actuel='clôturé')).count()
        clotures = queryset.filter(statut_actuel='clôturé').count()
        
        # Alert levels
        critiques = queryset.filter(niveau_alerte='CRITIQUE').count()
        en_alerte = queryset.filter(niveau_alerte='ALERTE').count()
        en_retard = queryset.filter(est_en_retard=True).count()
        
        # Averages
        aggregates = queryset.aggregate(
            score_sante_moyen=Avg('score_sante_dossier'),
            taux_first_pass_moyen=Avg('taux_first_pass_pct'),
            duree_moyenne_jours=Avg('duree_totale_jours'),
            taux_conformite_sla_moyen=Avg('taux_conformite_sla_pct'),
            nb_actions_moyen=Avg('nb_actions_total'),
            nb_allers_retours_moyen=Avg('nb_allers_retours')
        )
        
        summary_data = {
            'total_dossiers': total,
            'dossiers_en_cours': en_cours,
            'dossiers_clotures': clotures,
            'dossiers_critiques': critiques,
            'dossiers_en_alerte': en_alerte,
            'dossiers_en_retard': en_retard,
            'score_sante_moyen': round(aggregates['score_sante_moyen'] or 0, 1),
            'taux_first_pass_moyen': round(aggregates['taux_first_pass_moyen'] or 0, 1),
            'duree_moyenne_jours': round(float(aggregates['duree_moyenne_jours'] or 0), 1),
            'taux_conformite_sla_moyen': round(float(aggregates['taux_conformite_sla_moyen'] or 0), 1),
            'nb_actions_moyen': round(aggregates['nb_actions_moyen'] or 0, 1),
            'nb_allers_retours_moyen': round(aggregates['nb_allers_retours_moyen'] or 0, 2)
        }
        
        return Response(summary_data)

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_by_phase', timeout=300)
    def by_phase(self, request):
        """
        Get distribution of impenses by phase
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        distribution = queryset.values('phase_actuelle', 'phase_actuelle_libelle').annotate(
            count=Count('impense_id'),
            duree_moyenne=Avg('duree_totale_jours'),
            score_sante_moyen=Avg('score_sante_dossier')
        ).order_by('phase_actuelle')
        
        return Response(list(distribution))

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_by_zone', timeout=300)
    def by_zone(self, request):
        """
        Get distribution of impenses by industrial zone
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        distribution = queryset.values(
            'zone_industrielle_code', 
            'zone_industrielle_libelle'
        ).annotate(
            count=Count('impense_id'),
            en_retard=Count('impense_id', filter=Q(est_en_retard=True)),
            critiques=Count('impense_id', filter=Q(niveau_alerte='CRITIQUE')),
            score_sante_moyen=Avg('score_sante_dossier'),
            duree_moyenne=Avg('duree_totale_jours')
        ).order_by('-count')
        
        return Response(list(distribution))

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_by_alert', timeout=300)
    def by_alert_level(self, request):
        """
        Get distribution of impenses by alert level
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        distribution = queryset.values('niveau_alerte').annotate(
            count=Count('impense_id'),
            duree_moyenne=Avg('duree_totale_jours'),
            nb_actions_moyen=Avg('nb_actions_total')
        ).order_by('niveau_alerte')
        
        # Define order and colors for alert levels
        alert_order = {'CRITIQUE': 1, 'ALERTE': 2, 'ATTENTION': 3, 'NORMAL': 4, 'TERMINE': 5}
        alert_colors = {
            'CRITIQUE': '#ef4444',
            'ALERTE': '#f97316', 
            'ATTENTION': '#eab308',
            'NORMAL': '#22c55e',
            'TERMINE': '#6b7280'
        }
        
        result = []
        for item in distribution:
            item['order'] = alert_order.get(item['niveau_alerte'], 99)
            item['color'] = alert_colors.get(item['niveau_alerte'], '#9ca3af')
            result.append(item)
        
        result.sort(key=lambda x: x['order'])
        return Response(result)

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_by_role', timeout=300)
    def by_role(self, request):
        """
        Get intervention statistics by role
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        totals = queryset.aggregate(
            total_admin=Sum('nb_interventions_admin'),
            total_operateur=Sum('nb_interventions_operateur'),
            total_utilisateur=Sum('nb_interventions_utilisateur')
        )
        
        total_interventions = (
            (totals['total_admin'] or 0) + 
            (totals['total_operateur'] or 0) + 
            (totals['total_utilisateur'] or 0)
        )
        
        result = [
            {
                'role': 'Admin',
                'count': totals['total_admin'] or 0,
                'percentage': round((totals['total_admin'] or 0) / total_interventions * 100, 1) if total_interventions > 0 else 0,
                'color': '#3b82f6'
            },
            {
                'role': 'Opérateur',
                'count': totals['total_operateur'] or 0,
                'percentage': round((totals['total_operateur'] or 0) / total_interventions * 100, 1) if total_interventions > 0 else 0,
                'color': '#10b981'
            },
            {
                'role': 'Utilisateur',
                'count': totals['total_utilisateur'] or 0,
                'percentage': round((totals['total_utilisateur'] or 0) / total_interventions * 100, 1) if total_interventions > 0 else 0,
                'color': '#8b5cf6'
            }
        ]
        
        return Response(result)

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_sla', timeout=300)
    def sla_compliance(self, request):
        """
        Get SLA compliance statistics
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Count SLA compliance by phase
        total = queryset.count()
        if total == 0:
            return Response({
                'phases': [],
                'global_compliance': 0
            })
        
        sla_stats = queryset.aggregate(
            phase1_ok=Count('impense_id', filter=Q(sla_phase1_respecte=True)),
            phase1_total=Count('impense_id', filter=Q(temps_phase1_heures__isnull=False, temps_phase1_heures__gt=0)),
            phase2_ok=Count('impense_id', filter=Q(sla_phase2_respecte=True)),
            phase2_total=Count('impense_id', filter=Q(temps_phase2_heures__isnull=False, temps_phase2_heures__gt=0)),
            phase3_ok=Count('impense_id', filter=Q(sla_phase3_respecte=True)),
            phase3_total=Count('impense_id', filter=Q(temps_phase3_heures__isnull=False, temps_phase3_heures__gt=0)),
        )
        
        phases = [
            {
                'phase': 'Phase 1: Création',
                'sla_max_heures': 48,
                'respecte': sla_stats['phase1_ok'],
                'total': sla_stats['phase1_total'],
                'taux': round(sla_stats['phase1_ok'] / sla_stats['phase1_total'] * 100, 1) if sla_stats['phase1_total'] > 0 else 0
            },
            {
                'phase': 'Phase 2: Vérification',
                'sla_max_heures': 72,
                'respecte': sla_stats['phase2_ok'],
                'total': sla_stats['phase2_total'],
                'taux': round(sla_stats['phase2_ok'] / sla_stats['phase2_total'] * 100, 1) if sla_stats['phase2_total'] > 0 else 0
            },
            {
                'phase': 'Phase 3: Analyse',
                'sla_max_heures': 120,
                'respecte': sla_stats['phase3_ok'],
                'total': sla_stats['phase3_total'],
                'taux': round(sla_stats['phase3_ok'] / sla_stats['phase3_total'] * 100, 1) if sla_stats['phase3_total'] > 0 else 0
            }
        ]
        
        # Global compliance
        avg_compliance = queryset.aggregate(avg=Avg('taux_conformite_sla_pct'))
        
        return Response({
            'phases': phases,
            'global_compliance': round(float(avg_compliance['avg'] or 0), 1)
        })

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_performance', timeout=300)
    def performance_metrics(self, request):
        """
        Get performance metrics for impenses
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        metrics = queryset.aggregate(
            avg_duree=Avg('duree_totale_jours'),
            avg_actions=Avg('nb_actions_total'),
            avg_agents=Avg('nb_agents_impliques'),
            avg_allers_retours=Avg('nb_allers_retours'),
            avg_documents=Avg('nb_documents_uploades'),
            avg_delai_reponse=Avg('delai_moyen_reponse_heures'),
            avg_complexite=Avg('complexite_score'),
            avg_efficacite=Avg('efficacite_actions_par_jour'),
            taux_rejet_global=Avg('taux_rejet_pct'),
            taux_correction_global=Avg('taux_correction_pct'),
            taux_first_pass_global=Avg('taux_first_pass_pct')
        )
        
        return Response({
            'duree_moyenne_jours': round(float(metrics['avg_duree'] or 0), 1),
            'actions_moyennes': round(metrics['avg_actions'] or 0, 1),
            'agents_moyens': round(metrics['avg_agents'] or 0, 1),
            'allers_retours_moyens': round(metrics['avg_allers_retours'] or 0, 2),
            'documents_moyens': round(metrics['avg_documents'] or 0, 1),
            'delai_reponse_moyen_heures': round(float(metrics['avg_delai_reponse'] or 0), 1),
            'complexite_moyenne': round(metrics['avg_complexite'] or 0, 0),
            'efficacite_moyenne': round(float(metrics['avg_efficacite'] or 0), 2),
            'taux_rejet_global': round(float(metrics['taux_rejet_global'] or 0), 1),
            'taux_correction_global': round(float(metrics['taux_correction_global'] or 0), 1),
            'taux_first_pass_global': round(float(metrics['taux_first_pass_global'] or 0), 1)
        })

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_timeline', timeout=300)
    def timeline(self, request):
        """
        Get impenses creation timeline by month
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Group by month
        timeline = queryset.values('mois_creation').annotate(
            count=Count('impense_id'),
            avg_duree=Avg('duree_totale_jours'),
            avg_score=Avg('score_sante_dossier')
        ).order_by('mois_creation')
        
        return Response(list(timeline))

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_critiques', timeout=60)
    def critical_list(self, request):
        """
        Get list of critical impenses requiring attention
        """
        queryset = self.get_queryset().filter(
            Q(niveau_alerte='CRITIQUE') | 
            Q(niveau_alerte='ALERTE') |
            Q(est_en_retard=True) |
            Q(risque_abandon=True)
        ).order_by('-duree_totale_jours')[:20]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_temps_phase', timeout=300)
    def temps_par_phase(self, request):
        """
        Get average time spent in each phase
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        temps = queryset.aggregate(
            phase1=Avg('temps_phase1_heures'),
            phase2=Avg('temps_phase2_heures'),
            phase3=Avg('temps_phase3_heures'),
            phase4=Avg('temps_phase4_heures'),
            phase5=Avg('temps_phase5_heures'),
            phase6=Avg('temps_phase6_heures')
        )
        
        result = [
            {'phase': 'Phase 1: Création', 'heures': round(float(temps['phase1'] or 0), 1)},
            {'phase': 'Phase 2: Vérification', 'heures': round(float(temps['phase2'] or 0), 1)},
            {'phase': 'Phase 3: Analyse', 'heures': round(float(temps['phase3'] or 0), 1)},
            {'phase': 'Phase 4: Validation DI', 'heures': round(float(temps['phase4'] or 0), 1)},
            {'phase': 'Phase 5: Validation DG', 'heures': round(float(temps['phase5'] or 0), 1)},
            {'phase': 'Phase 6: Visite', 'heures': round(float(temps['phase6'] or 0), 1)}
        ]
        
        return Response(result)

    @action(detail=False, methods=['get'])
    @cache_api_response('impenses_health_distribution', timeout=300)
    def health_distribution(self, request):
        """
        Get distribution of health scores
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Categorize health scores
        distribution = {
            'excellent': queryset.filter(score_sante_dossier__gte=80).count(),
            'bon': queryset.filter(score_sante_dossier__gte=60, score_sante_dossier__lt=80).count(),
            'moyen': queryset.filter(score_sante_dossier__gte=40, score_sante_dossier__lt=60).count(),
            'faible': queryset.filter(score_sante_dossier__lt=40).count()
        }
        
        total = sum(distribution.values())
        
        result = [
            {
                'category': 'Excellent (80-100)',
                'count': distribution['excellent'],
                'percentage': round(distribution['excellent'] / total * 100, 1) if total > 0 else 0,
                'color': '#22c55e'
            },
            {
                'category': 'Bon (60-79)',
                'count': distribution['bon'],
                'percentage': round(distribution['bon'] / total * 100, 1) if total > 0 else 0,
                'color': '#84cc16'
            },
            {
                'category': 'Moyen (40-59)',
                'count': distribution['moyen'],
                'percentage': round(distribution['moyen'] / total * 100, 1) if total > 0 else 0,
                'color': '#eab308'
            },
            {
                'category': 'Faible (0-39)',
                'count': distribution['faible'],
                'percentage': round(distribution['faible'] / total * 100, 1) if total > 0 else 0,
                'color': '#ef4444'
            }
        ]
        
        return Response(result)
