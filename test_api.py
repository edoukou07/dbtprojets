import requests
import json

try:
    # Tester l'API
    resp = requests.get('http://localhost:8000/api/operationnel/summary/', timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"\nTaux Recouvrement Moyen: {data.get('taux_recouvrement_moyen')}")
    print(f"Total Collectes: {data.get('total_collectes')}")
    print(f"Total Demandes: {data.get('total_demandes')}")
    print(f"\nFull response:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
