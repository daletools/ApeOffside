#TODO: Add URL to test Gemini AI API and ensure it is working
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('gemini', views.generate, name='generate'),
]
