#!/usr/bin/env python3
import requests
import json

# Test the operationnel/summary endpoint
url = 'http://localhost:8000/api/operationnel/summary/'

print("=== TEST API /api/operationnel/summary/ ===\n")
print(f"URL: {url}\n")

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    print("✅ Réponse Reçue:\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Vérifications spécifiques
    print("\n\n=== VÉRIFICATIONS ===")
    print(f"Total Demandes: {data.get('total_demandes')} (Attendu: 23)")
    print(f"Demandes Approuvées: {data.get('total_approuvees')} (Attendu: 6)")
    print(f"Taux Recouvrement Moyen: {data.get('taux_recouvrement_moyen')}% (Avant corr: 19.1%, Après: ~32.89%)")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur: {e}")
except json.JSONDecodeError as e:
    print(f"❌ Erreur JSON: {e}")
    print(f"Réponse: {response.text[:500]}")
