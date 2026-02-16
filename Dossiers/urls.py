from django.urls import path
from .import views

urlpatterns = [
    path('liste_memoire/', views.ListDossierView.as_view(), name='liste_memoire'),
    path('statistique/', views.statistiques, name='statistique'),
    path('statistiques/api/', views.statistiques_api, name='statistiques_api'),

]

