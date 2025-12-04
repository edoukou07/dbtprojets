"""
Test script for new compliance endpoints with enterprise dimensions
Tests Phase 1 improvements: raison_sociale, forme_juridique, domaine_activite, categorie_domaine
"""
import requests
import json
from datetime import datetime
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
ANNEE = datetime.now().year

# Get authentication token
def get_auth_token():
    """Get or create authentication token for testing"""
    User = get_user_model()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test_api_compliance',
        defaults={
            'email': 'test_compliance@sigeti.com',
            'is_staff': True,
            'is_active': True
        }
    )
    
    if created:
        user.set_password('test123456')
        user.save()
        print(f"[OK] Created test user: {user.username}")
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f"[OK] Created new token for user: {user.username}")
    
    return token.key

# Authentication headers - Use hardcoded token from test_api user
AUTH_TOKEN = "6b6ddbda652f1c007215f84737959215a98cc764"
headers = {"Authorization": f"Token {AUTH_TOKEN}"}
print(f"[OK] Authentication configured with token: {AUTH_TOKEN[:20]}...\n")

def test_endpoint(name, url, params=None):
    """Test an endpoint and display results"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Status: {response.status_code}")
            print(f"Response data:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])  # First 1000 chars
            if isinstance(data, list):
                print(f"\n📊 Total records: {len(data)}")
            return True
        else:
            print(f"[ERROR] Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("TESTING NEW COMPLIANCE API ENDPOINTS - PHASE 1")
    print("Enterprise Dimensions: raison_sociale, forme_juridique, domaine_activite, categorie_domaine")
    print("="*80)
    
    results = {}
    
    # Test existing endpoints first
    print("\n" + "="*80)
    print("1. TESTING EXISTING ENDPOINTS (baseline)")
    print("="*80)
    
    results['conventions_summary'] = test_endpoint(
        "Conventions Summary",
        f"{BASE_URL}/compliance-compliance/conventions_summary/",
        {"annee": ANNEE}
    )
    
    results['approval_delays_summary'] = test_endpoint(
        "Approval Delays Summary",
        f"{BASE_URL}/compliance-compliance/approval_delays_summary/",
        {"annee": ANNEE}
    )
    
    # Test NEW endpoints for conventions
    print("\n" + "="*80)
    print("2. TESTING NEW ENDPOINTS - CONVENTIONS BY ENTERPRISE DIMENSIONS")
    print("="*80)
    
    results['conventions_by_domaine'] = test_endpoint(
        "Conventions by Domaine d'Activité (detailed)",
        f"{BASE_URL}/compliance-compliance/conventions_by_domaine/",
        {"annee": ANNEE}
    )
    
    results['conventions_by_categorie_domaine'] = test_endpoint(
        "Conventions by Catégorie Domaine (aggregated)",
        f"{BASE_URL}/compliance-compliance/conventions_by_categorie_domaine/",
        {"annee": ANNEE}
    )
    
    results['conventions_by_forme_juridique'] = test_endpoint(
        "Conventions by Forme Juridique",
        f"{BASE_URL}/compliance-compliance/conventions_by_forme_juridique/",
        {"annee": ANNEE}
    )
    
    results['conventions_by_entreprise'] = test_endpoint(
        "Conventions by Entreprise (raison sociale)",
        f"{BASE_URL}/compliance-compliance/conventions_by_entreprise/",
        {"annee": ANNEE, "limit": 20}
    )
    
    # Test NEW endpoints for approval delays
    print("\n" + "="*80)
    print("3. TESTING NEW ENDPOINTS - APPROVAL DELAYS BY ENTERPRISE DIMENSIONS")
    print("="*80)
    
    results['approval_delays_by_domaine'] = test_endpoint(
        "Approval Delays by Domaine d'Activité",
        f"{BASE_URL}/compliance-compliance/approval_delays_by_domaine/",
        {"annee": ANNEE}
    )
    
    results['approval_delays_by_forme_juridique'] = test_endpoint(
        "Approval Delays by Forme Juridique",
        f"{BASE_URL}/compliance-compliance/approval_delays_by_forme_juridique/",
        {"annee": ANNEE}
    )
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n[OK] Passed: {passed}/{total}")
    print(f"[FAILED] Failed: {total - passed}/{total}")
    
    print("\nDetailed results:")
    for endpoint, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} - {endpoint}")
    
    print("\n" + "="*80)
    print("NEW API CAPABILITIES - PHASE 1")
    print("="*80)
    print("""
    NOUVELLES ANALYSES DISPONIBLES:
    
    1. Conventions par Domaine d'Activité:
       - Taux de validation par secteur
       - Délai moyen par secteur
       - Distribution par catégorie (INDUSTRIE, SERVICES, TECH, etc.)
    
    2. Conventions par Forme Juridique:
       - Performance SARL vs EURL vs autres
       - Taux de rejet par forme juridique
       - Délai de traitement par type d'entreprise
    
    3. Conventions par Entreprise:
       - Top entreprises par volume
       - Performance individuelle
       - Traçabilité complète
    
    4. Délais d'Approbation:
       - Délai moyen par domaine d'activité
       - Délai médian par forme juridique
       - Temps d'attente par catégorie
    
    📊 ENDPOINTS DISPONIBLES:
       GET /api/compliance-compliance/conventions_by_domaine/?annee=2025
       GET /api/compliance-compliance/conventions_by_categorie_domaine/?annee=2025
       GET /api/compliance-compliance/conventions_by_forme_juridique/?annee=2025
       GET /api/compliance-compliance/conventions_by_entreprise/?annee=2025&limit=50
       GET /api/compliance-compliance/approval_delays_by_domaine/?annee=2025
       GET /api/compliance-compliance/approval_delays_by_forme_juridique/?annee=2025
    """)
    
    print("="*80)

if __name__ == "__main__":
    main()
