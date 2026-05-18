# cv_app/urls.py
from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('cv/',                               views.index,        name='cv_index'),
    path('cv/analyze/',                       views.analyze,      name='cv_analyze'),
    path('cv/strategy/<str:strategy_name>/',  views.strategy_viz, name='cv_strategy_viz'),
    # API REST para React
    path('api/cv/strategy-positions/', api.api_strategy_positions, name='api_cv_positions'),
    path('api/cv/identify/',           api.api_identify_strategy,  name='api_cv_identify'),
]
