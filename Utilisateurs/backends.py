# Utilisateurs/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Utilisateur, Collaborateur

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Utilisateur.objects.get(email=email)
            
            if user.check_password(password):
                print(f"✅ Backend: utilisateur trouvé {email}, rôle: {user.role}")
                
                # Si c'est un collaborateur, retourner l'instance Collaborateur
                if user.role == 'collaborateur':
                    try:
                        collaborateur = Collaborateur.objects.get(pk=user.pk)
                        return collaborateur
                    except Collaborateur.DoesNotExist:
                        return user
                return user
            return None
        except Utilisateur.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Utilisateur.objects.get(pk=user_id)
        except Utilisateur.DoesNotExist:
            return None