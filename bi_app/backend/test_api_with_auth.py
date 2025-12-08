#!/usr/bin/env python
"""
Frontend/Backend API Integration Test - WITH AUTHENTICATION
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
import requests

# Setup Django BEFORE importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_status(status, message, details=""):
    icon = "✓" if status else "✗"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{icon}{Colors.END} {message}")
    if details:
        print(f"  {Colors.CYAN}→ {details}{Colors.END}")

def create_test_user():
    """Create or get test user"""
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"{Colors.GREEN}✓{Colors.END} Created test user")
    return user

def get_jwt_token(user):
    """Generate JWT token for user"""
    try:
        refresh = AccessToken.for_user(user)
        return str(refresh)
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} Failed to generate JWT token: {str(e)}")
        return None

def test_endpoint(endpoint, token, params=None):
    """Test API endpoint with JWT authentication"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    try:
        if params:
            response = requests.get(url, headers=headers, params=params, timeout=5)
        else:
            response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return True, response.status_code, data
        else:
            return False, response.status_code, response.text
    except Exception as e:
        return False, None, str(e)

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   Frontend/Backend API Integration Test (with JWT Auth)          ║")
    print("║   Testing Dashboard Endpoints with Authentication                ║")
    print(f"║   {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<60} ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    total_tests = 0
    passed_tests = 0
    
    # ===== SETUP AUTHENTICATION =====
    print_section("1. SETUP & AUTHENTICATION")
    
    user = create_test_user()
    print_status(user is not None, "Test user ready", f"username: {user.username}")
    
    token = get_jwt_token(user)
    print_status(token is not None, "JWT token generated", f"token length: {len(token) if token else 0}")
    
    if not token:
        print(f"\n{Colors.RED}Cannot continue without valid token{Colors.END}\n")
        return 1
    
    # ===== TEST IMPLANTATION SUIVI =====
    print_section("2. IMPLANTATION SUIVI ENDPOINTS")
    
    endpoints = [
        ("/implantation-suivi/", None, "List all implantations"),
        ("/implantation-suivi/summary/", None, "Implantation summary"),
        ("/implantation-suivi/", {"zone_id": "1"}, "Filter by zone"),
        ("/implantation-suivi/", {"ordering": "-annee"}, "Sort by year"),
    ]
    
    for endpoint, params, desc in endpoints:
        total_tests += 1
        success, status_code, data = test_endpoint(endpoint, token, params)
        
        if success:
            passed_tests += 1
            if isinstance(data, dict) and 'results' in data:
                count = len(data.get('results', []))
                print_status(True, f"{desc}", f"HTTP {status_code}, {count} results")
            else:
                print_status(True, f"{desc}", f"HTTP {status_code}")
        else:
            print_status(False, f"{desc}", f"HTTP {status_code} - {data if status_code else 'Connection error'}")
    
    # ===== TEST INDEMNISATIONS =====
    print_section("3. INDEMNISATIONS ENDPOINTS")
    
    endpoints = [
        ("/indemnisations/", None, "List all indemnisations"),
        ("/indemnisations/summary/", None, "Indemnisations summary"),
        ("/indemnisations/", {"statut": "ACCEPTEE"}, "Filter by status"),
    ]
    
    for endpoint, params, desc in endpoints:
        total_tests += 1
        success, status_code, data = test_endpoint(endpoint, token, params)
        
        if success:
            passed_tests += 1
            if isinstance(data, dict) and 'results' in data:
                count = len(data.get('results', []))
                print_status(True, f"{desc}", f"HTTP {status_code}, {count} results")
            else:
                print_status(True, f"{desc}", f"HTTP {status_code}")
        else:
            print_status(False, f"{desc}", f"HTTP {status_code} - {str(data)[:50]}")
    
    # ===== TEST EMPLOIS CREES =====
    print_section("4. EMPLOIS CREES ENDPOINTS")
    
    endpoints = [
        ("/emplois-crees/", None, "List all emplois créés"),
        ("/emplois-crees/summary/", None, "Emplois créés summary"),
    ]
    
    for endpoint, params, desc in endpoints:
        total_tests += 1
        success, status_code, data = test_endpoint(endpoint, token, params)
        
        if success:
            passed_tests += 1
            if isinstance(data, dict) and 'results' in data:
                count = len(data.get('results', []))
                print_status(True, f"{desc}", f"HTTP {status_code}, {count} results")
            else:
                print_status(True, f"{desc}", f"HTTP {status_code}")
        else:
            print_status(False, f"{desc}", f"HTTP {status_code}")
    
    # ===== TEST CREANCES AGEES =====
    print_section("5. CREANCES AGEES ENDPOINTS")
    
    endpoints = [
        ("/creances-agees/", None, "List all créances âgées"),
        ("/creances-agees/summary/", None, "Créances âgées summary"),
    ]
    
    for endpoint, params, desc in endpoints:
        total_tests += 1
        success, status_code, data = test_endpoint(endpoint, token, params)
        
        if success:
            passed_tests += 1
            if isinstance(data, dict) and 'results' in data:
                count = len(data.get('results', []))
                print_status(True, f"{desc}", f"HTTP {status_code}, {count} results")
            else:
                print_status(True, f"{desc}", f"HTTP {status_code}")
        else:
            print_status(False, f"{desc}", f"HTTP {status_code}")
    
    # ===== RESPONSE STRUCTURE VALIDATION =====
    print_section("6. RESPONSE FORMAT VALIDATION")
    
    total_tests += 1
    success, status_code, data = test_endpoint("/implantation-suivi/", token)
    
    if success and isinstance(data, dict):
        required_keys = ['count', 'next', 'previous', 'results']
        has_structure = all(key in data for key in required_keys)
        
        if has_structure:
            passed_tests += 1
            print_status(True, "Pagination structure", f"✓ count, next, previous, results")
        else:
            missing = [k for k in required_keys if k not in data]
            print_status(False, "Pagination structure", f"Missing: {missing}")
    else:
        print_status(False, "Pagination structure", f"Invalid response format")
    
    # ===== DATA SAMPLE VALIDATION =====
    print_section("7. SAMPLE DATA VALIDATION")
    
    total_tests += 1
    success, status_code, data = test_endpoint("/implantation-suivi/?limit=1", token)
    
    if success and isinstance(data, dict) and data.get('results'):
        item = data['results'][0]
        required_fields = ['zone_id', 'annee', 'mois', 'nombre_implantations']
        has_fields = all(field in item for field in required_fields)
        
        if has_fields:
            passed_tests += 1
            print_status(True, "Data fields", f"✓ All required fields present")
            print(f"  Sample data: {Colors.CYAN}{json.dumps(item, ensure_ascii=False, indent=2)[:200]}...{Colors.END}")
        else:
            missing = [f for f in required_fields if f not in item]
            print_status(False, "Data fields", f"Missing: {missing}")
    else:
        print_status(False, "Data sample", "No results returned")
    
    # ===== FRONTEND SETUP INSTRUCTIONS =====
    print_section("8. FRONTEND INTEGRATION SETUP")
    
    print(f"{Colors.BOLD}Update bi_app/frontend/src/hooks/useDashboard.ts:{Colors.END}\n")
    
    config = f"""
// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// In useApi hook, add authorization:
const headers = {{
  'Authorization': `Bearer ${{token}}`,  // Get from localStorage or auth context
  'Content-Type': 'application/json',
}};
"""
    
    print(Colors.CYAN + config + Colors.END)
    
    # ===== LOGIN ENDPOINT TEST =====
    print_section("9. AUTHENTICATION ENDPOINTS")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/token/",
            json={"username": "testuser", "password": "testpass123"},
            timeout=5
        )
        
        total_tests += 1
        if response.status_code == 200:
            passed_tests += 1
            token_data = response.json()
            print_status(True, "JWT Token endpoint (/api/token/)", 
                        f"✓ Returns access & refresh tokens")
        else:
            print_status(False, "JWT Token endpoint", f"HTTP {response.status_code}")
    except Exception as e:
        print_status(False, "JWT Token endpoint", str(e))
    
    # ===== SUMMARY =====
    print_section("FINAL SUMMARY")
    
    print(f"  {Colors.BOLD}Total Tests:{Colors.END} {total_tests}")
    print(f"  {Colors.GREEN}{Colors.BOLD}Passed:{Colors.END} {passed_tests}")
    print(f"  {Colors.RED}{Colors.BOLD}Failed:{Colors.END} {total_tests - passed_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n  Success Rate: {Colors.BOLD}{success_rate:.1f}%{Colors.END}")
    
    if success_rate == 100:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
        print(f"  Frontend can now connect to backend.\n")
    else:
        print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Check above for details.{Colors.END}\n")
    
    return 0 if passed_tests == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
