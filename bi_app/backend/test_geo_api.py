import requests
import json

print("="*70)
print("TEST DES ENDPOINTS GÉOGRAPHIQUES")
print("="*70)

BASE_URL = "http://127.0.0.1:8000/api"

# Test 1: Get all zones map data
print("\n1. TEST: GET /api/zones/map/")
print("-"*70)
try:
    response = requests.get(f"{BASE_URL}/zones/map/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['success']}")
        print(f"✅ Zones count: {data['count']}")
        
        if data['zones']:
            print("\nPremière zone:")
            zone = data['zones'][0]
            print(f"  ID: {zone['id']}")
            print(f"  Nom: {zone['nom']}")
            print(f"  Superficie: {zone['superficie']} ha")
            print(f"  Taux occupation: {zone.get('taux_occupation_pct', 'N/A')}%")
            print(f"  Latitude: {zone.get('latitude', 'N/A')}")
            print(f"  Longitude: {zone.get('longitude', 'N/A')}")
            print(f"  Has polygon: {'Yes' if zone.get('polygon') else 'No'}")
            
            if zone.get('polygon'):
                coords = zone['polygon']['coordinates']
                print(f"  Polygon points: {len(coords[0]) if coords else 0}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 2: Get specific zone details
print("\n2. TEST: GET /api/zones/1/map/")
print("-"*70)
try:
    response = requests.get(f"{BASE_URL}/zones/1/map/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['success']}")
        
        zone = data['zone']
        print(f"\nZone: {zone['nom']}")
        print(f"  Superficie: {zone['superficie']} ha")
        print(f"  Lots count: {zone.get('lots_count', 0)}")
        print(f"  Latitude: {zone.get('latitude', 'N/A')}")
        print(f"  Longitude: {zone.get('longitude', 'N/A')}")
        
        if zone.get('lots'):
            print(f"\n  Premiers lots:")
            for lot in zone['lots'][:3]:
                print(f"    - Lot {lot['numero']}: {lot['superficie']} m² - {lot['statut']}")
                if lot.get('occupant'):
                    print(f"      Occupant: {lot['occupant']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("FIN DES TESTS")
print("="*70)
