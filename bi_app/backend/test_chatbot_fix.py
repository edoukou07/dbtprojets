"""
Test script to verify ChatBot query pattern matching is working
"""
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from ai_chat.query_engine import HybridQueryEngine
from ai_chat.chat_service import ChatService

# Initialize
query_engine = HybridQueryEngine(openai_api_key=None)
chat_service = ChatService(query_engine)

# Test comprehensive suite
test_questions = [
    # Financier
    ('Quel est le CA total ?', 'financier'),
    ('ca par mois', 'financier'),
    ('taux de recouvrement', 'financier'),
    ('impayés', 'financier'),
    ('performance par zone', 'financier'),
    
    # Occupation
    ('taux d\'occupation', 'occupation'),
    ('lots disponibles', 'occupation'),
    ('demandes attribution', 'occupation'),
    
    # Clients
    ('nombre entreprises', 'clients'),
    ('top clients', 'clients'),
    ('clients par secteur', 'clients'),
    ('clients à risque', 'clients'),
    ('affiche les clients', 'clients'),
    ('liste des clients', 'clients'),
    
    # Opérationnel
    ('kpi', 'operationnel'),
    ('collectes', 'operationnel'),
]

print('\n' + '='*80)
print('COMPREHENSIVE CHATBOT QUERY MATCHING TEST')
print('='*80)

success = 0
failed = 0
failed_queries = []

for q, expected_category in test_questions:
    sql, desc, category, engine = query_engine.generate_sql(q, prefer_ai=False)
    if sql:
        success += 1
        status = 'OK'
        cat_match = category == expected_category if category else False
        cat_status = 'OK' if cat_match else 'CAT_MISMATCH'
    else:
        failed += 1
        status = 'FAIL'
        cat_status = 'N/A'
        failed_queries.append(q)
    
    result_text = desc if desc else 'NO MATCH'
    print(f'{status:5} | {cat_status:10} | {q:30} | {result_text}')

print('\n' + '='*80)
print(f'RESULTS: {success} SUCCESS, {failed} FAILED out of {len(test_questions)} tests')
if failed_queries:
    print(f'\nFailed queries ({len(failed_queries)}):')
    for q in failed_queries:
        print(f'  ❌ {q}')
else:
    print('\n🎉 ALL TESTS PASSED!')
print('='*80)
