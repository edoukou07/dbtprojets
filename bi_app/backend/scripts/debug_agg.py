from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum, Avg
qs = MartPerformanceFinanciere.objects.all()
print('COUNT', qs.count())
summary = qs.aggregate(total_factures=Sum('nombre_factures'))
print('SUMMARY', summary)
try:
    avg = qs.aggregate(avg_delai=Avg('delai_moyen_paiement'))['avg_delai']
    print('AVG DELAI', type(avg), avg)
except Exception as e:
    print('AGG_EXCEPTION', type(e), e)
    vals = list(qs.values_list('delai_moyen_paiement', flat=True))
    print('VALS_LEN', len(vals))
    if vals:
        print('FIRST', type(vals[0]), vals[0])
    else:
        print('NO VALS')
