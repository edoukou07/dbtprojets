#!/usr/bin/env python3
"""
Comprehensive endpoint test to verify all API responses and Dashboard requirements
"""
import requests
import json
from datetime import datetime
import sys

# Set encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

BASE_URL = "http://localhost:8000/api"

# First, get a fresh JWT token
def get_auth_headers():
    """Authenticate and get JWT token"""
    # Try different credentials
    credentials = [
        {'username': 'admin', 'password': 'Admin@123'},
        {'username': 'admin@sigeti.ci', 'password': 'Admin@123'},
        {'username': 'admin', 'password': 'admin'},
    ]
    
    for creds in credentials:
        response = requests.post(
            f"{BASE_URL}/auth/jwt/login/",
            json=creds
        )
        
        if response.status_code == 200:
            token = response.json()['access']
            print(f"+ JWT Token obtained with {creds['username']}: {token[:50]}...")
            
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
    
    print(f"- Authentication failed with all credentials")
    return None

HEADERS = get_auth_headers()
if not HEADERS:
    exit(1)

def test_endpoint(name, endpoint):
    """Test a single endpoint and return results"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse Structure:")
            print(json.dumps(data, indent=2, default=str))
            
            # Highlight key metrics
            print(f"\n--- KEY METRICS ---")
            for key in data.keys():
                if not isinstance(data[key], (list, dict)):
                    print(f"{key}: {data[key]}")
            
            return data
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None

def main():
    print("COMPREHENSIVE API ENDPOINT TEST")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Base URL: {BASE_URL}")
    
    # Test all endpoints
    results = {}
    
    print("\n" + "="*60)
    print("1. FINANCIER ENDPOINT")
    print("="*60)
    results['financier'] = test_endpoint("Financier Summary", "/financier/summary/")
    
    print("\n" + "="*60)
    print("2. OCCUPATION ENDPOINT")
    print("="*60)
    results['occupation'] = test_endpoint("Occupation Summary", "/occupation/summary/")
    
    print("\n" + "="*60)
    print("3. CLIENTS ENDPOINT")
    print("="*60)
    results['clients'] = test_endpoint("Clients Summary", "/clients/summary/")
    
    print("\n" + "="*60)
    print("4. OPERATIONNEL ENDPOINT")
    print("="*60)
    results['operationnel'] = test_endpoint("Operationnel Summary", "/operationnel/summary/")
    
    # Summary report
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)
    
    endpoints_needed = {
        'financier': ['ca_total', 'ca_paye', 'ca_impaye', 'taux_recouvrement_moyen', 'taux_paiement_pct'],
        'occupation': ['total_lots', 'lots_disponibles', 'lots_attribues', 'taux_occupation_moyen', 'nombre_zones'],
        'clients': ['total_clients', 'ca_total', 'ca_paye', 'ca_impaye', 'taux_paiement_moyen'],
        'operationnel': ['total_collectes', 'taux_recouvrement_moyen', 'total_demandes', 'demandes_approuvees']
    }
    
    for endpoint_name, required_fields in endpoints_needed.items():
        print(f"\n{endpoint_name.upper()}:")
        data = results.get(endpoint_name, {})
        
        if not data:
            print("  - NO DATA")
            continue
            
        for field in required_fields:
            value = data.get(field, "N/A")
            status = "[OK]" if value != "N/A" else "[MISSING]"
            print(f"  {status} {field}: {value}")

if __name__ == "__main__":
    main()
