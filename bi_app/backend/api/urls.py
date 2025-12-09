"""
URL configuration for API endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MartPerformanceFinanciereViewSet,
    MartOccupationZonesViewSet,
    MartPortefeuilleClientsViewSet,
    MartKPIOperationnelsViewSet,
    AlertViewSet,
    AlertThresholdViewSet,
    ReportScheduleViewSet,
    UserViewSet,
    SMTPConfigurationViewSet,
    login_view,
    logout_view,
    current_user_view,
)
from .auth_views import (
    CustomTokenObtainPairView,
    login_view as jwt_login_view,
    logout_view as jwt_logout_view,
    register_view,
    me_view,
    update_profile_view,
)
from .logging_views import (
    api_metrics,
    recent_logs,
    error_logs,
    slow_requests,
    log_analytics,
    clear_metrics,
)
from .geo_views import (
    zones_map_data,
    zone_details_map,
)
from .refresh_views import (
    refresh_all_views,
    refresh_specific_view,
    get_refresh_status,
)
from .alert_config_views import (
    AlertThresholdsView,
    AlertThresholdsResetView,
)
from .compliance_views import ComplianceViewSet
from .compliance_compliance_views import ComplianceComplianceViewSet
from .rh_views import RhViewSet

router = DefaultRouter()
router.register(r'financier', MartPerformanceFinanciereViewSet, basename='financier')
router.register(r'occupation', MartOccupationZonesViewSet, basename='occupation')
router.register(r'clients', MartPortefeuilleClientsViewSet, basename='clients')
router.register(r'operationnel', MartKPIOperationnelsViewSet, basename='operationnel')
router.register(r'compliance', ComplianceViewSet, basename='compliance')
router.register(r'compliance-compliance', ComplianceComplianceViewSet, basename='compliance-compliance')
router.register(r'rh', RhViewSet, basename='rh')
router.register(r'implantation-suivi', MartImplantationSuiviViewSet, basename='implantation-suivi')
router.register(r'indemnisations', MartIndemnisationsViewSet, basename='indemnisations')
router.register(r'emplois-crees', MartEmploisCreesViewSet, basename='emplois-crees')
router.register(r'creances-agees', MartCreancesAgeesViewSet, basename='creances-agees')
router.register(r'alerts', AlertViewSet, basename='alerts')
router.register(r'alert-thresholds', AlertThresholdViewSet, basename='alert-thresholds')
router.register(r'reports', ReportScheduleViewSet, basename='reports')
router.register(r'auth/users', UserViewSet, basename='users')
router.register(r'smtp', SMTPConfigurationViewSet, basename='smtp')

urlpatterns = [
    path('', include(router.urls)),
    
    # JWT Authentication endpoints (NEW - SECURE)
    path('auth/jwt/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/jwt/login/', jwt_login_view, name='jwt-login'),
    path('auth/jwt/logout/', jwt_logout_view, name='jwt-logout'),
    path('auth/jwt/register/', register_view, name='jwt-register'),
    path('auth/jwt/me/', me_view, name='jwt-me'),
    path('auth/jwt/profile/', update_profile_view, name='jwt-profile'),
    
    # Legacy Authentication endpoints (DEPRECATED - kept for backward compatibility)
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/user/', current_user_view, name='current-user'),
    
    # Logging & Monitoring endpoints
    path('monitoring/metrics/', api_metrics, name='api-metrics'),
    path('monitoring/logs/', recent_logs, name='recent-logs'),
    path('monitoring/errors/', error_logs, name='error-logs'),
    path('monitoring/slow/', slow_requests, name='slow-requests'),
    path('monitoring/analytics/', log_analytics, name='log-analytics'),
    path('monitoring/clear-metrics/', clear_metrics, name='clear-metrics'),
    
    # Geographic/Map endpoints
    path('zones/map/', zones_map_data, name='zones-map'),
    path('zones/<int:zone_id>/map/', zone_details_map, name='zone-details-map'),
    
    # Refresh Materialized Views endpoints
    path('refresh/all/', refresh_all_views, name='refresh-all-views'),
    path('refresh/status/', get_refresh_status, name='refresh-status'),
    path('refresh/<str:view_name>/', refresh_specific_view, name='refresh-specific-view'),
    
    # Alert Configuration endpoints
    path('alerts/thresholds/', AlertThresholdsView.as_view(), name='alert-thresholds'),
    path('alerts/thresholds/reset/', AlertThresholdsResetView.as_view(), name='alert-thresholds-reset'),
]
