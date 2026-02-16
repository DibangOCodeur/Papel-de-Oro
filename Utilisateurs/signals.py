# Utilisateurs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Etudiant
from Dossiers.models import Dossier

# Utilisateurs/signals.py - Optionnel, si vous voulez que le signal gère aussi les fichiers
@receiver(post_save, sender=Etudiant)
def creer_dossier_etudiant(sender, instance, created, **kwargs):
    if created and instance.role == 'etudiant':
        try:
            # Vérifier si un dossier existe déjà
            dossier_existant = Dossier.objects.filter(etudiant=instance).exists()
            
            if not dossier_existant:
                dossier = Dossier.objects.create(
                    etudiant=instance,
                    # Note: support_pdf n'est pas défini ici car il vient du formulaire
                    # Il sera mis à jour dans la vue après l'upload
                    statut=False,
                    livraison=False
                )
                print(f"✅ Dossier créé pour l'étudiant : {instance.matricule}")
            else:
                print(f"⚠️  Dossier déjà existant pour : {instance.matricule}")
                
        except Exception as e:
            print(f"❌ Erreur création dossier pour {instance.matricule}: {str(e)}")