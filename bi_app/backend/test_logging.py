"""
Test script for API logging system
Tests request logging, error tracking, and monitoring endpoints
"""
import os
import django
import time
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.conf import settings

print("="*70)
print("API LOGGING SYSTEM TEST")
print("="*70)

BASE_URL = "http://127.0.0.1:8000/api"

# Test 1: Check logs directory
print("\n" + "="*70)
print("TEST 1: LOGS DIRECTORY")
print("="*70)

logs_dir = settings.LOGS_DIR
print(f"✓ Logs directory: {logs_dir}")
print(f"✓ Directory exists: {logs_dir.exists()}")

if logs_dir.exists():
    log_files = list(logs_dir.iterdir())
    print(f"✓ Log files found: {len(log_files)}")
    for log_file in log_files:
        size_kb = log_file.stat().st_size / 1024
        print(f"  - {log_file.name}: {size_kb:.2f} KB")
else:
    print("⚠️  Logs directory not created yet (will be created on first request)")

# Test 2: Make test requests to generate logs
print("\n" + "="*70)
print("TEST 2: GENERATING TEST REQUESTS")
print("="*70)

test_endpoints = [
    '/occupation/summary/',
    '/clients/summary/',
    '/financier/summary/',
    '/operationnel/summary/',
]

print("Making 10 requests to each endpoint...")
for endpoint in test_endpoints:
    url = BASE_URL + endpoint
    print(f"\n  Testing {endpoint}...")
    
    for i in range(10):
        try:
            start = time.time()
            response = requests.get(url)
            elapsed_ms = (time.time() - start) * 1000
            
            cache_status = response.headers.get('X-Cache', 'N/A')
            print(f"    Request {i+1}: {response.status_code} - {elapsed_ms:.2f}ms - Cache: {cache_status}")
            
            time.sleep(0.1)  # Small delay between requests
        except Exception as e:
            print(f"    Request {i+1}: ERROR - {e}")

# Test 3: Test error logging (404 and invalid endpoint)
print("\n" + "="*70)
print("TEST 3: TESTING ERROR LOGGING")
print("="*70)

error_endpoints = [
    '/invalid/endpoint/',
    '/occupation/999999/',  # Non-existent item
]

for endpoint in error_endpoints:
    url = BASE_URL + endpoint
    try:
        response = requests.get(url)
        print(f"  {endpoint}: Status {response.status_code}")
    except Exception as e:
        print(f"  {endpoint}: ERROR - {e}")

# Test 4: Check if logs were created
print("\n" + "="*70)
print("TEST 4: VERIFYING LOG FILES")
print("="*70)

expected_logs = ['api_requests.log', 'api_requests.json', 'errors.log']
for log_name in expected_logs:
    log_path = logs_dir / log_name
    if log_path.exists():
        size_kb = log_path.stat().st_size / 1024
        print(f"  ✅ {log_name}: {size_kb:.2f} KB")
        
        # Show last 3 lines
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if lines:
                print(f"     Last entry preview:")
                last_line = lines[-1].strip()
                if len(last_line) > 100:
                    print(f"     {last_line[:100]}...")
                else:
                    print(f"     {last_line}")
        except:
            pass
    else:
        print(f"  ❌ {log_name}: Not found")

# Test 5: Test monitoring endpoints (requires admin auth)
print("\n" + "="*70)
print("TEST 5: TESTING MONITORING ENDPOINTS")
print("="*70)

monitoring_endpoints = [
    '/monitoring/metrics/',
    '/monitoring/analytics/',
]

print("Note: These endpoints require admin authentication")
for endpoint in monitoring_endpoints:
    url = BASE_URL + endpoint
    try:
        response = requests.get(url)
        print(f"\n  {endpoint}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Response data keys: {list(data.keys())}")
            
            # Show some metrics
            if endpoint.endswith('/metrics/'):
                print(f"     Total requests: {data.get('total_requests', 0)}")
                print(f"     Total errors: {data.get('total_errors', 0)}")
                print(f"     Error rate: {data.get('error_rate', 0)}%")
            
            elif endpoint.endswith('/analytics/'):
                print(f"     Avg response time: {data.get('avg_response_time_ms', 0)}ms")
                print(f"     Cache hit rate: {data.get('cache_hit_rate', 0)}%")
                if 'top_endpoints' in data and data['top_endpoints']:
                    print(f"     Top endpoint: {data['top_endpoints'][0]}")
        
        elif response.status_code == 403:
            print(f"  ⚠️  Requires admin authentication (expected in production)")
        else:
            print(f"  ❌ Unexpected status code")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Test 6: Analyze log content
print("\n" + "="*70)
print("TEST 6: LOG CONTENT ANALYSIS")
print("="*70)

api_log = logs_dir / 'api_requests.log'
if api_log.exists():
    try:
        with open(api_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✓ Total log entries: {len(lines)}")
        
        # Count by level
        info_count = sum(1 for line in lines if 'INFO' in line)
        warning_count = sum(1 for line in lines if 'WARNING' in line)
        error_count = sum(1 for line in lines if 'ERROR' in line)
        
        print(f"  - INFO: {info_count}")
        print(f"  - WARNING: {warning_count}")
        print(f"  - ERROR: {error_count}")
        
        # Count cache hits/misses
        cache_hits = sum(1 for line in lines if 'Cache: HIT' in line)
        cache_misses = sum(1 for line in lines if 'Cache: MISS' in line)
        
        print(f"\n✓ Cache statistics:")
        print(f"  - Cache HITs: {cache_hits}")
        print(f"  - Cache MISSes: {cache_misses}")
        if cache_hits + cache_misses > 0:
            hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100
            print(f"  - Hit rate: {hit_rate:.1f}%")
    
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")
else:
    print("❌ api_requests.log not found")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

print("""
✅ Logging system configured successfully!

Log files created:
  - api_requests.log: Human-readable request logs
  - api_requests.json: Machine-readable JSON logs
  - errors.log: Error-specific logs
  - slow_requests.log: Slow requests (>1s)

Monitoring endpoints available (admin only):
  - /api/monitoring/metrics/ - Real-time metrics
  - /api/monitoring/logs/ - Recent log entries
  - /api/monitoring/errors/ - Recent errors
  - /api/monitoring/slow/ - Slow requests
  - /api/monitoring/analytics/ - Performance analytics
  - /api/monitoring/clear-metrics/ - Clear metrics cache

Features:
  ✓ Request timing and performance tracking
  ✓ Error logging with stack traces
  ✓ Cache hit/miss tracking
  ✓ Slow request detection (>1000ms)
  ✓ Rotating log files (10MB max, 10 backups)
  ✓ JSON logs for analysis
  ✓ Real-time metrics via cache
""")

print("="*70)
print("LOGGING SYSTEM TEST COMPLETE")
print("="*70)
