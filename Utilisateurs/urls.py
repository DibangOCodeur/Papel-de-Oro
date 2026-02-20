from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import ListeEtudiantView, ExportExcelView, DetailEtudiantView, DeleteEtudiantiew, UpdateEtudiantView, CollaborateurCreateView


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

    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # Changement de mot de passe
    path('changer-mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),
    
    # Dashboard collaborateur
    path('collaborateur/dashboard/', views.tableau_de_bord_collaborateur, name='dashboard_collaborateur'),
    path('Collaborateurs/liste-filleuls/', views.liste_filleuls, name='liste_filleuls'),
    path('inscription/', CollaborateurCreateView.as_view(), name='inscription_collaborateur'),
    path('collaborateur/recu/<int:collaborateur_id>/', views.recu_collaborateur, name='recu_collaborateur'),
    path('collaborateurs/listes/', views.CollaborateurListView.as_view(), name='liste_collaborateurs'),
    path('collaborateur/detail/<int:pk>/', views.CollaborateurDetailView.as_view(), name='detail_collaborateur'),
    path('collaborateur/update/<int:pk>/', views.CollaborateurUpdateView.as_view(), name='update_collaborateur'),
    path('collaborateur/delete/<int:pk>/', views.CollaborateurDeleteView.as_view(), name='delete_collaborateur'),

    path('collaborateur/memoires/imprimes/', views.liste_memoires_imprimes, name='liste_memoires_imprimes'),
    path('collaborateur/memoires/details/<int:dossier_id>/', views.details_memoire, name='details_memoire'),
    path('collaborateur/memoires/telecharger/<int:dossier_id>/', views.telecharger_pdf, name='telecharger_pdf'),
    path('collaborateur/memoires/marquer-livre/<int:dossier_id>/', views.marquer_livre, name='marquer_livre'),
    path('collaborateur/memoires/encours/', views.memoires_encours, name='memoires_encours'),




]




