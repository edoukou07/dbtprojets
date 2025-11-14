import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

# Créer un client API
client = APIClient()

# Tester sans authentification
print("Test sans authentification:")
response = client.get('/api/clients/')
print(f"Status: {response.status_code}")
print(f"Response: {response.data if hasattr(response, 'data') else 'No data'}\n")

# Créer ou récupérer un utilisateur
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"Utilisateur créé: {user.username}")
else:
    print(f"Utilisateur existant: {user.username}")

# Se connecter
from rest_framework.authtoken.models import Token
token, _ = Token.objects.get_or_create(user=user)
print(f"Token: {token.key}\n")

# Tester avec authentification
print("Test avec authentification:")
client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
response = client.get('/api/clients/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Nombre de clients: {len(response.data)}")
    if len(response.data) > 0:
        print(f"Premier client: {response.data[0]}")
else:
    print(f"Erreur: {response.data if hasattr(response, 'data') else 'No data'}")
