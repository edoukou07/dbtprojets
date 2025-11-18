#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_jwt_token():
    """Obtenir un token JWT"""
    url = f"http://localhost:8000/api/auth/jwt/token/"
    payload = {"username": "admin", "password": "admin"}
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get('access') or data.get('token')
    return None

def make_api_request(endpoint, token=None):
    """Faire une requête API"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def main():
    print("\n" + "="*70)
    print("VERIFICATION DES ENDPOINTS API DASHBOARD")
    print("="*70 + "\n")
    
    token = get_jwt_token()
    if not token:
        print("[ERREUR] Impossible d'obtenir un token JWT")
        return
    
    print("[OK] Token JWT obtenu\n")
    
    # Test Financier
    print("FINANCIER SUMMARY:")
    data = make_api_request("financier/summary/", token)
    if data:
        ca_total = data.get('ca_total', 0)
        ca_paye = data.get('ca_paye', 0)
        taux = data.get('taux_paiement_moyen', 0)
        print(f"  CA Total: {ca_total:,} FCFA (attendu 3,132,136,002)")
        print(f"  CA Paye: {ca_paye:,} FCFA (attendu 531,347,999)")
        print(f"  Taux Paiement: {taux}% (attendu 13.70%)")
        if ca_total == 3_132_136_002:
            print("  [OK] CA Total CORRECT")
        else:
            print("  [ERREUR] CA Total INCORRECT")
    
    # Test Occupation
    print("\nOCCUPATION SUMMARY:")
    data = make_api_request("occupation/summary/", token)
    if data:
        zones = data.get('nombre_zones', 0)
        print(f"  Nombre de Zones: {zones} (attendu 5)")
        if zones == 5:
            print("  [OK] Nombre de Zones CORRECT")
        else:
            print("  [ERREUR] Nombre de Zones INCORRECT")
    
    # Test Operationnel
    print("\nOPERATIONNEL SUMMARY:")
    data = make_api_request("operationnel/summary/", token)
    if data:
        collectes = data.get('total_collectes', 0)
        demandes = data.get('total_demandes', 0)
        approuvees = data.get('total_approuvees', 0)
        taux_recouvrement = data.get('taux_recouvrement_moyen', 0)
        factures = data.get('total_factures', 0)
        
        print(f"  Total Collectes: {collectes} (attendu 5)")
        print(f"  Total Demandes: {demandes} (attendu 23)")
        print(f"  Total Approuvees: {approuvees} (attendu 6)")
        print(f"  Taux Recouvrement: {taux_recouvrement}% (attendu 32.89%)")
        print(f"  Total Factures: {factures} (attendu 42)")
        
        if demandes == 23:
            print("  [OK] Total Demandes CORRECT")
        else:
            print("  [ERREUR] Total Demandes INCORRECT")
        
        if taux_recouvrement and abs(float(taux_recouvrement) - 32.89) < 0.5:
            print("  [OK] Taux Recouvrement CORRECT (32.89%)")
        else:
            print(f"  [ERREUR] Taux Recouvrement INCORRECT ({taux_recouvrement}%)")
    
    # Test Clients
    print("\nCLIENTS SUMMARY:")
    data = make_api_request("clients/summary/", token)
    if data:
        clients = data.get('total_clients', 0)
        ca = data.get('ca_total', 0)
        taux = data.get('taux_paiement_moyen', 0)
        
        print(f"  Total Clients: {clients} (attendu 35)")
        print(f"  CA Total: {ca:,} FCFA (attendu 3,132,136,002)")
        print(f"  Taux Paiement: {taux}% (attendu 35%)")
        
        if clients == 35:
            print("  [OK] Total Clients CORRECT")
        else:
            print("  [ERREUR] Total Clients INCORRECT")
    
    print("\n" + "="*70)
    print("VERIFICATION TERMINEE")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
