from django.urls import path

from . import views

app_name = 'ai_insights'

urlpatterns = [
    # Chatbot API endpoint
    path('chatbot/', views.chatbot_view, name='chatbot'),
]
