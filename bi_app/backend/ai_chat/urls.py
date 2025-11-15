"""
URLs pour le module AI Chat
"""

from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_message, name='ai_chat'),
    path('capabilities/', views.get_capabilities, name='ai_capabilities'),
    path('suggestions/', views.get_suggestions, name='ai_suggestions'),
    path('rules/', views.get_rules, name='ai_rules'),
    path('configure/', views.configure_openai, name='ai_configure'),
]
