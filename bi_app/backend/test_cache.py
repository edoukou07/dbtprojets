"""
Test script to verify cache is working
"""
import os
import django
import time
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.core.cache import cache
from django.conf import settings

print("="*60)
print("CACHE CONFIGURATION TEST")
print("="*60)

# Test 1: Check cache backend
print(f"\n✓ Cache Backend: {settings.CACHES['default']['BACKEND']}")
print(f"✓ Cache Location: {settings.CACHES['default'].get('LOCATION', 'N/A')}")

# Test 2: Basic cache operations
print("\n" + "="*60)
print("TESTING BASIC CACHE OPERATIONS")
print("="*60)

# Set a value
cache.set('test_key', 'test_value', 60)
print("✓ Set test_key = 'test_value'")

# Get the value
value = cache.get('test_key')
print(f"✓ Get test_key = '{value}'")

if value == 'test_value':
    print("✅ Basic cache operations working!")
else:
    print("❌ Cache get/set failed!")

# Test 3: Test API endpoint caching
print("\n" + "="*60)
print("TESTING API ENDPOINT CACHING")
print("="*60)

base_url = "http://127.0.0.1:8000/api"

# Note: Add authentication if endpoints require it
# For now, testing without auth (endpoints should allow anonymous access for testing)
headers = {
    'Accept': 'application/json',
}

endpoints = [
    '/occupation/summary/',
    '/clients/summary/',
    '/financier/summary/',
    '/operationnel/summary/',
]

for endpoint in endpoints:
    url = base_url + endpoint
    
    try:
        # First request (should be MISS)
        start_time = time.time()
        response1 = requests.get(url, headers=headers)
        time1 = (time.time() - start_time) * 1000
        
        cache_status1 = response1.headers.get('X-Cache', 'NO-HEADER')
        
        # Second request (should be HIT)
        start_time = time.time()
        response2 = requests.get(url, headers=headers)
        time2 = (time.time() - start_time) * 1000
        
        cache_status2 = response2.headers.get('X-Cache', 'NO-HEADER')
        
        print(f"\n{endpoint}")
        print(f"  Status: {response1.status_code}")
        print(f"  1st request: {time1:.2f}ms - Cache: {cache_status1}")
        print(f"  2nd request: {time2:.2f}ms - Cache: {cache_status2}")
        
        if cache_status2 == 'HIT':
            speedup = time1 / time2 if time2 > 0 else 0
            print(f"  ✅ Cache working! Speedup: {speedup:.1f}x")
        elif time2 < time1:
            print(f"  ✅ Response faster on 2nd request (likely cached)")
        else:
            print(f"  ⚠️  Check if authentication is required or cache decorator is applied")
    except requests.exceptions.ConnectionError:
        print(f"\n{endpoint}")
        print(f"  ❌ Connection error - Is Django server running?")
    except Exception as e:
        print(f"\n{endpoint}")
        print(f"  ❌ Error: {e}")

print("\n" + "="*60)
print("CACHE TTL SETTINGS")
print("="*60)
for key, value in settings.CACHE_TTL.items():
    print(f"  {key}: {value}s ({value/60:.1f} min)")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
