"""
Script de test pour l'endpoint analyse_comportement
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import sys
sys.path.insert(0, r'C:\Users\hynco\Desktop\DWH_SIG\bi_app\backend')
django.setup()

from api.views import MartPortefeuilleClientsViewSet
from rest_framework.test import APIRequestFactory
from django.test import RequestFactory

# Créer une requête factice
factory = APIRequestFactory()
request = factory.get('/api/clients/analyse_comportement/')

# Instantier le viewset
viewset = MartPortefeuilleClientsViewSet()
viewset.request = request

# Tester la méthode
try:
    response = viewset.analyse_comportement(request)
    print("✅ SUCCESS - Status:", response.status_code if hasattr(response, 'status_code') else 'N/A')
    print("\n📊 Response Data:")
    print(response.data)
    
    # Afficher les catégories de paiement
    if 'par_taux_paiement' in response.data:
        print("\n💰 Distribution par taux de paiement:")
        for cat in response.data['par_taux_paiement']:
            print(f"  - {cat['categorie']}: {cat['count']} clients, "
                  f"CA: {cat['ca_total']:,.0f} FCFA, "
                  f"Délai moyen: {cat['delai_moyen']} jours")
    
    # Afficher les délais de paiement
    if 'par_delai_paiement' in response.data:
        print("\n⏰ Distribution par délai de paiement:")
        for delai in response.data['par_delai_paiement']:
            print(f"  - {delai['plage_delai']}: {delai['count']} clients, "
                  f"CA: {delai['ca_total']:,.0f} FCFA, "
                  f"Taux: {delai['taux_paiement_moyen']:.1f}%")
    
except Exception as e:
    print("❌ ERROR:", type(e).__name__)
    print("Message:", str(e))
    import traceback
    traceback.print_exc()
