# cv_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('cv/',                               views.index,        name='cv_index'),
    path('cv/analyze/',                       views.analyze,      name='cv_analyze'),
    path('cv/strategy/<str:strategy_name>/',  views.strategy_viz, name='cv_strategy_viz'),
]
