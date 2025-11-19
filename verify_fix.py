import requests

r = requests.get(
    'http://localhost:8000/api/financier/summary/',
    headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYzNDgxOTM2LCJpYXQiOjE3NjM0NzgzMzYsImp0aSI6IjBmNGRjZGQ2Y2EzMzRlMjZhODlkYTFlZGNlMzg0MWY4IiwidXNlcl9pZCI6MSwiaXNzIjoiU0lHRVRJLUJJIn0.I1EvnhgEurk8uaO4s6-Ukm6ZnONSnW5nbo8OkAP72YU'}
)

d = r.json()

print('=== RÉSULTATS CORRIGÉS ===')
print(f'CA: {d.get("ca_total"):,.0f} FCFA')
print(f'Recouvré: {d.get("montant_recouvre"):,.0f} FCFA')
print(f'À Recouvrer: {d.get("montant_a_recouvrer"):,.0f} FCFA')
print(f'Taux Recouvrement: {d.get("taux_recouvrement_moyen")}%')

ca_real = d.get('ca_total')
recouvre = d.get('montant_recouvre')
print(f'\nCréances Impayées (CA - Recouvré): {ca_real - recouvre:,.0f} FCFA')
print(f'Formule: {ca_real:,.0f} - {recouvre:,.0f} = {ca_real - recouvre:,.0f}')

# Vérification de la logique
a_recouvrer = d.get('montant_a_recouvrer')
print(f'\n=== VÉRIFICATION DE LA LOGIQUE ===')
print(f'Montant À Recouvrer (API): {a_recouvrer:,.0f} FCFA')
print(f'Créances Impayées (Calculées): {ca_real - recouvre:,.0f} FCFA')
if abs((ca_real - recouvre) - a_recouvrer) < 1000:
    print('✅ Les valeurs correspondent! Le bug est fixé!')
else:
    print('❌ Les valeurs ne correspondent toujours pas')
