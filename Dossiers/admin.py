from django.contrib import admin
from .models import Dossier, AnneeAcademique, Niveau


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'paiement__montant_total','statut', 'livraison', 'date_creation', 'date_modification', 'date_livraison')
    list_filter = ('statut', 'livraison')
    search_fields = ('etudiant__utilisateur__username', 'etudiant__utilisateur__first_name', 'etudiant__utilisateur__last_name')
    readonly_fields = ('date_creation', 'date_modification', 'date_livraison')

@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    list_display = ('annee_academique',)
    list_filter = ('annee_academique',)
    search_fields = ('annee_academique',)

@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('niveau',)
    list_filter = ('niveau',)
    search_fields = ('niveau',)