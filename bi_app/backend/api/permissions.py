"""
Permissions personnalisées pour SIGETI BI
Système de rôles: Admin, Gestionnaire, Lecteur
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission pour les administrateurs uniquement.
    Accès complet: lecture, écriture, suppression.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and
            request.user.role.name == 'Admin'
        )


class IsGestionnaire(permissions.BasePermission):
    """
    Permission pour les gestionnaires.
    Peut lire et modifier, mais pas supprimer.
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request.user, 'role'):
            return False
            
        # Admin a tous les droits
        if request.user.role.name == 'Admin':
            return True
            
        # Gestionnaire peut lire et modifier
        if request.user.role.name == 'Gestionnaire':
            return request.method in ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH']
            
        return False


class IsLecteur(permissions.BasePermission):
    """
    Permission pour les lecteurs.
    Lecture seule (GET, HEAD, OPTIONS).
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request.user, 'role'):
            return False
            
        # Admin et Gestionnaire ont tous les droits
        if request.user.role.name in ['Admin', 'Gestionnaire']:
            return True
            
        # Lecteur en lecture seule
        if request.user.role.name == 'Lecteur':
            return request.method in permissions.SAFE_METHODS
            
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin: tous droits
    Autres utilisateurs authentifiés: lecture seule
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture réservée aux admins
        return (
            hasattr(request.user, 'role') and
            request.user.role.name == 'Admin'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission pour modifier uniquement ses propres objets.
    Lecture pour tous les utilisateurs authentifiés.
    """
    
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture uniquement pour le propriétaire ou admin
        if hasattr(request.user, 'role') and request.user.role.name == 'Admin':
            return True
            
        # Vérifier si l'objet a un champ 'user' ou 'created_by'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
            
        return False
