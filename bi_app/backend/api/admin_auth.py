"""
Admin configuration pour les modèles d'authentification
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models_auth import Role, UserProfile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Administration des rôles
    """
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description')
        }),
        ('Permissions avancées', {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Administration des profils utilisateurs
    """
    list_display = ('user', 'role', 'department', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'department')
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip')
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'role')
        }),
        ('Informations complémentaires', {
            'fields': ('department', 'phone', 'is_active')
        }),
        ('Informations système', {
            'fields': ('last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Inline pour afficher le profil dans l'admin User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'
    fields = ('role', 'department', 'phone', 'is_active')


# Étendre l'admin User existant
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    
    def get_role(self, obj):
        """Afficher le rôle dans la liste"""
        return obj.role.name if hasattr(obj, 'profile') and obj.profile else 'Aucun'
    get_role.short_description = 'Rôle'


# Réenregistrer UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
