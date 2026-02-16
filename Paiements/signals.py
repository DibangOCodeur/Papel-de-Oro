# Paiements/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Paiement
from Dossiers.models import Dossier

@receiver(post_save, sender=Paiement)
def associer_paiement_dossier(sender, instance, created, **kwargs):
    if created:
        try:
            # Option 1: Chercher un dossier existant sans paiement
            dossier = Dossier.objects.filter(etudiant=instance.etudiant).first()
            
            if dossier:
                # Associer le paiement au dossier
                dossier.paiement = instance
                dossier.save()
                print(f"✅ Paiement {instance.id} associé au dossier {dossier.id} pour {instance.etudiant.matricule}")
            else:
                # Option 2: Créer un nouveau dossier avec le paiement
                dossier = Dossier.objects.create(
                    etudiant=instance.etudiant,
                    paiement=instance,
                    statut=False,
                    livraison=False
                )
                print(f"✅ Nouveau dossier créé avec paiement pour {instance.etudiant.matricule}")
                
        except Exception as e:
            print(f"❌ Erreur association paiement-dossier: {str(e)}")