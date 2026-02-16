# Paiements/forms.py
from django import forms
from .models import Paiement
from decimal import Decimal


class PaiementForm(forms.ModelForm):
    # CORRECTION: Définition des choix pour intitule_annexes
    INTITULE_CHOICES = [
        ('', 'Sélectionnez un service'),
        ('PAGE_DE_GARDE', 'Page de garde (1,000 FCFA)'),
        ('MISE_EN_FORME', 'Mise en forme (4,000 FCFA)'),
        ('COMPLET', 'Complet (5,000 FCFA)'),
    ]
    
    # CORRECTION: Redéfinition des champs pour avoir le bon contrôle
    source = forms.ChoiceField(
        choices=Paiement.SOURCE_PAIEMENT,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    intitule_annexes = forms.ChoiceField(
        choices=INTITULE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # CORRECTION: Ajout de ces champs pour les calculs
    frais_annexe = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        initial=0,
        widget=forms.HiddenInput()
    )
    
    montant_jeu_reduction = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        initial=0,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Paiement
        fields = [
            'source', 'frais_impression', 'commission', 
            'service_annexe', 'intitule_annexes',
            'jeu_reduction', 'frais_annexe',
            'montant_total', 'montant_jeu_reduction'
        ]
        widgets = {
            'frais_impression': forms.NumberInput(attrs={
                'step': '100',  # Pas de 100 FCFA
                'min': '0',
                'class': 'form-control',
                'placeholder': 'Entrez les frais d\'impression'
            }),
            'commission': forms.NumberInput(attrs={
                'step': '100',
                'min': '0',
                'class': 'form-control',
                'placeholder': 'Entrez la commission'
            }),
            'service_annexe': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'jeu_reduction': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'montant_total': forms.HiddenInput(),  # Calculé automatiquement
        }
        labels = {
            'frais_impression': "Frais d'impression (FCFA)",
            'commission': "Commission (FCFA)",
            'source': "Moyen de paiement",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # CORRECTION: Initialisation correcte
        if not self.instance.pk:  # Nouvel enregistrement
            self.initial['frais_impression'] = 0
            self.initial['commission'] = 0
            self.initial['montant_total'] = 0
    
    def clean(self):
        cleaned_data = super().clean()
        
        # CORRECTION: Validation cohérente
        service_annexe = cleaned_data.get('service_annexe', False)
        intitule_annexes = cleaned_data.get('intitule_annexes')
        
        if service_annexe and not intitule_annexes:
            self.add_error('intitule_annexes', "Veuillez sélectionner un intitulé d'annexe")
        
        frais_impression = cleaned_data.get('frais_impression', 0)
        if frais_impression <= 0:
            self.add_error('frais_impression', "Les frais d'impression doivent être supérieurs à 0")
        
        return cleaned_data

    def save(self, commit=True, etudiant=None):
        # CORRECTION: Logique de sauvegarde corrigée
        instance = super().save(commit=False)
        
        if etudiant:
            instance.etudiant = etudiant
        
        # CORRECTION: Utilisation des données cleaned_data
        service_annexe = self.cleaned_data.get('service_annexe', False)
        intitule_annexes = self.cleaned_data.get('intitule_annexes')
        jeu_reduction = self.cleaned_data.get('jeu_reduction', False)
        
        # Prix des annexes
        PRIX_ANNEXE = {
            'PAGE_DE_GARDE': Decimal('1000'),
            'PAGINATION_TABLE_DE_MATIERE': Decimal('1500'),
            'COMPLET': Decimal('2500'),
        }
        
        # Calcul des frais annexes
        frais_annexe = Decimal('0')
        if service_annexe and intitule_annexes:
            frais_annexe = PRIX_ANNEXE.get(intitule_annexes, Decimal('0'))
            instance.intitule_annexes = intitule_annexes
        else:
            instance.intitule_annexes = None
        
        instance.frais_annexe = frais_annexe
        
        # Calcul du montant total
        frais_impression = self.cleaned_data.get('frais_impression', Decimal('0'))
        montant_total = frais_impression + frais_annexe
        
        # CORRECTION: Application de la réduction
        if jeu_reduction:
            # Réduction de 10% + 500 FCFA pour le jeu
            reduction = montant_total * Decimal('0.10')
            montant_total -= reduction
            instance.montant_jeu_reduction = Decimal('500')
        else:
            instance.montant_jeu_reduction = Decimal('0')
        
        # CORRECTION: Ajout de la commission au montant total
        commission = self.cleaned_data.get('commission', Decimal('0'))
        montant_total += commission  # La commission s'ajoute au total
        
        instance.montant_total = montant_total
        
        if commit:
            instance.save()
        
        return instance