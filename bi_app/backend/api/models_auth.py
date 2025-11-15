"""
Modèle de rôles utilisateur pour SIGETI BI
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """
    Rôles disponibles dans le système
    """
    ADMIN = 'Admin'
    GESTIONNAIRE = 'Gestionnaire'
    LECTEUR = 'Lecteur'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrateur - Tous droits'),
        (GESTIONNAIRE, 'Gestionnaire - Lecture/Écriture'),
        (LECTEUR, 'Lecteur - Lecture seule'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        verbose_name="Nom du rôle"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Permissions spécifiques au format JSON"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class UserProfile(models.Model):
    """
    Extension du modèle User Django avec rôle personnalisé
    """
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name="Rôle"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Département"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dernière IP de connexion"
    )
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    def has_role(self, role_name):
        """Vérifier si l'utilisateur a un rôle spécifique"""
        return self.role.name == role_name
    
    def is_admin(self):
        """Vérifier si l'utilisateur est admin"""
        return self.role.name == Role.ADMIN
    
    def is_gestionnaire(self):
        """Vérifier si l'utilisateur est gestionnaire"""
        return self.role.name == Role.GESTIONNAIRE
    
    def is_lecteur(self):
        """Vérifier si l'utilisateur est lecteur"""
        return self.role.name == Role.LECTEUR


# Signal pour ajouter la propriété 'role' directement sur User
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil pour chaque nouvel utilisateur"""
    if created:
        # Créer un profil avec rôle Lecteur par défaut
        try:
            default_role = Role.objects.get(name=Role.LECTEUR)
        except Role.DoesNotExist:
            # Si pas de rôle, en créer un
            default_role = Role.objects.create(
                name=Role.LECTEUR,
                description="Accès en lecture seule"
            )
        
        UserProfile.objects.create(user=instance, role=default_role)


# Ajouter une propriété 'role' sur le modèle User pour accès facile
def get_user_role(self):
    """Obtenir le rôle de l'utilisateur"""
    if hasattr(self, 'profile'):
        return self.profile.role
    return None

User.add_to_class('role', property(get_user_role))
