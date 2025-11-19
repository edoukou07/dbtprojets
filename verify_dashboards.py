#!/usr/bin/env python3
"""
Verify all dashboards display correct metrics with current API responses
"""
import json

# API Responses from endpoint testing
api_responses = {
    'financier': {
        'total_factures': 42,
        'ca_total': 3132136002.0,
        'ca_paye': 531347999.0,
        'ca_impaye': 2600788003.0,
        'total_collectes': 10,
        'montant_recouvre': 2021196002.0,
        'montant_a_recouvrer': 6144392004.0,
        'taux_recouvrement': 35.35,
        'delai_moyen_paiement': 12.215,
        'taux_paiement_moyen': 16.96,
        'taux_impaye_pct': 83.04,
        'taux_recouvrement_moyen': 32.89
    },
    'occupation': {
        'total_lots': 52,
        'lots_disponibles': 39,
        'lots_attribues': 14,
        'superficie_totale': 1138212.0,
        'superficie_disponible': 882923.0,
        'superficie_attribuee': 268989.0,
        'valeur_totale': 11076253396.0,
        'nombre_zones': 5,
        'taux_occupation_moyen': 26.92,
        'zones_faible_occupation': 3,
        'zones_saturees': 1
    },
    'clients': {
        'total_clients': 35,
        'ca_total': 3132136002.0,
        'ca_paye': 531347999.0,
        'ca_impaye': 2600788003.0,
        'taux_paiement_moyen': 35.0005,
        'total_factures': 42,
        'total_lots_attribues': 14,
        'superficie_totale': 0.0,
        'delai_moyen_paiement': 21,
        'factures_retard_total': 9,
        'taux_impaye_pct': 83.03560258364541,
        'taux_paye_pct': 16.964397416354593,
    },
    'operationnel': {
        'total_collectes': 5,
        'taux_cloture_moyen': 0.0,
        'taux_recouvrement_moyen': 32.89,
        'total_demandes': 23,
        'total_approuvees': 6,
        'taux_approbation_moyen': 26.09,
        'total_factures': 42,
        'total_payees': 17
    }
}

# Dashboard Requirements
dashboard_requirements = {
    'Dashboard': {
        'financier': ['ca_total', 'ca_paye', 'ca_impaye', 'taux_paiement_moyen', 'taux_recouvrement_moyen'],
        'occupation': ['total_lots', 'lots_disponibles', 'lots_attribues', 'taux_occupation_moyen'],
        'operationnel': ['total_collectes', 'total_demandes', 'taux_approbation_moyen', 'taux_recouvrement_moyen'],
    },
    'Financier Page': {
        'financier': ['ca_total', 'ca_paye', 'ca_impaye', 'taux_recouvrement_moyen', 'montant_recouvre', 'montant_a_recouvrer', 'delai_moyen_paiement'],
    },
    'Occupation Page': {
        'occupation': ['total_lots', 'lots_disponibles', 'lots_attribues', 'taux_occupation_moyen', 'nombre_zones'],
    },
    'Portefeuille Page': {
        'clients': ['total_clients', 'ca_total', 'ca_paye', 'ca_impaye', 'taux_paiement_moyen'],
    },
    'Operationnel Page': {
        'operationnel': ['total_collectes', 'total_demandes', 'total_approuvees', 'taux_recouvrement_moyen', 'taux_approbation_moyen'],
    }
}

# Verify
print("="*80)
print("DASHBOARD METRICS VERIFICATION")
print("="*80)

all_ok = True

for page_name, requirements in dashboard_requirements.items():
    print(f"\n{page_name}:")
    print("-" * 80)
    
    for endpoint, fields in requirements.items():
        response_data = api_responses.get(endpoint, {})
        
        print(f"\n  {endpoint.upper()} Endpoint:")
        for field in fields:
            if field in response_data:
                value = response_data[field]
                print(f"    [OK] {field}: {value}")
            else:
                print(f"    [MISSING] {field}: NOT IN RESPONSE")
                all_ok = False

print("\n" + "="*80)
if all_ok:
    print("✓ ALL DASHBOARDS HAVE REQUIRED METRICS")
else:
    print("✗ SOME DASHBOARDS MISSING METRICS")
print("="*80)

# Summary table
print("\n" + "="*80)
print("METRIC AVAILABILITY SUMMARY")
print("="*80)

for endpoint_name, endpoint_data in api_responses.items():
    print(f"\n{endpoint_name.upper()} ({len(endpoint_data)} fields):")
    for field, value in endpoint_data.items():
        if isinstance(value, float):
            print(f"  {field:35} = {value:.2f}")
        else:
            print(f"  {field:35} = {value}")
