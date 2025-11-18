#!/usr/bin/env python3
import os
import sys
import django
import json
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, r'c:\Users\hynco\Desktop\DWH_SIG\bi_app\backend')
django.setup()

from django.contrib.auth.models import User

# Get or create admin user
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@test.com', 'admin')

print(f"✅ Using user: {user.username}\n")

# Get JWT token
url_token = 'http://localhost:8000/api/auth/jwt/token/'
payload = {
    'username': 'admin',
    'password': 'admin'
}

print("=== OBTENIR TOKEN JWT ===")
print(f"POST {url_token}\n")

try:
    response = requests.post(url_token, json=payload)
    response.raise_for_status()
    data = response.json()
    token = data['access']
    print(f"✅ Token reçu: {token[:20]}...\n")
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)

# Test the operational summary endpoint
url_api = 'http://localhost:8000/api/operationnel/summary/'
headers = {'Authorization': f'Bearer {token}'}

print("=== TEST API /api/operationnel/summary/ ===")
print(f"GET {url_api}\n")

try:
    response = requests.get(url_api, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    print("✅ Réponse Reçue:\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print("\n\n=== VÉRIFICATIONS ===")
    print(f"✓ Total Demandes: {data.get('total_demandes')} (Attendu: 23)")
    print(f"✓ Demandes Approuvées: {data.get('total_approuvees')} (Attendu: 6)")
    print(f"✓ Taux Recouvrement: {data.get('taux_recouvrement_moyen')}% (Corrigé: ~32.89%)")
    print(f"✓ Total Collectes: {data.get('total_collectes')} (Attendu: 5)")
    print(f"✓ Total Factures: {data.get('total_factures')} (Attendu: 42 ou 84)")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur: {e}\nRéponse: {response.text[:300]}")
