"""
Modèles de l'application API
"""

from typing import Optional

from django.db import models
from django.utils import timezone

# Importer les modèles d'authentification historiques
from .models_auth import Role, UserProfile


class SMTPConfiguration(models.Model):
    """
    Configuration mutable du serveur SMTP utilisée par l'API.
    Permet d'activer/désactiver dynamiquement l'envoi d'email sans redéploiement.
    """

    TEST_STATUS_CHOICES = [
        ('never', 'Jamais testé'),
        ('success', 'Succès'),
        ('failed', 'Échec'),
    ]

    name = models.CharField(max_length=100, default='Serveur SMTP')
    backend = models.CharField(
        max_length=255,
        default='django.core.mail.backends.smtp.EmailBackend',
    )
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    default_from_email = models.EmailField(blank=True, null=True)
    timeout = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Délai de connexion en secondes",
    )
    is_active = models.BooleanField(default=True)

    # Observabilité
    last_tested_at = models.DateTimeField(blank=True, null=True)
    last_test_status = models.CharField(
        max_length=20,
        choices=TEST_STATUS_CHOICES,
        default='never',
    )
    last_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Configuration SMTP'
        verbose_name_plural = 'Configurations SMTP'

    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"

    @classmethod
    def get_active(cls):
        """Retourne la configuration active la plus récente."""
        return cls.objects.filter(is_active=True).order_by('-updated_at').first()

    def mark_test_result(self, success: bool, error_message: Optional[str] = None):
        """Met à jour les métadonnées d'un test SMTP."""
        self.last_tested_at = timezone.now()
        self.last_test_status = 'success' if success else 'failed'
        self.last_error = '' if success else (error_message or '')
        self.save(update_fields=['last_tested_at', 'last_test_status', 'last_error', 'updated_at'])

    def as_connection_kwargs(self):
        """Retourne les paramètres prêts pour `django.core.mail.get_connection`."""
        return {
            'backend': self.backend,
            'host': self.host,
            'port': self.port,
            'username': self.username or '',
            'password': self.password or '',
            'use_tls': self.use_tls and not self.use_ssl,  # éviter conflit TLS/SSL
            'use_ssl': self.use_ssl,
            'timeout': self.timeout,
            'default_from_email': self.default_from_email,
        }


__all__ = ['Role', 'UserProfile', 'SMTPConfiguration']
