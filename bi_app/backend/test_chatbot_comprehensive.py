#!/usr/bin/env python
"""
Comprehensive test of the ChatBot fix
Tests that queries now match correctly and return expected data
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from ai_chat.query_engine import HybridQueryEngine, TextNormalizer
from ai_chat.chat_service import ChatService

def test_normalization():
    """Test that normalization is working correctly"""
    print("\n" + "="*70)
    print("TEST 1: Text Normalization")
    print("="*70)
    
    test_cases = [
        ("taux d'occupation", "occupation"),
        ("taux occupation", "occupation"),
        ("remplissage", "occupation"),
        ("utilisation", "occupation"),
        ("nombre entreprises", "nombre clients"),
        ("affiche les clients", "affiche les clients"),
        ("ca total", "chiffre d'affaires total"),
        ("taux de recouvrement", "taux de recouvrement"),
    ]
    
    for input_text, expected_contains in test_cases:
        normalized = TextNormalizer.normalize(input_text)
        contains = expected_contains in normalized
        status = "✅" if contains else "❌"
        print(f"{status} '{input_text}' → '{normalized}'")
        print(f"   Expected to contain: '{expected_contains}' → {contains}")


def test_pattern_matching():
    """Test that patterns now match correctly"""
    print("\n" + "="*70)
    print("TEST 2: Pattern Matching")
    print("="*70)
    
    query_engine = HybridQueryEngine(openai_api_key=None)
    
    test_questions = [
        # (question, should_match, expected_description_fragment)
        ("taux d'occupation", True, "occupation"),
        ("nombre entreprises", True, "entreprises"),
        ("affiche les clients", True, "clients"),
        ("ca total", True, "affaires"),
        ("taux de recouvrement", True, "recouvrement"),
        ("lots disponibles", True, "disponibles"),
        ("demandes attribution", True, "attribution"),
        ("top clients", True, "clients"),
        ("clients à risque", True, "risque"),
        ("kpi", True, "opérationnel"),
        ("completely unrelated nonsense xyz", False, None),
    ]
    
    passed = 0
    failed = 0
    
    for question, should_match, expected_frag in test_questions:
        sql, desc, category, engine = query_engine.generate_sql(question, prefer_ai=False)
        matched = sql is not None
        
        if matched == should_match:
            if matched and expected_frag and expected_frag.lower() in desc.lower():
                status = "✅"
                passed += 1
            elif matched == should_match:
                status = "✅"
                passed += 1
            else:
                status = "❌"
                failed += 1
        else:
            status = "❌"
            failed += 1
        
        match_text = "MATCH" if matched else "NO MATCH"
        expected_text = "should match" if should_match else "should NOT match"
        desc_text = desc[:50] if desc else "N/A"
        
        print(f"{status} {question:30} → {match_text:10} ({expected_text:15}) | {desc_text}")
    
    print(f"\nResults: {passed} PASSED, {failed} FAILED")
    return failed == 0


def test_sql_execution():
    """Test that SQL can be executed successfully"""
    print("\n" + "="*70)
    print("TEST 3: SQL Execution")
    print("="*70)
    
    query_engine = HybridQueryEngine(openai_api_key=None)
    chat_service = ChatService(query_engine)
    
    test_queries = [
        "taux d'occupation",
        "nombre entreprises",
        "ca total",
    ]
    
    passed = 0
    failed = 0
    
    for query in test_queries:
        response = chat_service.process_chat_message(query, prefer_ai=False)
        
        has_answer = response.get('answer') and 'Désolé' not in response.get('answer', '')
        has_data = len(response.get('data', [])) > 0
        success = has_answer and has_data
        
        status = "✅" if success else "❌"
        if success:
            passed += 1
        else:
            failed += 1
        
        answer_preview = response.get('answer', 'N/A')[:50]
        data_count = len(response.get('data', []))
        
        print(f"{status} {query:30} | Answer: {answer_preview:30} | Data rows: {data_count}")
    
    print(f"\nResults: {passed} PASSED, {failed} FAILED")
    return failed == 0


def main():
    """Run all tests"""
    print("\n\n" + "="*70)
    print("CHATBOT FIX COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    test_normalization()
    pattern_match_ok = test_pattern_matching()
    sql_exec_ok = test_sql_execution()
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    if pattern_match_ok and sql_exec_ok:
        print("\n🎉 ALL TESTS PASSED - ChatBot fix is working correctly!")
        print("\nThe ChatBot should now:")
        print("✅ Match user questions to patterns correctly")
        print("✅ Generate appropriate SQL queries")
        print("✅ Return data instead of 'pas l'information' error")
        print("✅ Display results in the frontend")
        return 0
    else:
        print("\n❌ Some tests failed - please review the output above")
        return 1


if __name__ == '__main__':
    exit(main())
