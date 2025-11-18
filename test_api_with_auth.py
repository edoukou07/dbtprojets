#!/usr/bin/env python3
import requests
import json
from django.conf import settings
import sys
import os

# Setup Django
sys.path.insert(0, r'c:\Users\hynco\Desktop\DWH_SIG\bi_app\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')

import django
django.setup()

from django.contrib.auth.models import User

# Create or get test user
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
    print(f"✅ Created user: {user.username}")

# Get token
from rest_framework.authtoken.models import Token
token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key[:20]}...\n")

# Test the API
import requests
headers = {'Authorization': f'Token {token.key}'}
url = 'http://localhost:8000/api/operationnel/summary/'

print("=== TEST API /api/operationnel/summary/ ===\n")

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    print("✅ Réponse Reçue:\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Vérifications spécifiques
    print("\n\n=== VÉRIFICATIONS ===")
    print(f"Total Demandes: {data.get('total_demandes')} (Attendu: 23)")
    print(f"Demandes Approuvées: {data.get('total_approuvees')} (Attendu: 6)")
    print(f"Taux Recouvrement Moyen: {data.get('taux_recouvrement_moyen')}% (Après corr: ~32.89%)")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur: {e}")
except json.JSONDecodeError as e:
    print(f"❌ Erreur JSON: {e}")
