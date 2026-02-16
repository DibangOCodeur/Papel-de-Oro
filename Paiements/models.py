from django.db import models
from Utilisateurs.models import Etudiant
import uuid
from decimal import Decimal
import random

class Paiement(models.Model):

    SOURCE_PAIEMENT = [
        ('ESPECE', 'Espèce'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('WAVE_MONEY', 'Wave Money'),
    ]

    ANNEXE_CHOICES = [
        ('PAGE_DE_GARDE', 'Page de garde'),
        ('MISE_EN_FORME', 'Mise en forme'),
        ('COMPLET', 'Complet'),
    ]

    PRIX_ANNEXE = {
        'PAGE_DE_GARDE': Decimal('1000'),
        'MISE_EN_FORME': Decimal('4000'),
        'COMPLET': Decimal('5000'),
    }

    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='paiements')
    source = models.CharField(max_length=20, choices=SOURCE_PAIEMENT)
    statut = models.BooleanField(default=True)
    reference = models.CharField(max_length=100, unique=True, editable=False)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_paiement = models.DateTimeField(auto_now_add=True)

    frais_impression = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_annexe = models.BooleanField(default=False)
    frais_annexe = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    intitule_annexes = models.CharField(max_length=30, choices=ANNEXE_CHOICES, blank=True, null=True)

    jeu_reduction = models.BooleanField(default=False)

    reduction_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    montant_reduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reduction_grattee = models.BooleanField(default=False)
    reduction_revealed = models.BooleanField(default=False)

    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-date_paiement']

    # -----------------------------
    # SAVE UNIQUE ET CORRECT
    # -----------------------------
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.reference:
            self.reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"

        # Générer réduction seulement à la création
        if is_new and self.jeu_reduction:
            self.generer_reduction_aleatoire()

        self.calculer_frais_annexe()
        self.calculer_montant_total()

        super().save(*args, **kwargs)

        # Historique automatique
        HistoriquePaiement.objects.create(
            paiement=self,
            statut=self.statut,
            montant_total=self.montant_total
        )

    # -----------------------------
    # REDUCTION ALEATOIRE
    # -----------------------------
    def generer_reduction_aleatoire(self):
        rand = random.random()

        if rand <= 0.80:
            self.reduction_percentage = Decimal('0')
        elif rand <= 0.95:
            self.reduction_percentage = Decimal('10')
        else:
            self.reduction_percentage = Decimal('15')

        self.reduction_grattee = False
        self.reduction_revealed = False

    # -----------------------------
    # CALCUL FRAIS ANNEXE
    # -----------------------------
    def calculer_frais_annexe(self):
        if self.service_annexe and self.intitule_annexes:
            self.frais_annexe = self.PRIX_ANNEXE.get(
                self.intitule_annexes, Decimal('0')
            )
        else:
            self.frais_annexe = Decimal('0')
            self.intitule_annexes = None

    # -----------------------------
    # CALCUL MONTANT TOTAL
    # -----------------------------
    def calculer_montant_total(self):
        montant = (self.frais_impression or Decimal('0')) + (self.frais_annexe or Decimal('0'))

        if self.reduction_revealed and self.reduction_percentage > 0:
            self.montant_reduction = montant * (self.reduction_percentage / Decimal('100'))
            montant -= self.montant_reduction
        else:
            self.montant_reduction = Decimal('0')

        self.montant_total = montant

    # -----------------------------
    # REVELER REDUCTION
    # -----------------------------
    def reveler_reduction(self):
        if self.jeu_reduction and not self.reduction_revealed:
            self.reduction_revealed = True
            self.reduction_grattee = True
            self.calculer_montant_total()
            self.save()
            return True
        return False

    def __str__(self):
        return f"Paiement de {self.etudiant} - {self.montant_total} FCFA"


class HistoriquePaiement(models.Model):
    paiement = models.ForeignKey(Paiement, on_delete=models.CASCADE, related_name='historiques')
    date_historique = models.DateTimeField(auto_now_add=True)
    statut = models.BooleanField(default=False)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Historique de {self.paiement}"