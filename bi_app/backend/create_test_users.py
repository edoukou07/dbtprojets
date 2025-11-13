"""
Script pour créer des utilisateurs de test pour SIGETI BI
Exécuter: python manage.py shell < create_test_users.py
"""
from django.contrib.auth.models import User

# Liste des utilisateurs de test
test_users = [
    {
        'username': 'admin',
        'email': 'admin@sigeti.ci',
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'SIGETI',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'username': 'finance',
        'email': 'finance@sigeti.ci',
        'password': 'finance123',
        'first_name': 'Directeur',
        'last_name': 'Financier',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'operations',
        'email': 'ops@sigeti.ci',
        'password': 'ops123',
        'first_name': 'Directeur',
        'last_name': 'Opérations',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'direction',
        'email': 'direction@sigeti.ci',
        'password': 'direction123',
        'first_name': 'Directeur',
        'last_name': 'Général',
        'is_staff': False,
        'is_superuser': False,
    },
]

print("Création des utilisateurs de test...")
print("=" * 60)

for user_data in test_users:
    username = user_data['username']
    
    # Supprimer l'utilisateur s'il existe déjà
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
        print(f"✓ Utilisateur '{username}' existant supprimé")
    
    # Créer le nouvel utilisateur
    password = user_data.pop('password')
    user = User.objects.create_user(**user_data)
    user.set_password(password)
    user.save()
    
    print(f"✓ Utilisateur créé: {username}")
    print(f"  Email: {user_data['email']}")
    print(f"  Mot de passe: {password}")
    print(f"  Nom: {user_data['first_name']} {user_data['last_name']}")
    print(f"  Staff: {user_data['is_staff']}")
    print("-" * 60)

print("\n🎉 Tous les utilisateurs de test ont été créés avec succès!")
print("\nVous pouvez maintenant vous connecter avec:")
print("- admin@sigeti.ci / admin123 (Administrateur)")
print("- finance@sigeti.ci / finance123 (Finance)")
print("- ops@sigeti.ci / ops123 (Opérations)")
print("- direction@sigeti.ci / direction123 (Direction)")
