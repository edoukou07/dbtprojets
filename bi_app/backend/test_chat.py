#!/usr/bin/env python
"""Script de test rapide pour le chatbot"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from ai_chat.chat_service import ChatService
from ai_chat.query_engine import HybridQueryEngine
from dotenv import load_dotenv

load_dotenv()

# Test simple
print("🔍 Test du chatbot...")
try:
    qe = HybridQueryEngine(os.getenv('OPENAI_API_KEY'))
    cs = ChatService(qe)
    
    print("\n📝 Test 1: CA total")
    result = cs.process_chat_message('CA total')
    print(f"✅ Success: {result.get('success')}")
    print(f"💡 Insights: {len(result.get('business_insights', []))} insights")
    print(f"⚠️ Anomalies: {len(result.get('anomalies', []))} anomalies")
    if result.get('anomalies'):
        for a in result.get('anomalies', []):
            print(f"   - {a.get('message')}")
    
    print("\n📝 Test 2: Zones avec occupation > 80%")
    result2 = cs.process_chat_message('zones avec taux > 80%')
    print(f"✅ Success: {result2.get('success')}")
    print(f"💡 Insights: {len(result2.get('business_insights', []))} insights")
    print(f"⚠️ Anomalies: {len(result2.get('anomalies', []))} anomalies")
    if result2.get('anomalies'):
        for a in result2.get('anomalies', []):
            print(f"   - {a.get('message')}")
    
except Exception as e:
    print(f"❌ Erreur: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
