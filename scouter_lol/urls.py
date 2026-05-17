# ============================================================
# scouter_lol/urls.py
# ============================================================

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',  admin.site.urls),
    path('',        include('scouter_app.urls')),   # módulo NLP
    path('',        include('cv_app.urls')),         # módulo CV
]
