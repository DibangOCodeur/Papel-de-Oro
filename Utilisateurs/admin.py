from django.contrib import admin
from .models import Utilisateur, Etudiant, Filiere, Collaborateur
from django.db.models import Sum, Count, Q



@admin.register(Utilisateur)
class CustomUtilisateurAdmin(admin.ModelAdmin):
    model = Utilisateur
    list_display = ('email', 'first_name', 'last_name', 'role', 'contact','date_joined')
    list_filter = ('role',)
    search_fields = ('contact', 'email', 'first_name', 'last_name')

    fieldsets = (
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'contact', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    model = Etudiant
    list_display = ('first_name', 'last_name', 'matricule', 'filiere', 'date_inscription')
    list_filter = ('filiere', 'date_inscription')
    search_fields = ('first_name', 'last_name', 'email', 'matricule')

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'abreviation','cycle')
    search_fields = ('nom', 'abreviation','cycle')
    ordering = ('nom',)


@admin.register(Collaborateur)
class CollaborateurAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email','matricule', 'code_parainage','nombre_etudiant_display','montant_total_parrain_display', 'date_inscription_collaborateur')
    list_filter = ('date_inscription_collaborateur', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'matricule', 'code_parainage')
    readonly_fields = ('date_inscription_collaborateur',)
    ordering = ('-date_inscription_collaborateur',)
    
    # Méthode pour afficher le nombre d'étudiants
    def nombre_etudiant_display(self, obj):
        return obj.nombre_etudiant
    nombre_etudiant_display.short_description = "Nb étudiants"
    nombre_etudiant_display.admin_order_field = 'nb_etudiants'  # Permet le tri
    
    # Méthode pour afficher le montant total des paiements
    def montant_total_parrain_display(self, obj):
        return obj.montant_total_parrain
    montant_total_parrain_display.short_description = "Montant Parrainage"
    montant_total_parrain_display.admin_order_field = 'montant_parrainage'  # Permet le tri
    
    # Optimiser les requêtes avec une annotation
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Annoter avec le nombre d'étudiants pour optimiser les performances
        queryset = queryset.annotate(
            nb_etudiants=Count('etudiant')
        )
        return queryset