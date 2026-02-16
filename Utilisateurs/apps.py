# Utilisateurs/apps.py
from django.apps import AppConfig

class UtilisateursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Utilisateurs'
    
    def ready(self):
        import Utilisateurs.signals  # Import des signaux