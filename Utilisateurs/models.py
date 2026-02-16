from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UtilisateurManager

# ======================
# MODEL UTILISATEUR
# ======================

class Utilisateur(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('etudiant', 'Etudiant'),
        ('personnel', 'Personnel')
    ])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UtilisateurManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

# ======================
# CHOIX
# ======================

Cycle_CHOICES = [
    ('UNIVERSITAIRE', 'UNIVERSITAIRE'),
    ('PROFESSIONNEL', 'PROFESSIONNEL'),
]

Filiere_choices = (
    ('AUDIT ET CONTRÔLE DE GESTION', 'AUDIT ET CONTRÔLE DE GESTION'),
    ('ADMINISTRATION DES AFFAIRES', 'ADMINISTRATION DES AFFAIRES'),
    ('ANGLAIS ', 'ANGLAIS'),
    ('SCIENCE JURIDIQUE OPTION DROIT PRIVE', 'SCIENCE JURIDIQUE OPTION DROIT PRIVE'),
    ('SCIENCE JURIDIQUE OPTION DROIT PUBLIC', 'SCIENCE JURIDIQUE OPTION DROIT PUBLIC'),
    ('FINANCE BANQUE ASSURANCE', 'FINANCE BANQUE ASSURANCE'),
    ('FINANCE COMPTABILITE ET GESTION DES ENTREPRISES', 'FINANCE COMPTABILITE ET GESTION DES ENTREPRISES'),
    ('GENIE CIVIL OPTION BATIMENT', 'GENIE CIVIL OPTION BATIMENT'),
    ('GENIE CIVIL OPTION TRAVAUX PUBLIC', 'GENIE CIVIL OPTION TRAVAUX PUBLIC'),
    ('GESTION DES RESSOURCES HUMAINE', 'GESTION DES RESSOURCES HUMAINE'),
    ('INFORMATIQUE OPTION GENIE LOGICIEL', 'INFORMATIQUE OPTION GENIE LOGICIEL'),
    ('LETTRES MODERNES', 'LETTRES MODERNES'),
    ('MARKETING MANAGEMENT', 'MARKETING MANAGEMENT'),
    ('MINE GEOLOGIE ET PETRÔLE', 'MINE GEOLOGIE ET PETRÔLE'),
    ('RESEAUX INFORMATIQUE ET TELECOMMUNICATION', 'RESEAUX INFORMATIQUE ET TELECOMMUNICATION'),
    ('SCIENCE ECONOMIQUE OPTION ECONOMIE', 'SCIENCE ECONOMIQUE OPTION ECONOMIE'),
    ('SCIENCE ECONOMIQUE OPTION GESTION', 'SCIENCE ECONOMIQUE OPTION GESTION'),
    ("SCIENCE DE L'INFORMATION ET DE LA COMMUNICATION", " SCIENCE DE L'INFORMATION ET DE LA COMMUNICATION"),
    ('SOCIOLOGIE ET ETHNOLOGIE', 'SOCIOLOGIE ET ETHNOLOGIE'),
    ('TOURISME HÔTELERIE', 'TOURISME HÔTELERIE'),
    ('TRANSPORT LOGISTIQUE ', 'TRANSPORT LOGISTIQUE'),
)

# ======================
# MODEL FILIERE
# ======================
class Filiere(models.Model):
    nom = models.CharField(max_length=100, choices=Filiere_choices, unique=True)
    abreviation = models.CharField(max_length=10, blank=True, null=True, default='IIPEA')
    cycle = models.CharField(max_length=50, choices=Cycle_CHOICES, blank=True, null=True, default='UNIVERSITAIRE')
    def __str__(self):
        return f'{self.nom} - ({self.abreviation})'

# ======================
# MODEL ETUDIANT
# ======================

class Etudiant(Utilisateur):
    matricule = models.CharField(max_length=50, blank=True, null=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    theme_memoire = models.CharField(max_length=255, blank=False, null=False)
    date_inscription = models.DateField(auto_now_add=True)
    annee_academique = models.ForeignKey('Dossiers.AnneeAcademique', on_delete=models.CASCADE)
    niveau = models.ForeignKey('Dossiers.Niveau', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

    @property
    def dernier_paiement(self):
        """Retourne le dernier paiement de l'étudiant"""
        return self.paiements.order_by('-date_paiement').first()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"