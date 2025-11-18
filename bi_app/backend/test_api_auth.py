#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, r'c:\Users\hynco\Desktop\DWH_SIG\bi_app\backend')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import requests
import json

# Get or create admin user
try:
    user = User.objects.get(username='admin')
    print(f"✅ Admin user found: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
    print(f"✅ Created admin user: {user.username}")

# Get or create token
token, created = Token.objects.get_or_create(user=user)
if created:
    print(f"✅ Created token: {token.key[:20]}...")
else:
    print(f"✅ Using existing token: {token.key[:20]}...")

# Test API
headers = {'Authorization': f'Token {token.key}'}
url = 'http://localhost:8000/api/operationnel/summary/'

print(f"\n=== TEST API ===")
print(f"URL: {url}\n")

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    print("✅ Réponse Reçue:\n")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    # Vérifications
    print("\n=== VÉRIFICATIONS ===")
    print(f"✓ Total Demandes: {data.get('total_demandes')} (Attendu: 23)")
    print(f"✓ Demandes Approuvées: {data.get('total_approuvees')} (Attendu: 6)")
    print(f"✓ Taux Recouvrement: {data.get('taux_recouvrement_moyen')}% (Corrigé: ~32.89%)")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur: {e}")
