"""
Script de test pour vérifier l'authentification
"""

print("Test de l'authentification Django REST Framework")
print("=" * 60)

# 1. Vérifier les utilisateurs
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

users = User.objects.all()
print(f"\n✅ {users.count()} utilisateurs trouvés:")
for user in users:
    print(f"   - {user.email} (username: {user.username})")

# 2. Créer/récupérer les tokens
print("\n📝 Tokens d'authentification:")
for user in users:
    token, created = Token.objects.get_or_create(user=user)
    status = "créé" if created else "existant"
    print(f"   - {user.email}: {token.key} ({status})")

print("\n" + "=" * 60)
print("✅ Configuration terminée!")
print("\nPour tester avec curl:")
print('curl -H "Authorization: Token 48458d98c536a896979c723309cf83e7ce5259f9" http://localhost:8000/api/financier/summary/')
