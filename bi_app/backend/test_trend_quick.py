"""
Test rapide de l'analyse de tendances avec CA mensuel
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from ai_chat.chat_service import ChatService
from ai_chat.query_engine import HybridQueryEngine

# Initialiser le service
query_engine = HybridQueryEngine()
chat_service = ChatService(query_engine)

print("=" * 80)
print("Test: CA par mois (2025)")
print("=" * 80)

response = chat_service.process_chat_message("CA par mois en 2025")

print(f"\n✓ Question: {response['question']}")
print(f"✓ Nombre de résultats: {len(response.get('data', []))}")

if response.get('data'):
    print(f"\n📊 Données ({len(response['data'])} mois):")
    for row in response['data'][:5]:  # Afficher 5 premiers
        print(f"   - Mois {row.get('mois')}: CA facture = {row.get('ca_facture', 0):,.0f} FCFA")
    if len(response['data']) > 5:
        print(f"   ... + {len(response['data']) - 5} autres mois")

if response.get('trend_analysis'):
    trend = response['trend_analysis']
    print(f"\n📈 ANALYSE DE TENDANCE:")
    print(f"   - Tendance: {trend.get('tendance', 'N/A')}")
    print(f"   - Variation totale: {trend.get('variation_totale_pct', 0):.2f}%")
    print(f"   - Variation moyenne: {trend.get('variation_moyenne_pct', 0):.2f}%")
    print(f"   - Prévision: {trend.get('prevision_prochaine_periode', 0):,.0f}")
    print(f"   - Volatilité: {trend.get('volatilite', 'N/A')}")
    
    if trend.get('insights'):
        print(f"\n💡 INSIGHTS:")
        for insight in trend['insights']:
            print(f"   - {insight}")
else:
    print("\n⚠️ Pas d'analyse de tendance")

print("\n" + "=" * 80)
