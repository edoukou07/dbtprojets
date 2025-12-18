"""
Serializers for SIGETI BI API
"""
from rest_framework import serializers
from django.utils import timezone
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
from .models import SMTPConfiguration


class ReportScheduleSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    dashboards = serializers.ListField(
        child=serializers.ChoiceField(choices=ReportSchedule.DASHBOARD_CHOICES),
        required=False,
        allow_empty=False,
        help_text="Liste des dashboards à inclure dans le rapport"
    )
    recurrence_days_of_week = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=False,
        allow_empty=True,
        help_text="Jours de la semaine [0-6] où 0=lundi pour récurrence hebdomadaire"
    )
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'name', 'dashboard', 'dashboards', 'scheduled_at', 'recipients',
            'created_by', 'created_by_username', 'created_at', 'sent', 'sent_at', 'pdfs_data',
            # Recurrence fields
            'is_recurring', 'recurrence_type', 'recurrence_interval', 'recurrence_minute',
            'recurrence_hour', 'recurrence_days_of_week', 'recurrence_day_of_month',
            'recurrence_week_of_month', 'recurrence_month', 'recurrence_workdays_only',
            'recurrence_hour_range_start', 'recurrence_hour_range_end',
            'recurrence_hour_range_interval', 'recurrence_end_date', 'parent_schedule',
            'occurrence_number'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'sent', 'sent_at', 'pdfs_data',
            'parent_schedule', 'occurrence_number'
        ]
    
    def to_internal_value(self, data):
        """Parse JSON strings from FormData"""
        import json
        
        # Convertir QueryDict en dict normal pour pouvoir le modifier
        if hasattr(data, 'getlist'):
            # C'est un QueryDict (venant de FormData)
            data_dict = {}
            for key in data.keys():
                values = data.getlist(key)
                if len(values) == 1:
                    data_dict[key] = values[0]
                else:
                    data_dict[key] = values
            data = data_dict
        elif hasattr(data, 'copy'):
            data = data.copy()
        else:
            data = dict(data)
        
        # Si dashboards est une chaîne JSON (venant de FormData), la parser
        if 'dashboards' in data:
            dashboards_value = data['dashboards']
            # Gérer le cas où c'est une liste avec une seule chaîne
            if isinstance(dashboards_value, list) and len(dashboards_value) > 0:
                dashboards_value = dashboards_value[0]
            
            if isinstance(dashboards_value, str):
                try:
                    parsed = json.loads(dashboards_value)
                    data['dashboards'] = parsed
                except (json.JSONDecodeError, ValueError):
                    pass  # Si le parsing échoue, laisser le serializer gérer l'erreur
        
        # Parser recurrence_days_of_week si c'est une chaîne JSON
        if 'recurrence_days_of_week' in data:
            days_value = data['recurrence_days_of_week']
            if isinstance(days_value, list) and len(days_value) > 0 and isinstance(days_value[0], str):
                days_value = days_value[0]
            
            if isinstance(days_value, str):
                try:
                    parsed = json.loads(days_value)
                    data['recurrence_days_of_week'] = parsed
                except (json.JSONDecodeError, ValueError):
                    pass
        
        # Convertir les valeurs booléennes string en bool
        for bool_field in ['is_recurring', 'recurrence_workdays_only']:
            if bool_field in data:
                value = data[bool_field]
                if isinstance(value, str):
                    data[bool_field] = value.lower() in ('true', '1', 'yes', 'on')
        
        # Convertir les valeurs numériques string en int
        for int_field in [
            'recurrence_interval', 'recurrence_minute', 'recurrence_hour',
            'recurrence_day_of_month', 'recurrence_week_of_month', 'recurrence_month',
            'recurrence_hour_range_interval'
        ]:
            if int_field in data:
                value = data[int_field]
                if isinstance(value, str):
                    try:
                        data[int_field] = int(value) if value else None
                    except ValueError:
                        pass
        
        return super().to_internal_value(data)
    
    def validate(self, data):
        """Valide que soit dashboard soit dashboards est fourni et valide la récurrence"""
        dashboards = data.get('dashboards', [])
        dashboard = data.get('dashboard')
        
        # Si dashboards est fourni et non vide, on l'utilise
        if dashboards and len(dashboards) > 0:
            pass
        # Sinon, si dashboard est fourni (compatibilité ascendante), on le convertit en liste
        elif dashboard:
            data['dashboards'] = [dashboard]
        # Si aucun n'est fourni, on retourne une erreur
        else:
            raise serializers.ValidationError("Vous devez sélectionner au moins un dashboard (champ 'dashboards' ou 'dashboard').")
        
        # Validation de la récurrence
        is_recurring = data.get('is_recurring', False)
        recurrence_type = data.get('recurrence_type', 'none')
        
        if is_recurring and recurrence_type != 'none':
            # Valider selon le type de récurrence
            if recurrence_type == 'minute':
                # Pour récurrence par minute, interval doit être défini
                if not data.get('recurrence_interval'):
                    raise serializers.ValidationError({
                        'recurrence_interval': 'Intervalle requis pour récurrence par minute'
                    })
            
            elif recurrence_type == 'hour':
                # Pour récurrence par heure
                has_range = data.get('recurrence_hour_range_start') and data.get('recurrence_hour_range_end')
                has_fixed_hour = data.get('recurrence_hour') is not None
                if not has_range and not has_fixed_hour and not data.get('recurrence_interval'):
                    raise serializers.ValidationError({
                        'recurrence_hour': 'Heure fixe, plage horaire ou intervalle requis pour récurrence par heure'
                    })
            
            elif recurrence_type == 'weekly':
                # Pour récurrence hebdomadaire, jours de la semaine requis
                days_of_week = data.get('recurrence_days_of_week', [])
                if not days_of_week:
                    raise serializers.ValidationError({
                        'recurrence_days_of_week': 'Au moins un jour de la semaine requis pour récurrence hebdomadaire'
                    })
            
            elif recurrence_type == 'monthly':
                # Pour récurrence mensuelle
                has_day = data.get('recurrence_day_of_month') is not None
                has_week = data.get('recurrence_week_of_month') is not None and data.get('recurrence_days_of_week')
                if not has_day and not has_week and not data.get('recurrence_workdays_only'):
                    raise serializers.ValidationError({
                        'recurrence_day_of_month': 'Jour du mois, semaine/jour relatif ou jours ouvrables requis pour récurrence mensuelle'
                    })
            
            elif recurrence_type == 'yearly':
                # Pour récurrence annuelle, mois requis
                if not data.get('recurrence_month'):
                    raise serializers.ValidationError({
                        'recurrence_month': 'Mois requis pour récurrence annuelle'
                    })
            
            # Valider la plage horaire si spécifiée
            if data.get('recurrence_hour_range_start') or data.get('recurrence_hour_range_end'):
                start = data.get('recurrence_hour_range_start')
                end = data.get('recurrence_hour_range_end')
                if not start or not end:
                    raise serializers.ValidationError({
                        'recurrence_hour_range_start': 'Début et fin de plage horaire requis ensemble'
                    })
                if start and end and start >= end:
                    raise serializers.ValidationError({
                        'recurrence_hour_range_end': 'La fin de plage doit être après le début'
                    })
            
            # Valider les valeurs numériques
            if data.get('recurrence_minute') is not None and not (0 <= data['recurrence_minute'] <= 59):
                raise serializers.ValidationError({
                    'recurrence_minute': 'Minute doit être entre 0 et 59'
                })
            
            if data.get('recurrence_hour') is not None and not (0 <= data['recurrence_hour'] <= 23):
                raise serializers.ValidationError({
                    'recurrence_hour': 'Heure doit être entre 0 et 23'
                })
            
            if data.get('recurrence_day_of_month') is not None:
                day = data['recurrence_day_of_month']
                if day != -1 and not (1 <= day <= 31):
                    raise serializers.ValidationError({
                        'recurrence_day_of_month': 'Jour du mois doit être entre 1 et 31, ou -1 pour dernier jour'
                    })
            
            if data.get('recurrence_week_of_month') is not None and not (1 <= data['recurrence_week_of_month'] <= 4):
                raise serializers.ValidationError({
                    'recurrence_week_of_month': 'Semaine du mois doit être entre 1 et 4'
                })
            
            if data.get('recurrence_month') is not None and not (1 <= data['recurrence_month'] <= 12):
                raise serializers.ValidationError({
                    'recurrence_month': 'Mois doit être entre 1 et 12'
                })
        
        # S'assurer que scheduled_at est timezone-aware
        if 'scheduled_at' in data and data['scheduled_at']:
            scheduled_at = data['scheduled_at']
            if not timezone.is_aware(scheduled_at):
                data['scheduled_at'] = timezone.make_aware(scheduled_at)
        
        return data
    
    def create(self, validated_data):
        """Crée un nouveau rapport avec gestion de la compatibilité et calcul de la récurrence"""
        from analytics.recurrence import RecurrenceCalculator
        
        dashboards = validated_data.pop('dashboards', [])
        dashboard = validated_data.pop('dashboard', None)
        
        # Si dashboards est vide mais dashboard existe, on utilise dashboard
        if not dashboards and dashboard:
            dashboards = [dashboard]
        
        # Si dashboards est toujours vide, on utilise une valeur par défaut
        if not dashboards:
            dashboards = ['financier']
        
        validated_data['dashboards'] = dashboards
        # On garde aussi dashboard pour la compatibilité (premier élément)
        if not validated_data.get('dashboard'):
            validated_data['dashboard'] = dashboards[0] if dashboards else None
        
        # Si c'est un rapport récurrent et que scheduled_at n'est pas défini, calculer la première occurrence
        is_recurring = validated_data.get('is_recurring', False)
        recurrence_type = validated_data.get('recurrence_type', 'none')
        
        # S'assurer que is_recurring est cohérent avec recurrence_type
        if recurrence_type != 'none':
            validated_data['is_recurring'] = True
            is_recurring = True
        
        if is_recurring and recurrence_type != 'none':
            # Créer un objet temporaire pour calculer la récurrence
            temp_schedule = ReportSchedule(**validated_data)
            if not validated_data.get('scheduled_at'):
                # Si pas de scheduled_at, utiliser maintenant comme base
                from django.utils import timezone
                base_time = timezone.now()
                first_occurrence = RecurrenceCalculator.calculate_next_occurrence(temp_schedule, base_time)
                if first_occurrence:
                    validated_data['scheduled_at'] = first_occurrence
        
        # Définir l'utilisateur actuel si non spécifié
        if 'created_by' not in validated_data:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                validated_data['created_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Met à jour un rapport existant"""
        dashboards = validated_data.pop('dashboards', None)
        dashboard = validated_data.pop('dashboard', None)
        
        # Si dashboards est fourni, on l'utilise
        if dashboards is not None:
            if len(dashboards) == 0:
                raise serializers.ValidationError("Vous devez sélectionner au moins un dashboard.")
            instance.dashboards = dashboards
            # On met à jour aussi dashboard pour la compatibilité
            instance.dashboard = dashboards[0]
        elif dashboard is not None:
            # Compatibilité ascendante : si seul dashboard est fourni
            instance.dashboards = [dashboard]
            instance.dashboard = dashboard
        
        return super().update(instance, validated_data)


class SMTPConfigurationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = SMTPConfiguration
        fields = [
            'id',
            'name',
            'backend',
            'host',
            'port',
            'use_tls',
            'use_ssl',
            'username',
            'password',
            'default_from_email',
            'timeout',
            'is_active',
            'last_tested_at',
            'last_test_status',
            'last_error',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'last_tested_at', 'last_test_status', 'last_error', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Empêche l'activation simultanée de TLS et SSL."""
        use_tls = attrs.get('use_tls', getattr(self.instance, 'use_tls', False))
        use_ssl = attrs.get('use_ssl', getattr(self.instance, 'use_ssl', False))
        if use_tls and use_ssl:
            raise serializers.ValidationError("TLS et SSL ne peuvent pas être activés simultanément.")
        return super().validate(attrs)


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
