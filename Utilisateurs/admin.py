from django.contrib import admin
from .models import Utilisateur, Etudiant, Filiere

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