from decimal import Decimal
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import LoginForm, EtudiantForm
from Paiements.forms import PaiementForm
from django.contrib import messages
from .models import Filiere, Utilisateur, Etudiant
from Dossiers.models import AnneeAcademique, Niveau, Dossier
from Paiements.models import Paiement
from django.http import HttpResponse
from django.template.loader import render_to_string
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from django.db import transaction 
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.db.models import Sum, Count, Q
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse_lazy
import pandas as pd
from django.views.generic import View
import json



# ============================================
# VIEWS DE CONNEXION
# ============================================
def connexion(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                email=email,
                password=password
            )
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Email ou mot de passe incorrect')
        
    return render(request, 'Utilisateurs/connexion.html')


def logout(request):
    logout(request)
    return redirect('connexion')




# ============================================
# VIEWS D'ACCUEIL
# ============================================
def dashboard(request):
    # Récupérer les 5 derniers étudiants inscrits (triés par date d'inscription décroissante)
    derniers_etudiants = Etudiant.objects.all().order_by('-date_inscription')[:5]
    
    paiement = Paiement.objects.all()
    total_etudiants = Etudiant.objects.count()
    filiere = Filiere.objects.all()
    annee_academique = AnneeAcademique.objects.all()
    niveau = Niveau.objects.all()
    
    montant_total = Paiement.objects.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
    nb_memoire = Dossier.objects.filter(support_pdf__isnull=False).count()
    nb_participants = Paiement.objects.filter(jeu_reduction=True).count()
    frais_annexe = Paiement.objects.aggregate(Sum('frais_annexe'))['frais_annexe__sum'] or 0
    commission = Paiement.objects.aggregate(Sum('commission'))['commission__sum'] or 0

    nb_gagnant = Paiement.objects.filter(
        reduction_revealed=True,
        reduction_percentage__gt=Decimal('0')
    ).count()

    montant_perdu = Paiement.objects.filter(
        reduction_revealed=True,
        reduction_percentage__gt=Decimal('0')
    ).aggregate(Sum('montant_reduction'))['montant_reduction__sum'] or 0

    # Formater les montants
    montant_total_formate = f"{montant_total:,.0f}".replace(",", " ")
    montant_annexe_formate = f"{frais_annexe:,.0f}".replace(",", " ")
    commission_formate = f"{commission:,.0f}".replace(",", " ")
    montant_perdu_formate = f"{montant_perdu:,.0f}".replace(",", " ")

    benefice = commission + frais_annexe
    benefice_formate = f"{benefice:,.0f}".replace(",", " ")

    total_tombola = 0

    # Condition de cumul du montant de la tombola
    for paiement in paiement :
        if paiement.jeu_reduction:
            total_tombola +=500

    total_tombola_formate = f"{total_tombola:,.0f}".replace(",", " ")
    
    context = {
        'etudiants': derniers_etudiants,  # Changé de 'etudiant' à 'etudiants'
        'total_etudiants': total_etudiants,
        'filiere': filiere,
        'annee_academique': annee_academique,
        'niveau': niveau,
        'montant_total': montant_total,
        'nb_memoire': nb_memoire,
        'montant_total_formate': montant_total_formate,
        'nb_participants': nb_participants,
        'commission': commission,
        'frais_annexe': frais_annexe,
        'montant_annexe_formate': montant_annexe_formate,
        'commission_formate': commission_formate,
        'benefice': benefice,
        'benefice_formate': benefice_formate,
        'paiement': paiement,
        'total_tombola':total_tombola,
        'total_tombola_formate': total_tombola_formate,
        'nb_gagnant': nb_gagnant,
        'montant_perdu_formate': montant_perdu_formate,
    }    

    return render(request, 'Utilisateurs/dashboard.html', context)


# ============================================
# VIEWS D'ENREGISTREMENT D'UN ETUDIANT
# ============================================

