# recommender/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('recommendations/', views.recommend_internships, name='recommendations'),
]