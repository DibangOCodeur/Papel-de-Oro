from django import forms
from .models import Etudiant, Filiere, Collaborateur
from Dossiers.models import AnneeAcademique, Niveau, Dossier
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Collaborateur

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


# forms.py (ajouter)
from django.contrib.auth.forms import PasswordChangeForm

class ChangementMotDePasseForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        
        # Personnalisation des widgets
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ancien mot de passe',
            'required': True
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe',
            'required': True
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le nouveau mot de passe',
            'required': True
        })

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
            'matricule', 'filiere', 'niveau', 'annee_academique', 'parrain',
            'theme_memoire', 'support_pdf'  # support_pdf est un champ manuel
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'placeholder': 'Entrez le nom'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Entrez le prénom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Entrez l\'email'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Entrez le téléphone'}),
            'matricule': forms.TextInput(attrs={'placeholder': 'Entrez le matricule'}),
            'parrain': forms.Select(attrs={'placeholder': 'Qui est le parrain ?'}),
            'theme_memoire': forms.Textarea(attrs={
                'placeholder': 'Entrez le thème du mémoire',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(EtudiantForm, self).__init__(*args, **kwargs)

        self.fields['parrain'].required = False

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






class CollaborateurForm(forms.ModelForm):
    class Meta:
        model = Collaborateur
        fields = ['last_name', 'first_name', 'email', 'contact']
        widgets = {
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Entrez le nom',
                'class': 'form-input',
                'autocomplete': 'off'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Entrez le prénom',
                'class': 'form-input',
                'autocomplete': 'off'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Entrez l\'email',
                'class': 'form-input',
                'autocomplete': 'off'
            }),
            'contact': forms.TextInput(attrs={
                'placeholder': 'Entrez le téléphone',
                'class': 'form-input',
                'autocomplete': 'off'
            }),
        }
        labels = {
            'last_name': 'Nom',
            'first_name': 'Prénom',
            'email': 'Email',
            'contact': 'Téléphone',
        }

    def clean_email(self):
        """Vérifie que l'email est unique"""
        email = self.cleaned_data.get('email')
        if Collaborateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_contact(self):
        """Valide et formate le numéro de téléphone"""
        contact = self.cleaned_data.get('contact')
        if contact:
            # Supprimer les espaces et caractères spéciaux
            contact = ''.join(filter(str.isdigit, contact))
            
            # Vérifier la longueur
            if len(contact) < 8 or len(contact) > 15:
                raise forms.ValidationError(
                    "Le numéro de téléphone doit contenir entre 8 et 15 chiffres."
                )
        return contact

    def clean(self):
        """Vérifie que les mots de passe correspondent si fournis"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # Si l'utilisateur a fourni un mot de passe, vérifier la correspondance
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data

    def save(self, commit=True):
        """Sauvegarde le collaborateur avec le mot de passe par défaut"""
        collaborateur = super().save(commit=False)
        
        # Le mot de passe sera automatiquement défini à @papel@ dans le modèle
        # Pas besoin de le définir ici
        
        if commit:
            collaborateur.save()
        
        return collaborateur