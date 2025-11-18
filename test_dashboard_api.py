#!/usr/bin/env python3
"""
Test Dashboard API Endpoints - Vérifier que les bonnes valeurs sont retournées
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

# Test credentials
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def get_jwt_token():
    """Obtenir un token JWT"""
    url = f"http://localhost:8000/api/auth/jwt/token/"
    payload = {
        "username": "admin",
        "password": "admin"
    }
    
    response = requests.post(url, json=payload)
    print(f"  Token Request: {response.status_code}")
    if response.status_code != 200:
        print(f"  Response: {response.text[:200]}")
    if response.status_code == 200:
        data = response.json()
        return data.get('access') or data.get('token')
    else:
        # Try alternative endpoint
        url2 = f"http://localhost:8000/api/auth/jwt/login/"
        response = requests.post(url2, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get('access') or data.get('token')
        else:
            print(f"❌ Erreur obtention token: {response.status_code} - {response.text[:100]}")
            return None

def make_api_request(endpoint, token=None):
    """Faire une requête API avec authentification"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {}
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ {endpoint}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur {endpoint}: {e}")
        return None

def main():
    print("=" * 70)
    print("TEST DES ENDPOINTS API DASHBOARD")
    print("=" * 70)
    
    # Get token
    print("\n1. Obtention du token JWT...")
    token = get_jwt_token()
    if not token:
        print("❌ Impossible d'obtenir un token. Les serveurs Django/API tournent-ils ?")
        sys.exit(1)
    print(f"✅ Token obtenu")
    
    # Test endpoints
    print("\n2. TEST DES ENDPOINTS:\n")
    
    # Financier
    print("📊 FINANCIER SUMMARY:")
    data = make_api_request("financier/summary/", token)
    if data:
        print(f"  CA Total: {data.get('ca_total', 'N/A'):,} FCFA")
        print(f"  CA Payé: {data.get('ca_paye', 'N/A'):,} FCFA")
        print(f"  Taux Paiement: {data.get('taux_paiement_moyen', 'N/A')}%")
        expected_ca = 3_132_136_002
        if data.get('ca_total') == expected_ca:
            print(f"  ✅ CA Total CORRECT")
        else:
            print(f"  ❌ CA Total INCORRECT (attendu {expected_ca:,})")
    
    # Occupation
    print("\n📍 OCCUPATION SUMMARY:")
    data = make_api_request("occupation/summary/", token)
    if data:
        print(f"  Total Lots: {data.get('total_lots', 'N/A')}")
        print(f"  Lots Disponibles: {data.get('lots_disponibles', 'N/A')}")
        print(f"  Lots Attribués: {data.get('lots_attribues', 'N/A')}")
        print(f"  Taux Occupation: {data.get('taux_occupation_moyen', 'N/A')}%")
        print(f"  Nombre de Zones: {data.get('nombre_zones', 'N/A')}")
        if data.get('nombre_zones') == 5:
            print(f"  ✅ Nombre de Zones CORRECT (5)")
        else:
            print(f"  ❌ Nombre de Zones INCORRECT (attendu 5, got {data.get('nombre_zones')})")
    
    # Operationnel
    print("\n⚙️  OPERATIONNEL SUMMARY:")
    data = make_api_request("operationnel/summary/", token)
    if data:
        print(f"  Total Collectes: {data.get('total_collectes', 'N/A')}")
        print(f"  Total Demandes: {data.get('total_demandes', 'N/A')}")
        print(f"  Total Approuvées: {data.get('total_approuvees', 'N/A')}")
        print(f"  Taux Recouvrement Moyen: {data.get('taux_recouvrement_moyen', 'N/A')}%")
        print(f"  Total Factures: {data.get('total_factures', 'N/A')}")
        
        # Verify key metrics
        if data.get('total_demandes') == 23:
            print(f"  ✅ Total Demandes CORRECT (23)")
        else:
            print(f"  ❌ Total Demandes INCORRECT (attendu 23, got {data.get('total_demandes')})")
        
        taux_recouvrement = data.get('taux_recouvrement_moyen')
        if taux_recouvrement and abs(float(taux_recouvrement) - 32.89) < 0.1:
            print(f"  ✅ Taux Recouvrement CORRECT (~32.89%)")
        else:
            print(f"  ❌ Taux Recouvrement INCORRECT (attendu 32.89%, got {taux_recouvrement}%)")
    
    # Clients
    print("\n👥 CLIENTS SUMMARY:")
    data = make_api_request("clients/summary/", token)
    if data:
        print(f"  Total Clients: {data.get('total_clients', 'N/A')}")
        print(f"  CA Total: {data.get('ca_total', 'N/A'):,} FCFA")
        print(f"  Taux Paiement Moyen: {data.get('taux_paiement_moyen', 'N/A')}%")
        
        if data.get('total_clients') == 35:
            print(f"  ✅ Total Clients CORRECT (35)")
        else:
            print(f"  ❌ Total Clients INCORRECT (attendu 35, got {data.get('total_clients')})")
    
    print("\n" + "=" * 70)
    print("TEST TERMINÉ")
    print("=" * 70)

if __name__ == '__main__':
    main()
