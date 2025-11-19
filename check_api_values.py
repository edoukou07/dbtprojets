import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.test.client import Client

client = Client()

# Appeler l'endpoint API
response = client.get('/api/mart-performance-financiere/summary/')

if response.status_code == 200:
    data = response.json()
    print("="*80)
    print("VALEURS ACTUELLES RETOURNÉES PAR L'API")
    print("="*80)
    print(f"\n{'ca_total':<30}: {data.get('ca_total', 0):>20,.0f} FCFA = {data.get('ca_total', 0)/1e9:.2f} Md")
    print(f"{'ca_paye':<30}: {data.get('ca_paye', 0):>20,.0f} FCFA = {data.get('ca_paye', 0)/1e9:.2f} Md")
    print(f"{'ca_impaye':<30}: {data.get('ca_impaye', 0):>20,.0f} FCFA = {data.get('ca_impaye', 0)/1e9:.2f} Md")
    print(f"{'montant_recouvre':<30}: {data.get('montant_recouvre', 0):>20,.0f} FCFA = {data.get('montant_recouvre', 0)/1e9:.2f} Md")
    print(f"{'montant_a_recouvrer':<30}: {data.get('montant_a_recouvrer', 0):>20,.0f} FCFA = {data.get('montant_a_recouvrer', 0)/1e9:.2f} Md")
    print(f"{'total_collectes':<30}: {data.get('total_collectes', 0):>20,.0f}")
    print(f"{'total_factures':<30}: {data.get('total_factures', 0):>20,.0f}")
    print(f"{'taux_recouvrement_moyen':<30}: {data.get('taux_recouvrement_moyen', 0):>20.2f}%")
    
    print("\n" + "="*80)
    print("VÉRIFICATION DE LA COMPOSITION")
    print("="*80)
    
    ca_impaye = data.get('ca_impaye', 0)
    montant_a_recouvrer_api = data.get('montant_a_recouvrer', 0)
    
    print(f"\nFactures impayées (ca_impaye):     {ca_impaye:>20,.0f} FCFA")
    print(f"Collectes à recouvrer (montant_a_recouvrer): {montant_a_recouvrer_api:>20,.0f} FCFA")
    print(f"{'─'*80}")
    print(f"TOTAL À RECOUVRER (somme):         {ca_impaye + montant_a_recouvrer_api:>20,.0f} FCFA")
    print(f"MAIS l'API retourne 'montant_a_recouvrer': {montant_a_recouvrer_api:>20,.0f} FCFA")
    
    # Le problème
    print(f"\n" + "="*80)
    if montant_a_recouvrer_api > ca_impaye + 1000000000:
        print("❌ PROBLÈME DÉTECTÉ!")
        print(f"   montant_a_recouvrer ({montant_a_recouvrer_api:,.0f})")
        print(f"   ne correspond pas à")
        print(f"   ca_impaye ({ca_impaye:,.0f}) + collectes")
        print(f"\n   Cela signifie que 'montant_a_recouvrer' contient SEULEMENT les collectes!")
        print(f"   Les factures impayées ne sont PAS incluses dans ce champ!")
    else:
        print("✅ Les valeurs semblent cohérentes")
else:
    print(f"❌ Erreur API: {response.status_code}")
    print(response.content)
