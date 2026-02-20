from django.contrib import admin
from .models import Paiement, HistoriquePaiement
from django.utils.html import format_html
from django.db import models

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = (
        'etudiant', 
        'frais_impression', 
        'frais_annexe', 
        'montant_total_colore', 
        'commission_colore',
        'commission_parrain_colore',
        'a_un_parrain',
        'reduction_percentage',
        'montant_reduction',
        'reduction_grattee',
        'reduction_revealed',
        'reference', 
        'service_annexe',
        'jeu_reduction', 
        'statut'
    )
    
    list_filter = (
        'statut', 
        'source', 
        'service_annexe', 
        'jeu_reduction',
        'reduction_grattee',
        'reduction_revealed',
        'date_paiement',
    )
    
    search_fields = (
        'etudiant__nom', 
        'etudiant__prenom', 
        'etudiant__matricule',
        'reference', 
        'commission', 
        'commission_parrain'
    )
    
    readonly_fields = (
        'frais_annexe', 
        'montant_total', 
        'reference', 
        'commission_parrain',
        'montant_reduction'
    )
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('etudiant', 'source', 'statut', 'reference')
        }),
        ('Détails du paiement', {
            'fields': ('frais_impression', 'service_annexe', 'intitule_annexes', 'frais_annexe')
        }),
        ('Commission', {
            'fields': ('commission', 'commission_parrain'),
            'classes': ('wide',),
            'description': 'La commission parrain est automatiquement calculée (20% de la commission)'
        }),
        ('Jeu de réduction', {
            'fields': ('jeu_reduction', 'reduction_percentage', 'montant_reduction', 
                      'reduction_grattee', 'reduction_revealed'),
            'classes': ('wide',),
        }),
        ('Total', {
            'fields': ('montant_total',),
        }),
    )
    
    # Méthode pour afficher si l'étudiant a un parrain
    def a_un_parrain(self, obj):
        if obj.etudiant.parrain:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 2px 5px; border-radius: 3px;">{}</span>',
                '✓ Oui'
            )
        return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 2px 5px; border-radius: 3px;">{}</span>',
                '✗ Non'
            )
    a_un_parrain.short_description = "Parrain"
    a_un_parrain.admin_order_field = 'etudiant__parrain'
    
    # Méthode pour afficher la commission en vert
    def commission_colore(self, obj):
        commission_value = obj.commission if obj.commission is not None else 0
        if commission_value > 0:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{} FCFA</span>',
                str(commission_value)
            )
        return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
                '0 FCFA'
            )
    commission_colore.short_description = "Commission"
    commission_colore.admin_order_field = 'commission'
    
    # Méthode pour afficher le montant total en bleu
    def montant_total_colore(self, obj):
        montant_value = obj.montant_total if obj.montant_total is not None else 0
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{} FCFA</span>',
            str(montant_value)
        )
    montant_total_colore.short_description = "Montant total"
    montant_total_colore.admin_order_field = 'montant_total'
    
    # Méthode pour afficher la commission parrain en orange
    def commission_parrain_colore(self, obj):
        commission_parrain_value = obj.commission_parrain if obj.commission_parrain is not None else 0
        
        if obj.etudiant.parrain and commission_parrain_value > 0:
            return format_html(
                '<span style="background-color: #FFA500; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{} FCFA</span>',
                str(commission_parrain_value)
            )
        elif obj.etudiant.parrain:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 4px;">{}</span>',
                'En attente'
            )
        return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
                'Pas de parrain'
            )
    commission_parrain_colore.short_description = "Commission parrain"
    commission_parrain_colore.admin_order_field = 'commission_parrain'
    
    # Actions personnalisées
    actions = ['reveler_reductions_selectionnees', 'recalculer_commissions_parrain']
    
    def reveler_reductions_selectionnees(self, request, queryset):
        count = 0
        for paiement in queryset:
            if paiement.reveler_reduction():
                count += 1
        self.message_user(request, f"{count} réduction(s) ont été révélées avec succès.")
    reveler_reductions_selectionnees.short_description = "Révéler les réductions sélectionnées"
    
    def recalculer_commissions_parrain(self, request, queryset):
        count = 0
        for paiement in queryset:
            if paiement.calculer_commission_parrain():
                paiement.save()
                count += 1
        self.message_user(request, f"{count} commission(s) parrain ont été recalculées.")
    recalculer_commissions_parrain.short_description = "Recalculer les commissions parrain"
    
    # Personnalisation du formulaire d'édition
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # En mode édition
            readonly_fields.extend(['etudiant', 'reference'])
        return readonly_fields
    
    def get_fieldsets(self, request, obj=None):
        if not obj:  # En mode création
            return (
                ('Informations de base', {
                    'fields': ('etudiant', 'source', 'statut')
                }),
                ('Détails du paiement', {
                    'fields': ('frais_impression', 'service_annexe', 'intitule_annexes')
                }),
                ('Commission', {
                    'fields': ('commission',),
                    'description': 'La commission parrain sera automatiquement calculée après la création'
                }),
                ('Jeu de réduction', {
                    'fields': ('jeu_reduction',),
                }),
            )
        return self.fieldsets


@admin.register(HistoriquePaiement)
class HistoriquePaiementAdmin(admin.ModelAdmin):
    list_display = (
        'get_etudiant_nom',
        'get_paiement_reference',
        'get_source',
        'date_historique', 
        'statut_colore', 
        'montant_total_colore'
    )
    
    list_filter = (
        'date_historique', 
        'statut',
        'paiement__source',
        'paiement__service_annexe'
    )
    
    search_fields = (
        'paiement__etudiant__nom', 
        'paiement__etudiant__prenom',
        'paiement__etudiant__matricule',
        'paiement__reference'
    )
    
    readonly_fields = (
        'paiement',
        'date_historique', 
        'montant_total',
        'statut'
    )
    
    fieldsets = (
        ('Informations de l\'historique', {
            'fields': ('paiement', 'date_historique')
        }),
        ('Détails', {
            'fields': ('statut', 'montant_total')
        }),
    )
    
    def get_etudiant_nom(self, obj):
        if obj.paiement and obj.paiement.etudiant:
            return f"{obj.paiement.etudiant.first_name} {obj.paiement.etudiant.last_name}"
        return "Non défini"
    get_etudiant_nom.short_description = "Étudiant"
    get_etudiant_nom.admin_order_field = 'paiement__etudiant__first_name'
    
    def get_paiement_reference(self, obj):
        if obj.paiement:
            return obj.paiement.reference
        return "Non défini"
    get_paiement_reference.short_description = "Référence"
    get_paiement_reference.admin_order_field = 'paiement__reference'
    
    def get_source(self, obj):
        if obj.paiement:
            return obj.paiement.get_source_display()
        return "Non défini"
    get_source.short_description = "Source"
    get_source.admin_order_field = 'paiement__source'
    
    def statut_colore(self, obj):
        if obj.statut:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
                '✓ Actif'
            )
        return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 4px;">{}</span>',
                '✗ Inactif'
            )
    statut_colore.short_description = "Statut"
    
    def montant_total_colore(self, obj):
        montant_value = obj.montant_total if obj.montant_total is not None else 0
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 4px 8px; border-radius: 4px;">{} FCFA</span>',
            str(montant_value)
        )
    montant_total_colore.short_description = "Montant"