from django.urls import path

from . import views

app_name = 'ai_insights'

urlpatterns = [
    # Gemini API endpoint
    path('chatbot/', views.gemini_view, name='chatbot'),
]
