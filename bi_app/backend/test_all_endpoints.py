#!/usr/bin/env python3
"""
Test de tous les endpoints API pour vérifier les métriques des dashboards
"""
import os
import sys
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, r'c:\Users\hynco\Desktop\DWH_SIG\bi_app\backend')
django.setup()

from django.contrib.auth.models import User

# Get or create admin
user, _ = User.objects.get_or_create(username='admin')
user.set_password('admin')
user.is_superuser = True
user.is_staff = True
user.save()

# Get JWT token
payload = {'username': 'admin', 'password': 'admin'}
response = requests.post('http://localhost:8000/api/auth/jwt/token/', json=payload)
token = response.json()['access']
headers = {'Authorization': f'Bearer {token}'}

print("=" * 90)
print("VÉRIFICATION DE TOUS LES ENDPOINTS API - DASHBOARDS")
print("=" * 90)

# FINANCIER
print("\n📊 FINANCIER - /api/financier/summary/")
print("-" * 90)
try:
    res = requests.get('http://localhost:8000/api/financier/summary/', headers=headers)
    res.raise_for_status()
    data = res.json()
    print(f"  ✓ CA Total:              {data.get('ca_total', 'N/A'):>20}")
    print(f"  ✓ CA Payé:               {data.get('ca_paye', 'N/A'):>20}")
    print(f"  ✓ CA Impayé:             {data.get('ca_impaye', 'N/A'):>20}")
    print(f"  ✓ Taux Paiement:         {data.get('taux_paiement_pct', 'N/A'):>20}%")
    print(f"  ✓ Délai Moyen Paiement:  {data.get('delai_moyen_paiement', 'N/A'):>20} jours")
except Exception as e:
    print(f"  ❌ Erreur: {e}")

# OCCUPATION
print("\n📍 OCCUPATION - /api/occupation/summary/")
print("-" * 90)
try:
    res = requests.get('http://localhost:8000/api/occupation/summary/', headers=headers)
    res.raise_for_status()
    data = res.json()
    print(f"  ✓ Total Lots:            {data.get('total_lots', 'N/A'):>20}")
    print(f"  ✓ Lots Disponibles:      {data.get('lots_disponibles', 'N/A'):>20}")
    print(f"  ✓ Lots Attribués:        {data.get('lots_attribues', 'N/A'):>20}")
    print(f"  ✓ Superficie Totale:     {data.get('superficie_totale', 'N/A'):>20} m²")
    print(f"  ✓ Taux Occupation:       {data.get('taux_occupation_moyen', 'N/A'):>20}%")
    print(f"  ✓ Zones Industrielles:   {data.get('nombre_zones', 'N/A'):>20}")
except Exception as e:
    print(f"  ❌ Erreur: {e}")

# CLIENTS
print("\n👥 CLIENTS - /api/clients/summary/")
print("-" * 90)
try:
    res = requests.get('http://localhost:8000/api/clients/summary/', headers=headers)
    res.raise_for_status()
    data = res.json()
    print(f"  ✓ Total Clients:         {data.get('total_clients', 'N/A'):>20}")
    print(f"  ✓ CA Portefeuille:       {data.get('ca_portefeuille', 'N/A'):>20}")
    print(f"  ✓ Créances Totales:      {data.get('creances_totales', 'N/A'):>20}")
    print(f"  ✓ Taux Paiement Moyen:   {data.get('taux_paiement_moyen', 'N/A'):>20}%")
except Exception as e:
    print(f"  ❌ Erreur: {e}")

# OPÉRATIONNEL
print("\n⚙️  OPÉRATIONNEL - /api/operationnel/summary/")
print("-" * 90)
try:
    res = requests.get('http://localhost:8000/api/operationnel/summary/', headers=headers)
    res.raise_for_status()
    data = res.json()
    print(f"  ✓ Total Collectes:       {data.get('total_collectes', 'N/A'):>20}")
    print(f"  ✓ Taux Clôture:          {data.get('taux_cloture_moyen', 'N/A'):>20}%")
    print(f"  ✓ Taux Recouvrement:     {data.get('taux_recouvrement_moyen', 'N/A'):>20}% ⭐")
    print(f"  ✓ Total Demandes:        {data.get('total_demandes', 'N/A'):>20}")
    print(f"  ✓ Demandes Approuvées:   {data.get('total_approuvees', 'N/A'):>20}")
    print(f"  ✓ Taux Approbation:      {data.get('taux_approbation_moyen', 'N/A'):>20}%")
    print(f"  ✓ Total Factures:        {data.get('total_factures', 'N/A'):>20}")
except Exception as e:
    print(f"  ❌ Erreur: {e}")

print("\n" + "=" * 90)
print("✅ TOUS LES ENDPOINTS TESTÉS")
print("=" * 90)
