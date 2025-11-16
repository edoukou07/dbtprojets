"""
Test de l'analyse de tendances du chatbot
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from ai_chat.chat_service import ChatService
from ai_chat.query_engine import HybridQueryEngine


def test_trend_analysis():
    """Test de l'analyse de tendances"""
    
    print("=" * 80)
    print("TEST ANALYSE DE TENDANCES - Chatbot SIGETI")
    print("=" * 80)
    
    # Initialiser le service
    query_engine = HybridQueryEngine()
    chat_service = ChatService(query_engine)
    
    # Test 1: Évolution mensuelle du CA (tendance simple)
    print("\n" + "=" * 80)
    print("Test 1: Évolution mensuelle du CA 2024")
    print("=" * 80)
    
    response1 = chat_service.process_chat_message("évolution du CA par mois en 2024")
    
    print(f"\n✓ Question: {response1['question']}")
    print(f"✓ Réponse: {response1['answer']}")
    print(f"✓ Nombre de résultats: {len(response1.get('data', []))}")
    print(f"✓ Méthode: {response1.get('method')}")
    
    if response1.get('trend_analysis'):
        trend = response1['trend_analysis']
        print(f"\n📈 ANALYSE DE TENDANCE:")
        print(f"   - Tendance: {trend.get('tendance', 'N/A')}")
        print(f"   - Variation totale: {trend.get('variation_totale_pct', 0):.2f}%")
        print(f"   - Variation moyenne: {trend.get('variation_moyenne_pct', 0):.2f}%")
        print(f"   - Prévision prochaine période: {trend.get('prevision_prochaine_periode', 0):.2f}")
        print(f"   - Volatilité: {trend.get('volatilite', 'N/A')}")
        print(f"   - Nombre de périodes: {trend.get('nb_periodes', 0)}")
        
        if trend.get('saisonnalite', {}).get('detectee'):
            saison = trend['saisonnalite']
            print(f"\n📅 SAISONNALITÉ DÉTECTÉE:")
            print(f"   - Mois fort: {saison.get('mois_fort')}")
            print(f"   - Mois faible: {saison.get('mois_faible')}")
            print(f"   - Coefficient de variation: {saison.get('coefficient_variation', 0):.2f}%")
        
        if trend.get('insights'):
            print(f"\n💡 INSIGHTS ({len(trend['insights'])}):")
            for i, insight in enumerate(trend['insights'], 1):
                print(f"   {i}. {insight}")
    else:
        print("\n⚠️ Aucune analyse de tendance disponible")
    
    # Test 2: Évolution par zone (tendances groupées)
    print("\n" + "=" * 80)
    print("Test 2: Évolution du CA par zone en 2024")
    print("=" * 80)
    
    response2 = chat_service.process_chat_message("évolution du CA par zone en 2024")
    
    print(f"\n✓ Question: {response2['question']}")
    print(f"✓ Réponse: {response2['answer']}")
    print(f"✓ Nombre de résultats: {len(response2.get('data', []))}")
    print(f"✓ Méthode: {response2.get('method')}")
    
    if response2.get('trend_analysis'):
        trend = response2['trend_analysis']
        print(f"\n📈 ANALYSE DE TENDANCES GROUPÉES:")
        print(f"   - Nombre d'entités: {trend.get('nb_entites', 0)}")
        print(f"   - Variation moyenne globale: {trend.get('variation_moyenne_globale', 0):.2f}%")
        
        if trend.get('top_5_hausse'):
            print(f"\n🏆 TOP 5 EN HAUSSE:")
            for i, item in enumerate(trend['top_5_hausse'], 1):
                print(f"   {i}. {item['entite']}: {item['variation_pct']:+.2f}% ({item['tendance']})")
        
        if trend.get('top_5_baisse'):
            print(f"\n📉 TOP 5 EN BAISSE:")
            for i, item in enumerate(trend['top_5_baisse'], 1):
                print(f"   {i}. {item['entite']}: {item['variation_pct']:+.2f}% ({item['tendance']})")
        
        if trend.get('insights'):
            print(f"\n💡 INSIGHTS ({len(trend['insights'])}):")
            for i, insight in enumerate(trend['insights'], 1):
                print(f"   {i}. {insight}")
    else:
        print("\n⚠️ Aucune analyse de tendance disponible")
    
    # Test 3: Comparaison annuelle
    print("\n" + "=" * 80)
    print("Test 3: Comparaison annuelle du CA")
    print("=" * 80)
    
    response3 = chat_service.process_chat_message("comparer le CA entre les années")
    
    print(f"\n✓ Question: {response3['question']}")
    print(f"✓ Réponse: {response3['answer']}")
    print(f"✓ Nombre de résultats: {len(response3.get('data', []))}")
    print(f"✓ Méthode: {response3.get('method')}")
    
    if response3.get('trend_analysis'):
        trend = response3['trend_analysis']
        print(f"\n📈 TENDANCE:")
        print(f"   - Type: {trend.get('tendance', 'N/A')}")
        print(f"   - Variation: {trend.get('variation_totale_pct', 0):+.2f}%")
        
        if trend.get('insights'):
            print(f"\n💡 INSIGHTS:")
            for insight in trend['insights']:
                print(f"   - {insight}")
    
    # Afficher les insights métier
    if response3.get('business_insights'):
        print(f"\n💼 INSIGHTS MÉTIER ({len(response3['business_insights'])}):")
        for i, insight in enumerate(response3['business_insights'], 1):
            print(f"   {i}. {insight}")
    
    # Afficher les anomalies
    if response3.get('anomalies'):
        print(f"\n⚠️ ANOMALIES DÉTECTÉES ({len(response3['anomalies'])}):")
        for i, anomaly in enumerate(response3['anomalies'], 1):
            severity_icon = '🔴' if anomaly['severity'] == 'error' else '⚠️'
            print(f"   {severity_icon} {anomaly['message']}")
    
    print("\n" + "=" * 80)
    print("✅ Tests terminés avec succès")
    print("=" * 80)


if __name__ == '__main__':
    test_trend_analysis()
