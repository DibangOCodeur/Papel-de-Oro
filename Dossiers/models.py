from django.db import models
from Utilisateurs.models import Etudiant
from Paiements.models import Paiement
import os
from datetime import date


# ===============================
# MODEL DOSSIER DE L'ETUDIANT
# ===============================

def memoire_upload_path(instance, filename):
    """
    Génère le chemin de sauvegarde pour les mémoires.
    Format: memoires/{annee_academique}/{matricule}/{nom_fichier}
    """
    # Si le dossier n'a pas encore d'étudiant associé
    if not instance.etudiant:
        return f"memoires/orphans/{filename}"
    
    # Récupérer l'année académique (si disponible)
    today = date.today().strftime('%Y-%m-%d')
    
    nom_etudiant = f"{instance.etudiant.last_name}_{instance.etudiant.first_name}"
    nom_etudiant = nom_etudiant.replace(' ', '_').replace("'", "").lower()

    return os.path.join(
        'Memoire',
        today,
        nom_etudiant,
        filename
    )

class Dossier(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    paiement = models.ForeignKey(Paiement, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.BooleanField(default=False)
    livraison = models.BooleanField(default=False)
    support_pdf = models.FileField(upload_to=memoire_upload_path, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_livraison = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dossier de {self.etudiant}"

    def validation_dossier(self):
        self.statut = True
        self.save()

    def livraison_dossier(self):
        self.livraison = True
        self.save()
    
    def supprimer_dossier(self):
        self.delete()


#=======================
# Choix
#=======================
ANNEE_CHOICES = (
    ('2025-2026','2025-2026'),
    ('2026-2027','2026-2027'),
)

NIVEAU_CHOICES = (
    ('LICENCE 3','LICENCE 3'),
    ('MASTER 2','MASTER 2'),
)

#=======================
# MODELS ANNEE ET NIVEAU
#=======================
class AnneeAcademique(models.Model):
    annee_academique = models.CharField(max_length=20, choices=ANNEE_CHOICES, default='2025-2026')

    class Meta:
        verbose_name = "Année Académique"
        verbose_name_plural = "Années Académiques"
    def __str__(self):
        return self.annee_academique

class Niveau(models.Model):
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='LICENCE 3')

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
    def __str__(self):
        return self.niveau