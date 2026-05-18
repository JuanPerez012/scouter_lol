# scouter_app/urls.py
from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('',        views.index,       name='index'),
    path('report/', views.report_view, name='report'),
    # API REST para React
    path('api/nlp/scouting/',  api.api_full_scouting, name='api_nlp_scouting'),
    path('api/champions/',     api.api_champions,     name='api_champions'),
]
