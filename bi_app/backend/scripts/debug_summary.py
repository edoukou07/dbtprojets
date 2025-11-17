from analytics.models import MartPerformanceFinanciere
from django.db.models import Sum, Avg
qs = MartPerformanceFinanciere.objects.all()
summary = qs.aggregate(
    total_factures=Sum('nombre_factures'),
    ca_total=Sum('montant_total_facture')
)
print('SUMMARY', summary)
avg_delai = None
try:
    avg_delai = qs.aggregate(avg_delai=Avg('delai_moyen_paiement'))['avg_delai']
except TypeError:
    avg_delai = None

# Normalize
if isinstance(avg_delai, (int, float)) and avg_delai is not None:
    summary['delai_moyen_paiement'] = float(avg_delai)
elif hasattr(avg_delai, 'total_seconds'):
    summary['delai_moyen_paiement'] = avg_delai.total_seconds() / 86400
elif avg_delai is None:
    values = list(qs.values_list('delai_moyen_paiement', flat=True))
    values = [v for v in values if v is not None]
    if values:
        total_days = 0.0
        count = 0
        for v in values:
            if hasattr(v, 'total_seconds'):
                total_days += v.total_seconds() / 86400
            else:
                try:
                    total_days += float(v)
                except Exception:
                    continue
            count += 1
        summary['delai_moyen_paiement'] = (total_days / count) if count else 0
    else:
        summary['delai_moyen_paiement'] = 0
else:
    try:
        summary['delai_moyen_paiement'] = float(avg_delai)
    except Exception:
        summary['delai_moyen_paiement'] = 0

print('DELAI IN DAYS:', summary['delai_moyen_paiement'])
