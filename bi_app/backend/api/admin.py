"""
Admin configuration pour l'application API
"""

from django.contrib import admin

# Importer la configuration admin d'authentification
from .admin_auth import *  # noqa
from .models import SMTPConfiguration


@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
    """Interface d'administration pour la configuration SMTP."""

    list_display = (
        'name',
        'host',
        'port',
        'use_tls',
        'use_ssl',
        'is_active',
        'last_test_status',
        'last_tested_at',
        'updated_at',
    )
    list_filter = ('is_active', 'use_tls', 'use_ssl', 'last_test_status')
    search_fields = ('name', 'host', 'username')
    readonly_fields = ('last_tested_at', 'last_test_status', 'last_error', 'created_at', 'updated_at')
    fieldsets = (
        ('Connexion', {
            'fields': ('name', 'backend', 'host', 'port', 'use_tls', 'use_ssl', 'timeout', 'is_active')
        }),
        ('Identifiants', {
            'fields': ('username', 'password', 'default_from_email'),
            'classes': ('collapse',),
        }),
        ('Observabilité', {
            'fields': ('last_tested_at', 'last_test_status', 'last_error'),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
