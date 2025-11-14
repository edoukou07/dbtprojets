"""
URL configuration for API endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MartPerformanceFinanciereViewSet,
    MartOccupationZonesViewSet,
    MartPortefeuilleClientsViewSet,
    MartKPIOperationnelsViewSet,
    AlertViewSet,
    AlertThresholdViewSet,
    login_view,
    logout_view,
    current_user_view,
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

router = DefaultRouter()
router.register(r'financier', MartPerformanceFinanciereViewSet, basename='financier')
router.register(r'occupation', MartOccupationZonesViewSet, basename='occupation')
router.register(r'clients', MartPortefeuilleClientsViewSet, basename='clients')
router.register(r'operationnel', MartKPIOperationnelsViewSet, basename='operationnel')
router.register(r'alerts', AlertViewSet, basename='alerts')
router.register(r'alert-thresholds', AlertThresholdViewSet, basename='alert-thresholds')

urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication endpoints
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
]
