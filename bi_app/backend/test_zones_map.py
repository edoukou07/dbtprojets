"""
Test de l'API des zones géographiques
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

print("="*70)
print("TEST DE L'API ZONES GÉOGRAPHIQUES")
print("="*70)

# Test 1: Récupérer toutes les zones avec coordonnées
print("\n1. GET /zones/map/")
response = requests.get(f"{BASE_URL}/zones/map/")
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Success: {data.get('success')}")
    print(f"   Nombre de zones: {len(data.get('zones', []))}")
    
    if data.get('zones'):
        zone = data['zones'][0]
        print(f"\n   Exemple de zone:")
        print(f"   - ID: {zone.get('id')}")
        print(f"   - Nom: {zone.get('nom')}")
        print(f"   - Latitude: {zone.get('latitude')}")
        print(f"   - Longitude: {zone.get('longitude')}")
        print(f"   - Taux occupation: {zone.get('taux_occupation_pct')}%")
        print(f"   - Lots totaux: {zone.get('lots_totaux')}")
        print(f"   - Lots occupés: {zone.get('lots_occupes')}")
        
        if zone.get('polygon'):
            poly = zone['polygon']
            print(f"   - Polygon type: {poly.get('type')}")
            if poly.get('coordinates'):
                coords_count = len(poly['coordinates'][0]) if poly['coordinates'] else 0
                print(f"   - Nombre de points du polygon: {coords_count}")
                if coords_count > 0:
                    print(f"   - Premier point: {poly['coordinates'][0][0]}")

# Test 2: Récupérer les détails d'une zone spécifique
print("\n2. GET /zones/1/details/")
response = requests.get(f"{BASE_URL}/zones/1/details/")
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Success: {data.get('success')}")
    
    if data.get('zone'):
        zone = data['zone']
        print(f"\n   Détails de la zone:")
        print(f"   - Nom: {zone.get('nom')}")
        print(f"   - Superficie: {zone.get('superficie_ha')} ha")
        print(f"   - Prix: {zone.get('prix')} FCFA/m²")
        print(f"   - Viabilité: {zone.get('viabilite')}")
        print(f"   - Statut: {zone.get('statut')}")
        
        if 'stats' in data:
            stats = data['stats']
            print(f"\n   Statistiques:")
            print(f"   - Lots totaux: {stats.get('lots_totaux')}")
            print(f"   - Lots occupés: {stats.get('lots_occupes')}")
            print(f"   - Lots disponibles: {stats.get('lots_disponibles')}")
            print(f"   - Taux occupation: {stats.get('taux_occupation_pct')}%")
            print(f"   - Superficie occupée: {stats.get('superficie_occupee_ha')} ha")

# Test 3: Vérifier les zones avec polygons
print("\n3. Analyse des polygons")
response = requests.get(f"{BASE_URL}/zones/map/")
if response.status_code == 200:
    data = response.json()
    zones = data.get('zones', [])
    
    zones_with_polygon = [z for z in zones if z.get('polygon') and z['polygon'].get('coordinates')]
    zones_without_polygon = [z for z in zones if not (z.get('polygon') and z['polygon'].get('coordinates'))]
    
    print(f"   Zones avec polygon: {len(zones_with_polygon)}")
    print(f"   Zones sans polygon: {len(zones_without_polygon)}")
    
    if zones_without_polygon:
        print(f"\n   Zones sans polygon:")
        for z in zones_without_polygon[:5]:
            print(f"   - {z.get('nom')} (ID: {z.get('id')})")

# Test 4: Vérifier les coordonnées (lat/lon)
print("\n4. Analyse des coordonnées")
response = requests.get(f"{BASE_URL}/zones/map/")
if response.status_code == 200:
    data = response.json()
    zones = data.get('zones', [])
    
    zones_with_coords = [z for z in zones if z.get('latitude') and z.get('longitude')]
    zones_without_coords = [z for z in zones if not (z.get('latitude') and z.get('longitude'))]
    
    print(f"   Zones avec coordonnées: {len(zones_with_coords)}")
    print(f"   Zones sans coordonnées: {len(zones_without_coords)}")
    
    if zones_with_coords:
        print(f"\n   Exemples de coordonnées:")
        for z in zones_with_coords[:3]:
            print(f"   - {z.get('nom')}: ({z.get('latitude')}, {z.get('longitude')})")

print("\n" + "="*70)
print("FIN DES TESTS")
print("="*70)
