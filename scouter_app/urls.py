# ============================================================
# scouter_app/urls.py
# ============================================================

from django.urls import path
from . import views

urlpatterns = [
    path('',        views.index,          name='index'),
    path('report/', views.report_view,    name='report'),
    path('api/scouting/', views.scouting_report, name='api_scouting'),
]
