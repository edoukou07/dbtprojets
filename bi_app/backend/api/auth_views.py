"""
Vues d'authentification JWT pour SIGETI BI
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from .models_auth import UserProfile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personnalisé pour ajouter des infos utilisateur au token
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Ajouter des infos supplémentaires
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        
        # Ajouter le rôle si disponible
        if hasattr(user, 'profile'):
            data['user']['role'] = user.profile.role.name
            data['user']['department'] = user.profile.department
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue personnalisée pour obtenir un token JWT
    """
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST')  # 5 tentatives par minute
def login_view(request):
    """
    Connexion avec JWT
    Rate limited: 5 tentatives par minute par IP
    Accepte username ou email
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(f"DEBUG Login attempt - username: {username}, has_password: {bool(password)}")
    
    if not username or not password:
        print(f"DEBUG Missing credentials - username: {username}, password: {'***' if password else 'None'}")
        return Response(
            {'error': 'Username/email et password requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Essayer d'authentifier avec le username d'abord
    user = authenticate(username=username, password=password)
    print(f"DEBUG First auth attempt: {user}")
    
    # Si échec et que username contient @, essayer avec l'email
    if user is None and '@' in username:
        try:
            user_obj = User.objects.get(email=username)
            print(f"DEBUG Found user by email: {user_obj.username}")
            user = authenticate(username=user_obj.username, password=password)
            print(f"DEBUG Second auth attempt: {user}")
        except User.DoesNotExist:
            print(f"DEBUG No user found with email: {username}")
            pass
    
    if user is None:
        return Response(
            {'error': 'Identifiants invalides'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Compte désactivé'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Vérifier si le profil existe
    if hasattr(user, 'profile') and not user.profile.is_active:
        return Response(
            {'error': 'Profil désactivé'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Générer tokens
    refresh = RefreshToken.for_user(user)
    
    # Enregistrer l'IP de connexion
    if hasattr(user, 'profile'):
        user.profile.last_login_ip = request.META.get('REMOTE_ADDR')
        user.profile.save()
    
    response_data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }
    
    # Ajouter le rôle
    if hasattr(user, 'profile'):
        response_data['user']['role'] = user.profile.role.name
        response_data['user']['department'] = user.profile.department
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Déconnexion (blacklist le refresh token)
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response(
            {'message': 'Déconnexion réussie'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/h', method='POST')  # 3 inscriptions par heure
def register_view(request):
    """
    Inscription d'un nouveau utilisateur
    Rate limited: 3 inscriptions par heure par IP
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    # Validation
    if not username or not email or not password:
        return Response(
            {'error': 'Username, email et password requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username déjà utilisé'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email déjà utilisé'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Créer l'utilisateur
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # Le profil est créé automatiquement par le signal
    # avec le rôle Lecteur par défaut
    
    return Response(
        {
            'message': 'Utilisateur créé avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.profile.role.name
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Informations sur l'utilisateur connecté
    """
    user = request.user
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    }
    
    if hasattr(user, 'profile'):
        data['role'] = user.profile.role.name
        data['department'] = user.profile.department
        data['is_active'] = user.profile.is_active
    
    return Response(data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Mettre à jour le profil de l'utilisateur connecté
    """
    user = request.user
    
    # Mise à jour des champs User
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    if 'email' in request.data:
        user.email = request.data['email']
    
    user.save()
    
    # Mise à jour du profil
    if hasattr(user, 'profile'):
        profile = user.profile
        if 'department' in request.data:
            profile.department = request.data['department']
        if 'phone' in request.data:
            profile.phone = request.data['phone']
        profile.save()
    
    return Response(
        {'message': 'Profil mis à jour avec succès'},
        status=status.HTTP_200_OK
    )