def ajouter_etudiant(request):
    # Récupérer les données pour les listes déroulantes
    filieres = Filiere.objects.all().order_by('nom')
    annee_academiques = AnneeAcademique.objects.all().order_by('annee_academique')
    niveaux = Niveau.objects.all().order_by('niveau')
    
    if request.method == 'POST':
        # Initialisation des formulaires
        etudiant_form = EtudiantForm(request.POST, request.FILES)
        paiement_form = PaiementForm(request.POST)

        # Débug, on affiches les données reçues        
        if etudiant_form.is_valid() and paiement_form.is_valid():
            try:
                with transaction.atomic():
                    # === ÉTAPE 1: Créer l'étudiant ===
                    etudiant = etudiant_form.save(commit=False)
                    etudiant.set_password('@elites@')
                    etudiant.role = 'etudiant'

                    # DEBUG: Afficher les fichiers reçus
                    print("Fichiers reçus:", request.FILES)
                    
                    #Sauvegarder l'étudiant
                    etudiant.save()
                    print(f"✅ Étudiant créé: {etudiant.matricule}")
                    
                    
                    # === ÉTAPE 2: Créer le paiement ===
                    paiement = paiement_form.save(commit=False, etudiant=etudiant)


                    # Calculer les frais annexes
                    PRIX_ANNEXE = {
                        'PAGE_DE_GARDE': Decimal('1000'),
                        'MISE_EN_FORME': Decimal('4000'),
                        'COMPLET': Decimal('5000'),
                    }
                    
                    # Calculer les frais annexes (si non déjà fait dans save())
                    service_annexe = paiement_form.cleaned_data.get('service_annexe', False)
                    intitule_annexes = paiement_form.cleaned_data.get('intitule_annexes')


                    if service_annexe and intitule_annexes:
                        frais_annexe = PRIX_ANNEXE.get(intitule_annexes, Decimal('0'))
                        paiement.frais_annexe = frais_annexe
                        paiement.intitule_annexe = intitule_annexes
                    else:
                        paiement.frais_annexe = Decimal('0')
                        paiement.intitule_annexe = None
                    
                    
                    # Calculer le montant total

                    frais_impression = paiement_form.cleaned_data.get('frais_impression', Decimal('0'))
                    commission = paiement_form.cleaned_data.get('commission', Decimal('0'))
                    montant_total = frais_impression + paiement.frais_annexe

                    # Comptabiliser la réduction
                    jeu_reduction = paiement_form.cleaned_data.get('jeu_reduction', False)
                    paiement.jeu_reduction = jeu_reduction
                    montant_reduction = Decimal('0')

                    if jeu_reduction:
                        montant_reduction += 500 
                    
                    # enregistrement du paiement

                    paiement.montant_total = montant_total
                    paiement.commission = commission
                    paiement.save()

                    
                    print(f"✅ Paiement enregistré: {paiement.id}")

                    support_pdf = None
                    if 'support_pdf' in request.FILES:
                        support_pdf = request.FILES['support_pdf']
                        print(f"✅ Support PDF reçu: {support_pdf.name}")


                    # === ÉTAPE 3: Vérifier/Mettre à jour le dossier ===
                    try:
                        dossier = Dossier.objects.get(etudiant=etudiant)
                        dossier.paiement = paiement

                        if support_pdf:
                            dossier.support_pdf = support_pdf
                            print(f"✅ Support PDF enregistré: {dossier.id}")

                        dossier.save()
                        print(f"✅ Dossier mis à jour avec paiement: {dossier.id}")

                    except Dossier.DoesNotExist:
                        # Le signal devrait avoir créé le dossier, mais au cas où...
                        dossier = Dossier.objects.create(
                            etudiant=etudiant,
                            paiement=paiement,
                            support_pdf=support_pdf,
                            statut=False,
                            livraison=False
                        )
                        print(f"✅ Dossier créé avec paiement: {dossier.id}")
                    
                    messages.success(request, 'Étudiant et paiement enregistrés avec succès !')


                    # === ÉTAPE 4: Gérer la redirection ===                    
                    return redirect('generer_reçu', paiement_id=paiement.id)

            except Exception as e:
                messages.error(request, f'Erreur lors de l\'enregistrement: {str(e)}')
                # DEBUG: Afficher l'erreur dans la console pour diagnostic
                print(f"ERREUR: {str(e)}")
                import traceback
                traceback.print_exc()

                # Re-préparer le contexte
                context = {
                    'form': etudiant_form,
                    'paiement_form': paiement_form,
                    'filieres': filieres,
                    'annee_academiques': annee_academiques,
                    'niveaux': niveaux,
                }
                return render(request, 'Utilisateurs/ajouter_etudiant.html', context)

        else:
            # DEBUG: Afficher les erreurs du formulaire
            print("❌ Erreurs du formulaire:", etudiant_form.errors)
            print("❌ Erreur du paiement:", paiement_form.errors)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')

            context = {
                'form': etudiant_form,
                'paiement_form': paiement_form,
                'filieres': filieres,
                'annee_academiques': annee_academiques,
                'niveaux': niveaux,
            }
            return render (request, 'Utilisateurs/ajouter_etudiant.html', context)
    
    else:
        etudiant_form = EtudiantForm()
        paiement_form = PaiementForm()

    
    # Préparer le contexte
    context = {
        'form': etudiant_form,
        'paiement_form': paiement_form,
        'filieres': filieres,
        'annee_academiques': annee_academiques,
        'niveaux': niveaux,
    }
    
    return render(request, 'Utilisateurs/ajouter_etudiant.html', context)



