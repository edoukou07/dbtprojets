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
    AlertThreshold,
    UserDashboardPermission,
    ReportSchedule,
    MartImplantationSuivi,
    MartIndemnisations,
    MartEmploisCrees,
    MartCreancesAgees
)


class ReportScheduleSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = ['id', 'name', 'dashboard', 'scheduled_at', 'recipients', 'created_by', 'created_by_username', 'created_at', 'sent', 'sent_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'sent', 'sent_at']


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


# User Serializer
from django.contrib.auth.models import User
from django.db import transaction


class UserSerializer(serializers.ModelSerializer):
    dashboards = serializers.SerializerMethodField()
    dashboards_write = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'is_staff', 'is_active', 'dashboards', 'dashboards_write', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'dashboards']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def get_dashboards(self, obj):
        """Retrieve list of dashboards the user has access to"""
        permissions = UserDashboardPermission.objects.filter(user=obj).values_list('dashboard', flat=True)
        return list(permissions)

    def create(self, validated_data):
        # Extraire dashboards
        dashboards = validated_data.pop('dashboards_write', [])
        password = validated_data.pop('password', None)
        
        with transaction.atomic():
            user = User(**validated_data)
            if password:
                user.set_password(password)
            user.save()
            
            # Create dashboard permissions
            for dashboard in dashboards:
                UserDashboardPermission.objects.get_or_create(
                    user=user,
                    dashboard=dashboard
                )
        
        return user

    def update(self, instance, validated_data):
        # Extraire dashboards
        dashboards = validated_data.pop('dashboards_write', [])
        password = validated_data.pop('password', None)
        
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            if password:
                instance.set_password(password)
            instance.save()
            
            # Update dashboard permissions
            UserDashboardPermission.objects.filter(user=instance).delete()
            for dashboard in dashboards:
                UserDashboardPermission.objects.get_or_create(
                    user=instance,
                    dashboard=dashboard
                )
        
        return instance


class MartImplantationSuiviSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartImplantationSuivi
        fields = '__all__'


class MartIndemnisationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartIndemnisations
        fields = '__all__'


class MartEmploisCreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartEmploisCrees
        fields = '__all__'


class MartCreancesAgeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartCreancesAgees
        fields = '__all__'
