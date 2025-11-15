"""
URL configuration for SIGETI BI project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/ai/', include('ai_chat.urls')),
]
