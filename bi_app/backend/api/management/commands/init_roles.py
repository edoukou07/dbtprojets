"""
Script d'initialisation des rôles pour SIGETI BI
À exécuter après les migrations
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models_auth import Role, UserProfile


class Command(BaseCommand):
    help = 'Initialise les rôles par défaut et crée un utilisateur admin'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initialisation des rôles...')
        
        # Créer les rôles par défaut
        roles_data = [
            {
                'name': Role.ADMIN,
                'description': 'Administrateur système avec tous les droits',
                'permissions': {
                    'can_read': True,
                    'can_write': True,
                    'can_delete': True,
                    'can_manage_users': True,
                    'can_view_logs': True,
                }
            },
            {
                'name': Role.GESTIONNAIRE,
                'description': 'Gestionnaire avec droits de lecture et écriture',
                'permissions': {
                    'can_read': True,
                    'can_write': True,
                    'can_delete': False,
                    'can_manage_users': False,
                    'can_view_logs': False,
                }
            },
            {
                'name': Role.LECTEUR,
                'description': 'Lecteur avec accès en lecture seule',
                'permissions': {
                    'can_read': True,
                    'can_write': False,
                    'can_delete': False,
                    'can_manage_users': False,
                    'can_view_logs': False,
                }
            },
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Rôle créé: {role.name}'))
            else:
                self.stdout.write(f'  Rôle existant: {role.name}')
        
        # Créer un admin par défaut si pas d'utilisateur
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('\nCréation d\'un utilisateur admin par défaut...')
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@sigeti.com',
                password='admin123',  # À CHANGER EN PRODUCTION!
                first_name='Admin',
                last_name='SIGETI'
            )
            
            # Créer le profil admin
            admin_role = Role.objects.get(name=Role.ADMIN)
            UserProfile.objects.create(
                user=admin_user,
                role=admin_role,
                department='IT',
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Admin créé: username=admin, password=admin123'))
            self.stdout.write(self.style.WARNING('⚠ CHANGEZ LE MOT DE PASSE EN PRODUCTION!'))
        
        # Assigner le rôle Lecteur aux utilisateurs sans profil
        users_without_profile = User.objects.filter(profile__isnull=True)
        if users_without_profile.exists():
            self.stdout.write(f'\nAssignation du rôle Lecteur à {users_without_profile.count()} utilisateurs...')
            lecteur_role = Role.objects.get(name=Role.LECTEUR)
            
            for user in users_without_profile:
                UserProfile.objects.create(
                    user=user,
                    role=lecteur_role,
                    is_active=True
                )
                self.stdout.write(f'  ✓ Profil créé pour: {user.username}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initialisation terminée!'))
        self.stdout.write('\nRésumé des rôles:')
        for role in Role.objects.all():
            count = role.users.count()
            self.stdout.write(f'  - {role.name}: {count} utilisateur(s)')
