from django.contrib import admin
from .models import Paiement, HistoriquePaiement
from django.utils.html import format_html

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'frais_impression', 'frais_annexe', 'montant_total_colore', 'commission_colore','reduction_percentage','montant_reduction','reduction_grattee','reduction_revealed','reference', 'service_annexe','jeu_reduction', 'statut')
    search_fields = ('etudiant', 'frais_annexe', 'montant_total', 'commission','jeu_reduction')
    readonly_fields = ('frais_annexe','montant_total','reference')
    fieldsets = (
        ('Informations de base', {
            'fields': ('etudiant', 'source', 'statut')
        }),
        ('Détails', {
            'fields': ('frais_impression', 'service_annexe', 'frais_annexe', 'intitule_annexes','reduction_percentage','montant_reduction','reduction_grattee','reduction_revealed', 'montant_total', 'commission', 'jeu_reduction')
        }),
    )
     # Méthode pour afficher la commission en vert
    def commission_colore(self, obj):
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 2px 5px; border-radius: 3px;">{} FCFA</span>',
            obj.commission
        )
    commission_colore.short_description = "Commission"

    # Méthode pour afficher le montant total en bleu
    def montant_total_colore(self, obj):
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 2px 5px; border-radius: 3px;">{} FCFA</span>',
            obj.montant_total
        )
    montant_total_colore.short_description = "Montant total"

@admin.register(HistoriquePaiement)
class HistoriquePaiementAdmin(admin.ModelAdmin):
    list_display = ('paiement__etudiant','paiement__source','paiement__reference', 'date_historique', 'statut', 'montant_total')
    list_filter = ('date_historique', 'statut')
    search_fields = ('paiement__etudiant__nom', 'paiement__etudiant__prenom')
    readonly_fields = ('date_historique', 'montant_total')