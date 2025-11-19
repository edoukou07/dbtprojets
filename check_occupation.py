import os, sys, django
sys.path.insert(0, 'bi_app/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from analytics.models import MartPortefeuilleClients
from django.db.models import Sum

qs = MartPortefeuilleClients.objects.filter(nombre_lots_attribues__gt=0)
print(f'Clients avec lots: {qs.count()}')

if qs.exists():
    sample = qs.first()
    print(f'Sample:')
    print(f'  nombre_lots_attribues: {sample.nombre_lots_attribues}')
    print(f'  superficie_totale_attribuee: {sample.superficie_totale_attribuee}')
    
agg = qs.aggregate(
    total_lots=Sum('nombre_lots_attribues'),
    superficie=Sum('superficie_totale_attribuee')
)
print(f'Aggregate:')
print(f'  total_lots: {agg["total_lots"]}')
print(f'  superficie: {agg["superficie"]}')
