from django import forms
from .models import Etudiant, Filiere
from Dossiers.models import AnneeAcademique, Niveau, Dossier

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse email',
            'id': 'email',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe',
            'id': 'password',
            'required': True
        })
    )


class EtudiantForm(forms.ModelForm):
    # CORRECTION: Changé à required=True pour correspondre au HTML
    support_pdf = forms.FileField(
        label="Support PDF du Dossier",
        required=True,  # Changé de False à True
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        })
    )

    class Meta:
        model = Etudiant
        # CORRECTION: Ajout de tous les champs nécessaires
        fields = [
            'last_name', 'first_name', 'email', 'contact', 
            'matricule', 'filiere', 'niveau', 'annee_academique',
            'theme_memoire', 'support_pdf'  # support_pdf est un champ manuel
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'placeholder': 'Entrez le nom'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Entrez le prénom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Entrez l\'email'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Entrez le téléphone'}),
            'matricule': forms.TextInput(attrs={'placeholder': 'Entrez le matricule'}),
            'theme_memoire': forms.Textarea(attrs={
                'placeholder': 'Entrez le thème du mémoire',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(EtudiantForm, self).__init__(*args, **kwargs)
        
        # Filtrage de la Queryset Filière
        self.fields['filiere'].queryset = Filiere.objects.all()
        self.fields['niveau'].queryset = Niveau.objects.all()
        self.fields['annee_academique'].queryset = AnneeAcademique.objects.all()

        # Ajout automatique des classes CSS
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
    
    def save(self, commit=True):
        # CORRECTION: Sauvegarde du fichier PDF dans le modèle Dossier
        etudiant = super().save(commit=False)
        
        if commit:
            # 1. Sauvegarder l'étudiant
            etudiant.save()
            
            # 2. Créer le dossier avec le fichier PDF
            support_pdf = self.cleaned_data.get('support_pdf')
            if support_pdf:
                Dossier.objects.create(
                    etudiant=etudiant,
                    support_pdf=support_pdf
                )
        return etudiant