#!/usr/bin/env python3
"""
Test login directly to verify credentials
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Test with username (as the backend expects)
credentials = {
    'username': 'admin',
    'password': 'Admin@123'
}

print("Testing /api/auth/login/ endpoint...")
print(f"Credentials: {credentials}")
print()

response = requests.post(
    f"{BASE_URL}/auth/login/",
    json=credentials
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("\n✓ Login successful!")
    token = response.json().get('access')
    print(f"Token (first 50 chars): {token[:50]}...")
else:
    print("\n✗ Login failed!")
    print("\nTrying with email instead of username...")
    
    credentials_email = {
        'username': 'admin@sigeti.ci',
        'password': 'Admin@123'
    }
    
    response2 = requests.post(
        f"{BASE_URL}/auth/login/",
        json=credentials_email
    )
    
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")
