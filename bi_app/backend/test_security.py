import requests

# Test 1: Sans token
print("Test 1: Sans token (devrait échouer)")
r1 = requests.get('http://127.0.0.1:8000/api/zones/map/')
print(f'Status: {r1.status_code}')
print(f'Message: {r1.json()}')
print()

# Test 2: Avec token
print("Test 2: Avec token (devrait réussir)")
login = requests.post('http://127.0.0.1:8000/api/auth/jwt/login/', 
                     json={'username':'admin', 'password':'admin123'})
token = login.json()['access']
print(f'Token obtenu: {token[:50]}...')

r2 = requests.get('http://127.0.0.1:8000/api/zones/map/', 
                 headers={'Authorization': f'Bearer {token}'})
print(f'Status: {r2.status_code}')
if r2.ok:
    zones = r2.json()['zones']
    print(f'✅ Zones: {len(zones)} zones chargées')
else:
    print(f'❌ Erreur: {r2.text}')
