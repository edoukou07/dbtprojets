"""
Serializers for SIGETI BI API
"""
from rest_framework import serializers
from analytics.models import (
    MartPerformanceFinanciere,
    MartOccupationZones,
    MartPortefeuilleClients,
    MartKPIOperationnels
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
