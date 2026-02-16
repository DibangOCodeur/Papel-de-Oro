from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import ListeEtudiantView, ExportExcelView, DetailEtudiantView, DeleteEtudiantiew, UpdateEtudiantView


urlpatterns = [
    path('', views.connexion, name='connexion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ajouter_etudiant/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('generer-reçu/<int:paiement_id>/', views.generer_reçu, name='generer_reçu'),
    path('liste_etudiant/', ListeEtudiantView.as_view(), name='liste_etudiant'),
    path('etudiants/export/excel/', ExportExcelView.as_view(), name='export_etudiants_excel'),
    path('etudiants/export/excel/selection/', ExportExcelView.as_view(), name='export_etudiants_selection_excel'),
    path('etudiant/<int:pk>/', DetailEtudiantView.as_view(), name='detail_etudiant'),
    path('etudiant/delete/<int:pk>/', views.DeleteEtudiantiew.as_view(), name='delete_etudiant'),
    path('etudiant/update/<int:pk>/', UpdateEtudiantView.as_view(), name='update_etudiant'),
]




