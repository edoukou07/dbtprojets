"""
Serializers for SIGETI BI API
"""
from rest_framework import serializers
from analytics.models import (
    MartPerformanceFinanciere,
    MartOccupationZones,
    MartPortefeuilleClients,
    MartKPIOperationnels,
    Alert,
    AlertThreshold
)


class MartPerformanceFinanciereSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartPerformanceFinanciere
        fields = '__all__'


class MartOccupationZonesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartOccupationZones
        fields = '__all__'


class MartPortefeuilleClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartPortefeuilleClients
        fields = '__all__'


class MartKPIOperationnelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartKPIOperationnels
        fields = '__all__'


class AlertSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AlertThresholdSerializer(serializers.ModelSerializer):
    threshold_operator_display = serializers.CharField(source='get_threshold_operator_display', read_only=True)
    
    class Meta:
        model = AlertThreshold
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'last_checked')
