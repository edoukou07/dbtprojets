import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

client = APIClient()

print('Appel sans authentification:')
res = client.get('/api/financier/summary/', HTTP_HOST='127.0.0.1')
print('Status:', res.status_code)

user, created = User.objects.get_or_create(username='testuser_summary', defaults={'email': 'testsum@example.com'})
if created:
    user.set_password('testpass123')
    user.save()
    print('Utilisateur créé')

token = AccessToken.for_user(user)
client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token)}')

print('Appel avec authentification...')
res = client.get('/api/financier/summary/', HTTP_HOST='127.0.0.1')
print('Status:', res.status_code)
if res.status_code == 200:
    print('Keys:', list(res.data.keys()))
    print('delai_moyen_paiement:', res.data.get('delai_moyen_paiement'))
else:
    # Some responses return HttpResponse (e.g., not JSON) instead of DRF Response
    try:
        print('Erreur:', res.data)
    except Exception:
        print('Erreur: status', res.status_code)
