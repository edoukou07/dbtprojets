#!/usr/bin/env python
"""
Fixed Frontend/Backend API Integration Test - WITH PROPER JWT AUTHENTICATION
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
import requests
from pathlib import Path

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
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def create_test_user():
    """Create or get test user and return access token"""
    print(f"{BLUE}Creating test user...{RESET}")
    
    try:
        user = User.objects.get(username='testuser')
        print(f"{YELLOW}  → Test user already exists{RESET}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='testuser@sigeti.local',
            password='testpass123'
        )
        print(f"{GREEN}  ✓ Test user created{RESET}")
    
    # Generate JWT token
    token = AccessToken.for_user(user)
    print(f"{GREEN}  ✓ JWT token generated{RESET}")
    
    return str(token)

def test_endpoint(name, method, url, token, params=None, expected_status=200):
    """Test a single endpoint"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=params, timeout=10)
        
        if response.status_code == expected_status:
            print(f"{GREEN}✓ {name}{RESET}")
            print(f"  → HTTP {response.status_code}")
            
            # Try to parse JSON
            try:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    print(f"  → Pagination: count={data.get('count')}, results={len(data.get('results', []))}")
                elif isinstance(data, dict) and 'detail' in data:
                    print(f"  → Response: {data.get('detail')}")
            except:
                pass
            
            return True
        else:
            print(f"{RED}✗ {name}{RESET}")
            print(f"  → Expected HTTP {expected_status}, got {response.status_code}")
            try:
                print(f"  → Response: {response.json()}")
            except:
                print(f"  → Response: {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"{RED}✗ {name}{RESET}")
        print(f"  → Error: {str(e)}")
        return False

def main():
    print(f"\n{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}  FRONTEND/BACKEND API INTEGRATION TEST - FIXED VERSION{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}\n")
    
    # Create test user and get token
    token = create_test_user()
    print(f"  Token: {token[:20]}...{token[-10:]}\n")
    
    # Test endpoints
    passed = 0
    total = 0
    
    # 1. IMPLANTATION SUIVI
    print(f"\n{YELLOW}1. IMPLANTATION SUIVI ENDPOINTS{RESET}")
    print("─" * 60)
    
    total += 1
    if test_endpoint(
        "List all implantations",
        "GET",
        f"{API_BASE}/implantation-suivi/",
        token
    ):
        passed += 1
    
    total += 1
    if test_endpoint(
        "Implantation summary",
        "GET",
        f"{API_BASE}/implantation-suivi/summary/",
        token
    ):
        passed += 1
    
    # 2. INDEMNISATIONS
    print(f"\n{YELLOW}2. INDEMNISATIONS ENDPOINTS{RESET}")
    print("─" * 60)
    
    total += 1
    if test_endpoint(
        "List all indemnisations",
        "GET",
        f"{API_BASE}/indemnisations/",
        token
    ):
        passed += 1
    
    total += 1
    if test_endpoint(
        "Indemnisations summary",
        "GET",
        f"{API_BASE}/indemnisations/summary/",
        token
    ):
        passed += 1
    
    # 3. EMPLOIS CREES
    print(f"\n{YELLOW}3. EMPLOIS CREES ENDPOINTS{RESET}")
    print("─" * 60)
    
    total += 1
    if test_endpoint(
        "List all emplois créés",
        "GET",
        f"{API_BASE}/emplois-crees/",
        token
    ):
        passed += 1
    
    total += 1
    if test_endpoint(
        "Emplois créés summary",
        "GET",
        f"{API_BASE}/emplois-crees/summary/",
        token
    ):
        passed += 1
    
    # 4. CREANCES AGEES
    print(f"\n{YELLOW}4. CREANCES AGEES ENDPOINTS{RESET}")
    print("─" * 60)
    
    total += 1
    if test_endpoint(
        "List all créances âgées",
        "GET",
        f"{API_BASE}/creances-agees/",
        token
    ):
        passed += 1
    
    total += 1
    if test_endpoint(
        "Créances âgées summary",
        "GET",
        f"{API_BASE}/creances-agees/summary/",
        token
    ):
        passed += 1
    
    # 5. JWT TOKEN ENDPOINT
    print(f"\n{YELLOW}5. AUTHENTICATION ENDPOINTS{RESET}")
    print("─" * 60)
    
    total += 1
    if test_endpoint(
        "JWT Token endpoint (/api/auth/jwt/token/)",
        "POST",
        f"{API_BASE}/auth/jwt/token/",
        token,
        params={"username": "testuser", "password": "testpass123"},
        expected_status=200
    ):
        passed += 1
    
    # FINAL SUMMARY
    print(f"\n{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}  FINAL SUMMARY{RESET}")
    print(f"{BOLD}═══════════════════════════════════════════════════════════════{RESET}")
    
    print(f"\n  Total Tests: {total}")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    print(f"  {RED}Failed: {total - passed}{RESET}")
    
    if passed > 0:
        rate = (passed / total) * 100
        print(f"\n  Success Rate: {rate:.1f}%")
        
        if rate == 100:
            print(f"\n  {GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}")
            print(f"\n  {BLUE}Next Steps:{RESET}")
            print(f"  1. Update frontend API configuration:")
            print(f"     - API_BASE_URL = 'http://localhost:8000/api'")
            print(f"     - Store JWT token in localStorage")
            print(f"     - Add Authorization header to all requests")
            print(f"\n  2. Start React frontend dev server:")
            print(f"     cd bi_app/frontend")
            print(f"     npm run dev")
            print(f"\n  3. Test dashboard data loading")
            return 0
        else:
            print(f"\n  {YELLOW}⚠ Some tests failed. Check details above.{RESET}")
            return 1
    else:
        print(f"\n  {RED}{BOLD}✗ NO TESTS PASSED{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
