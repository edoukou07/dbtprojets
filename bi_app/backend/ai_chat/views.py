"""
API Views pour le chatbot IA
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from .query_engine import HybridQueryEngine
from .chat_service import ChatService


# Initialiser le moteur global avec la clé OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
query_engine = HybridQueryEngine(openai_api_key=OPENAI_API_KEY)
chat_service = ChatService(query_engine)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_message(request):
    """
    Endpoint principal pour envoyer un message au chatbot
    
    POST /api/ai/chat/
    Body: {
        "question": "Quel est le CA total ?",
        "prefer_ai": false  // optionnel
    }
    """
    question = request.data.get('question', '').strip()
    prefer_ai = request.data.get('prefer_ai', False)
    
    if not question:
        return Response({
            'error': 'Question requise'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Traiter la question
    response = chat_service.process_chat_message(question, prefer_ai)
    
    return Response(response)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_capabilities(request):
    """
    Retourne les capacités du chatbot
    
    GET /api/ai/capabilities/
    """
    capabilities = query_engine.get_capabilities()
    
    return Response({
        'capabilities': capabilities,
        'openai_configured': query_engine.ai_engine.enabled
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_suggestions(request):
    """
    Retourne des suggestions de questions
    
    GET /api/ai/suggestions/
    """
    suggestions = query_engine.rule_engine.get_suggestions()
    
    return Response({
        'suggestions': suggestions
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rules(request):
    """
    Retourne toutes les règles chargées avec leurs détails
    
    GET /api/ai/rules/
    GET /api/ai/rules/?category=financier
    """
    category_filter = request.GET.get('category', None)
    
    rules = []
    for pattern in query_engine.rule_engine.patterns:
        # Filtrer par catégorie si demandé
        if category_filter and pattern.category != category_filter:
            continue
            
        rules.append({
            'category': pattern.category,
            'description': pattern.description,
            'patterns': pattern.patterns,
            'example': pattern.patterns[0] if pattern.patterns else '',
            'sql_template': pattern.sql_template[:200] + '...' if len(pattern.sql_template) > 200 else pattern.sql_template
        })
    
    # Grouper par catégorie
    categories = {}
    for rule in rules:
        cat = rule['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(rule)
    
    return Response({
        'total': len(rules),
        'rules': rules,
        'by_category': categories,
        'categories': list(categories.keys())
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def configure_openai(request):
    """
    Configure la clé API OpenAI (pour admin uniquement)
    
    POST /api/ai/configure/
    Body: {
        "api_key": "sk-..."
    }
    """
    if not request.user.is_staff:
        return Response({
            'error': 'Permission refusée'
        }, status=status.HTTP_403_FORBIDDEN)
    
    api_key = request.data.get('api_key', '').strip()
    
    if not api_key:
        return Response({
            'error': 'Clé API requise'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Réinitialiser le moteur avec la nouvelle clé
    global query_engine, chat_service
    query_engine = HybridQueryEngine(openai_api_key=api_key)
    chat_service = ChatService(query_engine)
    
    return Response({
        'success': True,
        'message': 'Clé API OpenAI configurée',
        'ai_enabled': query_engine.ai_engine.enabled
    })
