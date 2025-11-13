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
]