# ============================================
# VIEWS DE GENERATION DE RECU
# ============================================
def generer_reçu(request, paiement_id):
    """Générer le reçu de paiement avec QR code si réduction"""
    try:
        paiement = Paiement.objects.get(id=paiement_id)
    except Paiement.DoesNotExist:
        messages.error(request, 'Paiement non trouvé.')
        return redirect('ajouter_etudiant')
    
    # Calculer les montants
    montant_sans_reduction = paiement.frais_impression + paiement.frais_annexe
    
    tarif = {
        'memoire': paiement.frais_impression,
        'annexe': paiement.frais_annexe,
        'total_sans_reduction': montant_sans_reduction,
        'reduction_percentage': float(paiement.reduction_percentage),
        'montant_reduction': float(paiement.montant_reduction),
        'total_avec_reduction': paiement.montant_total
    }
    
    # Générer le QR code si jeu de réduction est activé
    qr_code_base64 = None
    if paiement.jeu_reduction:
        qr_data = {
            'type': 'reduction_universitaire',
            'reference': paiement.reference,
            'etudiant': {
                'nom': paiement.etudiant.last_name,
                'prenom': paiement.etudiant.first_name,
                'matricule': paiement.etudiant.matricule,
            },
            'montant_sans_reduction': str(montant_sans_reduction),
            'montant_final': str(paiement.montant_total),
            'reduction_percentage': str(paiement.reduction_percentage),
            'montant_reduction': str(paiement.montant_reduction),
            'date': paiement.date_paiement.strftime('%Y-%m-%d %H:%M:%S'),
            'reduction_grattee': paiement.reduction_grattee,
            'reduction_revealed': paiement.reduction_revealed,
            'url_grattage': f"{request.build_absolute_uri('/')}paiements/scanner/{paiement.reference}/",
        }
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(str(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"Erreur génération QR code: {e}")
            qr_code_base64 = None
    
    context = {
        'etudiant': paiement.etudiant,
        'paiement': paiement,
        'tarif': tarif,
        'reduction_percentage': paiement.reduction_percentage,
        'montant_reduction': paiement.montant_reduction,
        'qr_code_base64': qr_code_base64,
        'date_impression': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'montant_sans_reduction': montant_sans_reduction,
        'montant_final': paiement.montant_total,
        'reduction_grattee': paiement.reduction_grattee,
        'reduction_revealed': paiement.reduction_revealed,
    }
    
    html_string = render_to_string('Paiements/reçu_paiement.html', context)
    response = HttpResponse(html_string)
    return response




# ============================================
# VIEWS DE LISTE D'ETUDIANTS
# ============================================
class ListeEtudiantView(ListView):
    model = Etudiant
    template_name = 'Utilisateurs/liste_etudiant.html'
    context_object_name = 'etudiants'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_etudiants'] = Etudiant.objects.count()
        context['filieres'] = Filiere.objects.all()

        context['etudiants_recents'] = Etudiant.objects.order_by('-date_inscription')[:10]

        return context

    def get_queryset(self):
        queryset = Etudiant.objects.select_related(
            'filiere',
            'annee_academique',
            'niveau',
        ).all()   

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(matricule__icontains=search) |
                Q(filiere__nom__icontains=search)
            )
        
        filiere = self.request.GET.get('filiere')
        if filiere:
            queryset = queryset.filter(filiere__nom=filiere)

        
        niveau = self.request.GET.get('niveau')
        if niveau:
            queryset = queryset.filter(niveau_id=niveau)

        
        annee_academique = self.request.GET.get('annee_academique')
        if annee_academique:
            queryset = queryset.filter(annee_academique_id=annee_academique)


        paginate_by = self.request.GET.get('paginate_by')
        if paginate_by: 
            self.paginate_by = int(paginate_by)

        return queryset.order_by('-date_inscription')




