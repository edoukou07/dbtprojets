import os, sys, django
sys.path.insert(0, 'bi_app/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.test import RequestFactory
from api.views import MartPortefeuilleClientsViewSet
import json

factory = RequestFactory()
request = factory.get('/api/portefeuille/analyse_occupation/')
view = MartPortefeuilleClientsViewSet.as_view({'get': 'analyse_occupation'})
response = view(request)

print("API Response:")
print(json.dumps(response.data, indent=2, default=str))
