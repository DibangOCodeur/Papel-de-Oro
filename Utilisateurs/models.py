from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UtilisateurManager
from django.db.models import Sum


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
        ('collaborateur', 'Collaborateur')
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

    parrain = models.ForeignKey('Collaborateur', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

    @property
    def dernier_paiement(self):
        """Retourne le dernier paiement de l'étudiant"""
        return self.paiements.order_by('-date_paiement').first()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ======================
# MODEL COLLABORATEUR
# ======================
class Collaborateur(Utilisateur):
    matricule = models.CharField(max_length=50, unique=True, blank=True, null=True)
    code_parainage = models.CharField(max_length=50, unique=True, blank=True, null=True)
    date_inscription_collaborateur = models.DateField(auto_now_add=True)
    
    # Mot de passe par défaut
    DEFAULT_PASSWORD = "@papel@"

    class Meta:
        verbose_name = "Collaborateur"
        verbose_name_plural = "Collaborateurs"

    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour générer automatiquement matricule et code_parainage"""
        from django.contrib.auth.hashers import make_password
        
        # Définir le rôle
        self.role = 'collaborateur'
        
        # Générer le matricule si ce n'est pas déjà fait
        if not self.matricule:
            self.matricule = self.generer_matricule()
        
        # Générer le code de parrainage si ce n'est pas déjà fait
        if not self.code_parainage:
            self.code_parainage = self.generer_code_parainage()
        
        # Si c'est une nouvelle instance (pas de mot de passe défini), utiliser le mot de passe par défaut
        if not self.pk and not self.password:
            self.password = make_password(self.DEFAULT_PASSWORD)
        
        super().save(*args, **kwargs)

    def generer_matricule(self):
        """
        Génère un matricule unique au format: COL + année + numéro séquentiel
        Exemple: COL2026001, COL2026002, etc.
        """
        from django.utils import timezone
        
        # Année en cours
        annee = timezone.now().strftime('%Y')
        
        # Compter le nombre de collaborateurs existants
        dernier_matricule = Collaborateur.objects.filter(
            matricule__startswith=f'COL{annee}'
        ).order_by('-matricule').first()
        
        if dernier_matricule and dernier_matricule.matricule:
            # Extraire le numéro séquentiel
            try:
                dernier_numero = int(dernier_matricule.matricule[7:])  # après COL+année (7 caractères)
                nouveau_numero = dernier_numero + 1
            except:
                nouveau_numero = 1
        else:
            nouveau_numero = 1
        
        # Formater avec 3 chiffres (001, 002, ...)
        matricule = f"COL{annee}{nouveau_numero:03d}"
        
        # Vérifier l'unicité
        while Collaborateur.objects.filter(matricule=matricule).exists():
            nouveau_numero += 1
            matricule = f"COL{annee}{nouveau_numero:03d}"
        
        return matricule

    def generer_code_parainage(self):
        """
        Génère un code de parainage unique
        Format: DBG + 6 caractères aléatoires (lettres majuscules et chiffres)
        Exemple: DBG7F3K9, DBG2M5N8, etc.
        """
        import random
        import string
        
        # Générer un code aléatoire
        while True:
            # 6 caractères aléatoires (lettres majuscules + chiffres)
            random_part = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=6
            ))
            code = f"DBG{random_part}"
            
            # Vérifier l'unicité
            if not Collaborateur.objects.filter(code_parainage=code).exists():
                return code

    @property
    def nombre_etudiant(self):
        return self.etudiant_set.count()
    
    @property
    def montant_total_parrain(self):
        from Paiements.models import Paiement
        return Paiement.objects.filter(etudiant__parrain=self).aggregate(
            Sum('commission_parrain')
        )['commission_parrain__sum'] or 0

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.matricule or 'Sans matricule'})"