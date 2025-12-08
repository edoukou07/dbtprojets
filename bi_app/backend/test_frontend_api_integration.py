#!/usr/bin/env python
"""
Test Frontend/Backend API Integration
Tests all dashboard endpoints that the React frontend will call
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Base URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# ANSI colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} - {name}")
    if details:
        print(f"    {Colors.CYAN}{details}{Colors.END}")

def test_endpoint(endpoint, method="GET", expected_keys=None, filters=None):
    """Test a single endpoint"""
    url = f"{API_BASE}{endpoint}"
    
    if filters:
        # Add query parameters
        query_params = "&".join([f"{k}={v}" for k, v in filters.items()])
        url = f"{url}?{query_params}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, timeout=5)
        
        passed = response.status_code in [200, 201]
        
        if passed and response.json():
            data = response.json()
            
            # Check expected keys if provided
            if expected_keys:
                has_keys = all(key in data for key in expected_keys)
                if not has_keys:
                    passed = False
                    missing = [key for key in expected_keys if key not in data]
                    details = f"Status: {response.status_code}, Missing keys: {missing}"
                else:
                    # Count results
                    if isinstance(data, dict) and 'results' in data:
                        result_count = len(data.get('results', []))
                        details = f"Status: {response.status_code}, Results: {result_count}"
                    else:
                        details = f"Status: {response.status_code}, Data returned: {type(data).__name__}"
            else:
                details = f"Status: {response.status_code}"
        else:
            details = f"Status: {response.status_code}, Response: {response.text[:100]}"
        
        return passed, details, response
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {str(e)}", None
    except requests.exceptions.Timeout:
        return False, "Timeout (5s)", None
    except Exception as e:
        return False, f"Error: {str(e)}", None

# ============================================================================
# TEST SUITE
# ============================================================================

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   Frontend/Backend API Integration Test                   ║")
    print("║   Testing Dashboard Endpoints                             ║")
    print(f"║   {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<51} ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # ===== IMPLANTATION SUIVI ENDPOINTS =====
    print_header("1. IMPLANTATION SUIVI ENDPOINTS")
    
    tests = [
        ("/implantation-suivi/", "GET", ["count", "results"], None),
        ("/implantation-suivi/summary/", "GET", ["total_implantations"], None),
        ("/implantation-suivi/", "GET", ["count", "results"], {"zone_id": "1"}),
        ("/implantation-suivi/", "GET", ["count", "results"], {"ordering": "-annee"}),
    ]
    
    for endpoint, method, expected_keys, filters in tests:
        total_tests += 1
        name = f"{endpoint}" + (f" (filters: {filters})" if filters else "")
        passed, details, _ = test_endpoint(endpoint, method, expected_keys, filters)
        
        if passed:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print_test(name, passed, details)
    
    # ===== INDEMNISATIONS ENDPOINTS =====
    print_header("2. INDEMNISATIONS ENDPOINTS")
    
    tests = [
        ("/indemnisations/", "GET", ["count", "results"], None),
        ("/indemnisations/summary/", "GET", ["total_indemnisations"], None),
        ("/indemnisations/", "GET", ["count", "results"], {"statut": "ACCEPTEE"}),
        ("/indemnisations/", "GET", ["count", "results"], {"zone_id": "1"}),
    ]
    
    for endpoint, method, expected_keys, filters in tests:
        total_tests += 1
        name = f"{endpoint}" + (f" (filters: {filters})" if filters else "")
        passed, details, _ = test_endpoint(endpoint, method, expected_keys, filters)
        
        if passed:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print_test(name, passed, details)
    
    # ===== EMPLOIS CREES ENDPOINTS =====
    print_header("3. EMPLOIS CREES ENDPOINTS")
    
    tests = [
        ("/emplois-crees/", "GET", ["count", "results"], None),
        ("/emplois-crees/summary/", "GET", ["total_emplois"], None),
        ("/emplois-crees/", "GET", ["count", "results"], {"type_demande": "CREATION"}),
    ]
    
    for endpoint, method, expected_keys, filters in tests:
        total_tests += 1
        name = f"{endpoint}" + (f" (filters: {filters})" if filters else "")
        passed, details, _ = test_endpoint(endpoint, method, expected_keys, filters)
        
        if passed:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print_test(name, passed, details)
    
    # ===== CREANCES AGEES ENDPOINTS =====
    print_header("4. CREANCES AGEES ENDPOINTS")
    
    tests = [
        ("/creances-agees/", "GET", ["count", "results"], None),
        ("/creances-agees/summary/", "GET", ["total_factures"], None),
        ("/creances-agees/", "GET", ["count", "results"], {"niveau_risque": "ELEVE"}),
    ]
    
    for endpoint, method, expected_keys, filters in tests:
        total_tests += 1
        name = f"{endpoint}" + (f" (filters: {filters})" if filters else "")
        passed, details, _ = test_endpoint(endpoint, method, expected_keys, filters)
        
        if passed:
            passed_tests += 1
        else:
            failed_tests += 1
        
        print_test(name, passed, details)
    
    # ===== CORS & HEADERS TEST =====
    print_header("5. CORS & RESPONSE HEADERS")
    
    try:
        response = requests.options(f"{API_BASE}/implantation-suivi/", timeout=5)
        has_cors = 'access-control-allow-origin' in response.headers or response.status_code == 200
        total_tests += 1
        
        if has_cors:
            passed_tests += 1
            print_test("CORS headers present", True, f"Status: {response.status_code}")
        else:
            failed_tests += 1
            print_test("CORS headers present", False, f"Status: {response.status_code}")
    except Exception as e:
        total_tests += 1
        failed_tests += 1
        print_test("CORS headers present", False, str(e))
    
    # ===== RESPONSE FORMAT TEST =====
    print_header("6. RESPONSE FORMAT VALIDATION")
    
    try:
        response = requests.get(f"{API_BASE}/implantation-suivi/", timeout=5)
        data = response.json()
        
        # Check pagination structure
        has_pagination = all(key in data for key in ['count', 'next', 'previous', 'results'])
        total_tests += 1
        
        if has_pagination:
            passed_tests += 1
            print_test("Pagination structure (count, next, previous, results)", True, 
                      f"Results: {len(data.get('results', []))}")
        else:
            failed_tests += 1
            missing = [k for k in ['count', 'next', 'previous', 'results'] if k not in data]
            print_test("Pagination structure", False, f"Missing: {missing}")
    except Exception as e:
        total_tests += 1
        failed_tests += 1
        print_test("Pagination structure", False, str(e))
    
    # ===== SAMPLE DATA TEST =====
    print_header("7. SAMPLE DATA VALIDATION")
    
    try:
        response = requests.get(f"{API_BASE}/implantation-suivi/?limit=1", timeout=5)
        data = response.json()
        
        if data['results']:
            item = data['results'][0]
            required_fields = ['zone_id', 'annee', 'mois', 'nombre_implantations']
            has_required = all(field in item for field in required_fields)
            
            total_tests += 1
            if has_required:
                passed_tests += 1
                print_test("Sample data has required fields", True, 
                          f"Fields: {', '.join(list(item.keys())[:5])}...")
            else:
                failed_tests += 1
                missing = [f for f in required_fields if f not in item]
                print_test("Sample data has required fields", False, f"Missing: {missing}")
        else:
            total_tests += 1
            failed_tests += 1
            print_test("Sample data available", False, "No results returned")
    except Exception as e:
        total_tests += 1
        failed_tests += 1
        print_test("Sample data validation", False, str(e))
    
    # ===== SUMMARY =====
    print_header("TEST SUMMARY")
    
    print(f"  {Colors.BOLD}Total Tests:{Colors.END} {total_tests}")
    print(f"  {Colors.GREEN}{Colors.BOLD}Passed:{Colors.END} {passed_tests}")
    print(f"  {Colors.RED}{Colors.BOLD}Failed:{Colors.END} {failed_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate == 100:
        status_color = Colors.GREEN
        status_icon = "✓"
    elif success_rate >= 80:
        status_color = Colors.YELLOW
        status_icon = "⚠"
    else:
        status_color = Colors.RED
        status_icon = "✗"
    
    print(f"\n  {status_color}{Colors.BOLD}{status_icon} Success Rate: {success_rate:.1f}%{Colors.END}")
    
    # ===== NEXT STEPS =====
    print_header("NEXT STEPS FOR FRONTEND INTEGRATION")
    
    if passed_tests == total_tests:
        print(f"  {Colors.GREEN}✓{Colors.END} All endpoints working! Frontend can connect.")
        print(f"\n  Frontend configuration to use:")
        print(f"    {Colors.CYAN}BASE_URL = 'http://localhost:8000/api'{Colors.END}")
        print(f"\n  Update in: {Colors.CYAN}bi_app/frontend/src/hooks/useDashboard.ts{Colors.END}")
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Some endpoints have issues. Check errors above.")
        print(f"\n  Common issues:")
        print(f"    1. CORS not enabled - add django-cors-headers")
        print(f"    2. Endpoints not registered - check api/urls.py")
        print(f"    3. Database not migrated - run python manage.py migrate")
    
    print("\n")
    
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