# ============================================
# VIEWS DE DETAIL D'ETUDIANTS
# ============================================
class DetailEtudiantView(DetailView):
    model = Etudiant
    template_name = 'Utilisateurs/detail_etudiant.html'
    context_object_name = 'etudiant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        etudiant = self.get_object()

        # Récupérer le dossier associé
        try:
            dossier = Dossier.objects.get(etudiant=etudiant)
            context['dossier'] = dossier
        except Dossier.DoesNotExist:
            context['dossier'] = None
        
        # Récupérer les paiements
        paiements = Paiement.objects.filter(etudiant=etudiant).order_by('-date_paiement')
        context['paiements'] = paiements
        
        # Calculer les totaux
        context['total_montant'] = paiements.aggregate(total=Sum('montant_total'))['total'] or 0
        context['frais_impression'] = paiements.aggregate(total=Sum('frais_impression'))['total'] or 0
        context['commission'] = paiements.aggregate(total=Sum('commission'))['total'] or 0
        context['frais_annexe'] = paiements.aggregate(total=Sum('frais_annexe'))['total'] or 0
        
        # Créer un historique d'activités
        activites = []
        
        # Ajouter l'inscription
        activites.append({
            'type': 'inscription',
            'titre': 'Inscription',
            'description': f'Étudiant inscrit dans le système',
            'date': etudiant.date_inscription
        })
        
        # Ajouter les paiements
        for paiement in paiements:
            activites.append({
                'type': 'paiement',
                'titre': f'Paiement de {paiement.montant_total} FCFA',
                'description': f'Paiement pour impression de mémoire',
                'date': paiement.date_paiement
            })
        
        # Ajouter l'upload de fichier si existant
        if dossier and dossier.support_pdf:
            activites.append({
                'type': 'soumission',
                'titre': 'Soumission du mémoire',
                'description': f'Fichier PDF soumis: {dossier.support_pdf.name}',
                'date': dossier.date_modification
            })
        
        # Trier par date
        context['activites'] = activites

        return context



# ============================================
# VIEWS DE SUPPRESSION D'ETUDIANTS
# ============================================
class DeleteEtudiantiew(DeleteView):
    model = Etudiant
    template_name = 'Utilisateurs/delete_etudiant.html'
    success_url = reverse_lazy('liste_etudiant')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etudiant'] = self.get_object()
        return context
    


# ============================================
# VIEWS DE MISE A JOUR D'ETUDIANTS
# ============================================
class UpdateEtudiantView(UpdateView):
    model = Etudiant
    template_name = 'Utilisateurs/update_etudiant.html'
    fields = '__all__'
    success_url = reverse_lazy('liste_etudiant')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etudiant'] = self.get_object()
        context['filieres'] = Filiere.objects.all().order_by('nom')
        context['annee_academiques'] = AnneeAcademique.objects.all().order_by('annee_academique')
        context['niveaux'] = Niveau.objects.all().order_by('niveau')
        return context




class ExportExcelView(View):
    def get(self, request, *args, **kwargs):
        queryset = Etudiant.objects.select_related('filiere', 'niveau', 'annee_academique').all()
        
        # Créer un DataFrame pandas
        data = []
        for etudiant in queryset:
            data.append({
                'Matricule': etudiant.matricule,
                'Nom': etudiant.last_name,
                'Prénom': etudiant.first_name,
                'Email': etudiant.email,
                'Contact': etudiant.contact or '',
                'Filière': etudiant.filiere.nom,
                'Niveau': etudiant.niveau.niveau,
                'Thème mémoire': etudiant.theme_memoire,
                'Année académique': str(etudiant.annee_academique),
                'Date inscription': etudiant.date_inscription.strftime('%d/%m/%Y'),
            })
        
        df = pd.DataFrame(data)
        
        # Créer la réponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="liste_etudiants.xlsx"'
        
        # Écrire dans la réponse
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Étudiants', index=False)
        
        return response
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        student_ids = data.get('student_ids', [])
        
        queryset = Etudiant.objects.filter(id__in=student_ids).select_related(
            'filiere', 'niveau', 'annee_academique'
        )
        
        # Créer un DataFrame pandas
        data_list = []
        for etudiant in queryset:
            data_list.append({
                'Matricule': etudiant.matricule,
                'Nom': etudiant.last_name,
                'Prénom': etudiant.first_name,
                'Email': etudiant.email,
                'Contact': etudiant.contact or '',
                'Filière': etudiant.filiere.nom,
                'Niveau': etudiant.niveau.nom,
                'Thème mémoire': etudiant.theme_memoire,
                'Année académique': str(etudiant.annee_academique),
                'Date inscription': etudiant.date_inscription.strftime('%d/%m/%Y'),
            })
        
        df = pd.DataFrame(data_list)
        
        # Créer la réponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="etudiants_selectionnes.xlsx"'
        
        # Écrire dans la réponse
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Étudiants', index=False)
        
        return response





# Utilisateurs/views.py
def debug_dossiers(request):
    """Vue temporaire pour déboguer"""
    dossiers = Dossier.objects.all().select_related('etudiant', 'paiement')
    
    context = {
        'dossiers': dossiers,
        'total': dossiers.count(),
        'avec_paiement': dossiers.filter(paiement__isnull=False).count(),
        'sans_paiement': dossiers.filter(paiement__isnull=True).count(),
    }
    
    return render(request, 'Utilisateurs/debug_dossiers.html', context)