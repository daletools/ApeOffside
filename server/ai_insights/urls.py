"""
URL configuration for the ai_insights application.
This module defines the URL patterns for AI-powered features including chatbot and player insights.
"""

from django.urls import path

from . import views

# Namespace for the ai_insights app - used to organize and reference URL patterns
app_name = "ai_insights"

urlpatterns = [
    # URL pattern for the Gemini chatbot API endpoint
    # Handles chat interactions and AI responses through views.gemini_view
    path("chatbot/", views.gemini_view, name="chatbot"),

    # URL pattern for retrieving AI-generated player insights
    # Processes and returns analytical insights about players through views.fetch_player_insights
    path("insights/", views.fetch_player_insights, name="insights"),
]
