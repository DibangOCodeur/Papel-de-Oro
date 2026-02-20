from decimal import Decimal
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib.auth import login

import Paiements
from .forms import LoginForm, EtudiantForm, CollaborateurForm
from Paiements.forms import PaiementForm
from django.contrib import messages
from .models import Filiere, Utilisateur, Etudiant, Collaborateur
from Dossiers.models import AnneeAcademique, Niveau, Dossier
from Paiements.models import Paiement
from django.http import HttpResponse
from django.template.loader import render_to_string
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from django.db import transaction 
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from django.db.models import Sum, Count, Q
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse_lazy
import pandas as pd
from django.views.generic import View
import json
from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q, Avg, F, DateField
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
from django.utils.safestring import mark_safe


# ============================================
# VIEWS DE CONNEXION
# ============================================
def connexion(request):
    # Si l'utilisateur est déjà connecté, rediriger selon son rôle
    if request.user.is_authenticated:
        if hasattr(request.user, 'collaborateur') or request.user.role == 'collaborateur':
            return redirect('dashboard_collaborateur')
        else:
            return redirect('dashboard')
    
    form = LoginForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            print(f"\n🔐 TENTATIVE DE CONNEXION")
            print(f"📧 Email: {email}")
            print(f"🔑 Mot de passe fourni: {password}")
            
            # Vérification manuelle
            try:
                user = Utilisateur.objects.get(email=email)
                print(f"✅ Utilisateur trouvé: {user.email}")
                print(f"👤 Rôle: {user.role}")
                print(f"🔐 Hash du mot de passe: {user.password[:50]}...")
                
                # Vérifier le mot de passe
                password_valid = user.check_password(password)
                print(f"✅ Mot de passe valide (check_password): {password_valid}")
                
                if password_valid:
                    # IMPORTANT: Récupérer le chemin du backend
                    from django.conf import settings
                    
                    # Utiliser le premier backend configuré
                    backend = settings.AUTHENTICATION_BACKENDS[0]
                    
                    # Connecter l'utilisateur avec le backend spécifié
                    login(request, user, backend=backend)
                    print(f"✅ Connexion réussie pour {email} avec backend {backend}")
                    
                    # Redirection selon le rôle
                    if user.role == 'collaborateur':
                        if password == '@papel@':
                            messages.warning(request, 'Veuillez changer votre mot de passe par défaut.')
                            return redirect('changer_mot_de_passe')
                        return redirect('dashboard_collaborateur')
                    else:
                        return redirect('dashboard')
                else:
                    print(f"❌ Mot de passe invalide pour {email}")
                    messages.error(request, 'Email ou mot de passe incorrect')
                    
            except Utilisateur.DoesNotExist:
                print(f"❌ Aucun utilisateur avec l'email {email}")
                messages.error(request, 'Email ou mot de passe incorrect')
            except Exception as e:
                print(f"❌ Erreur: {e}")
                messages.error(request, 'Erreur lors de la connexion')
        
    return render(request, 'Utilisateurs/connexion.html', {'form': form})


def deconnexion(request):
    auth_logout(request)
    return redirect('connexion')

# ===========================================
# VIEWS DE CHANGEMENT DE MOT DE PASSE
# ===========================================
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import ChangementMotDePasseForm

@login_required
def changer_mot_de_passe(request):
    if request.method == 'POST':
        form = ChangementMotDePasseForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur
            messages.success(request, 'Votre mot de passe a été changé avec succès !')
            
            # Rediriger vers le dashboard approprié
            if hasattr(request.user, 'collaborateur'):
                return redirect('dashboard_collaborateur')
            return redirect('dashboard')
    else:
        form = ChangementMotDePasseForm(request.user)
    
    return render(request, 'Utilisateurs/changer_mot_de_passe.html', {
        'form': form,
        'is_collaborateur': hasattr(request.user, 'collaborateur')
    })


# ============================================
# VIEWS D'ACCUEIL
# ============================================
def dashboard(request):
    # Récupérer les 5 derniers étudiants inscrits (triés par date d'inscription décroissante)
    derniers_etudiants = Etudiant.objects.all().order_by('-date_inscription')[:5]
    derniers_participants = Paiement.objects.filter(jeu_reduction=True).order_by('-date_paiement')[:5]
    
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
        'derniers_participants': derniers_participants,
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
# VIEWS DE DASHBOARD COLLABORATEUR
# ============================================

def tableau_de_bord_collaborateur(request):
    # Vérifier si l'utilisateur est authentifié
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Récupérer le collaborateur
    try:
        collaborateur = request.user.collaborateur
    except:
        return redirect('login')
    
    # Date actuelle
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    
    # ========== STATISTIQUES PRINCIPALES ==========
    # Statistiques de base
    nb_etudiant = Etudiant.objects.filter(parrain=collaborateur).count()
    
    # Nouveaux étudiants ce mois
    nb_nouveaux_etudiants = Etudiant.objects.filter(
        parrain=collaborateur,
        date_inscription__gte=first_day_month
    ).count()
    
    # Mémoires traités (tous)
    nb_memoire_traiter = Dossier.objects.filter(
        etudiant__parrain=collaborateur
    ).count()
    
    # Mémoires en cours
    nb_memoire_encours = Dossier.objects.filter(
        etudiant__parrain=collaborateur,
        statut=False,
        livraison=False
    ).count()
    
    # Mémoires terminés (imprimés)
    nb_memoire_termine = Dossier.objects.filter(
        etudiant__parrain=collaborateur,
        statut=True
    ).count()
    
    # Mémoires livrés
    nb_memoire_livre = Dossier.objects.filter(
        etudiant__parrain=collaborateur,
        livraison=True
    ).count()
    
    # Paiements
    mon_solde = Paiement.objects.filter(
        etudiant__parrain=collaborateur
    ).aggregate(
        Sum('commission_parrain')
    )['commission_parrain__sum'] or 0
    
    # Paiements du mois
    paiements_mois = Paiement.objects.filter(
        etudiant__parrain=collaborateur,
        date_paiement__gte=first_day_month
    ).aggregate(
        total=Sum('montant_total'),
        commission=Sum('commission_parrain')
    )
    
    # Dernier paiement
    dernier_paiement = Paiement.objects.filter(
        etudiant__parrain=collaborateur
    ).order_by('-date_paiement').first()
    
    # ========== STATISTIQUES PAR FILIERE ==========
    stats_par_filiere = []
    filieres = Filiere.objects.all()
    
    for filiere in filieres:
        count = Etudiant.objects.filter(
            parrain=collaborateur,
            filiere=filiere
        ).count()
        
        if count > 0:
            paiements_filiere = Paiement.objects.filter(
                etudiant__parrain=collaborateur,
                etudiant__filiere=filiere
            ).aggregate(
                total=Sum('montant_total'),
                commission=Sum('commission_parrain')
            )
            
            stats_par_filiere.append({
                'nom': filiere.nom[:30] + '...' if len(filiere.nom) > 30 else filiere.nom,
                'abreviation': filiere.abreviation,
                'nb_etudiants': count,
                'total_paiements': paiements_filiere['total'] or 0,
                'commission': paiements_filiere['commission'] or 0
            })
    
    # Trier par nombre d'étudiants
    stats_par_filiere.sort(key=lambda x: x['nb_etudiants'], reverse=True)
    
    # ========== ÉVOLUTION MENSUELLE (6 derniers mois) ==========
    evolution_mensuelle = []
    labels_mois = []
    
    for i in range(5, -1, -1):
        mois = today - timedelta(days=30 * i)
        mois_debut = mois.replace(day=1)
        if mois.month == 12:
            mois_fin = mois.replace(day=31)
        else:
            mois_fin = (mois + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Étudiants inscrits ce mois
        etudiants_mois = Etudiant.objects.filter(
            parrain=collaborateur,
            date_inscription__range=[mois_debut, mois_fin]
        ).count()
        
        # Mémoires traités ce mois
        memoires_mois = Dossier.objects.filter(
            etudiant__parrain=collaborateur,
            date_creation__range=[mois_debut, mois_fin]
        ).count()
        
        # Paiements ce mois
        paiements_mois_data = Paiement.objects.filter(
            etudiant__parrain=collaborateur,
            date_paiement__range=[mois_debut, mois_fin]
        ).aggregate(
            total=Sum('montant_total'),
            commission=Sum('commission_parrain')
        )
        
        evolution_mensuelle.append({
            'mois': mois_debut.strftime('%B %Y'),
            'etudiants': etudiants_mois,
            'memoires': memoires_mois,
            'paiements': float(paiements_mois_data['total'] or 0),
            'commission': float(paiements_mois_data['commission'] or 0)
        })
        
        labels_mois.append(mois_debut.strftime('%b'))
    
    # ========== TOP ÉTUDIANTS (par montant de paiement) ==========
    top_etudiants = Etudiant.objects.filter(
        parrain=collaborateur
    ).annotate(
        total_paiements=Sum('paiements__montant_total'),
        total_commission=Sum('paiements__commission_parrain')
    ).order_by('-total_paiements')[:5]
    
    top_etudiants_data = []
    for etudiant in top_etudiants:
        dernier_dossier = Dossier.objects.filter(
            etudiant=etudiant
        ).order_by('-date_creation').first()
        
        top_etudiants_data.append({
            'id': etudiant.id,
            'nom': f"{etudiant.first_name} {etudiant.last_name}",
            'initiales': f"{etudiant.first_name[0] if etudiant.first_name else ''}{etudiant.last_name[0] if etudiant.last_name else ''}",
            'filiere': etudiant.filiere.abreviation if etudiant.filiere else 'N/A',
            'total_paiements': float(etudiant.total_paiements or 0),
            'total_commission': float(etudiant.total_commission or 0),
            'statut_dossier': 'Terminé' if dernier_dossier and dernier_dossier.statut else 'En cours' if dernier_dossier else 'Aucun'
        })
    
    # ========== DOSSIERS RÉCENTS ==========
    dossiers_recents = Dossier.objects.filter(
        etudiant__parrain=collaborateur
    ).select_related('etudiant').order_by('-date_creation')[:7]
    
    dossiers_recents_data = []
    for dossier in dossiers_recents:
        dossiers_recents_data.append({
            'etudiant': f"{dossier.etudiant.first_name} {dossier.etudiant.last_name}",
            'initiales': f"{dossier.etudiant.first_name[0] if dossier.etudiant.first_name else ''}{dossier.etudiant.last_name[0] if dossier.etudiant.last_name else ''}",
            'date': dossier.date_creation.strftime('%d/%m/%Y'),
            'statut': 'Terminé' if dossier.statut else 'En attente' if not dossier.livraison else 'Livré',
            'livraison': dossier.livraison
        })
    
    # ========== ACTIVITÉS RÉCENTES ==========
    activites = []
    
    # Derniers paiements
    derniers_paiements = Paiement.objects.filter(
        etudiant__parrain=collaborateur
    ).select_related('etudiant').order_by('-date_paiement')[:3]
    
    for paiement in derniers_paiements:
        if paiement.date_paiement:
            # Convertir le datetime en date pour la soustraction
            if hasattr(paiement.date_paiement, 'date'):
                date_paiement = paiement.date_paiement.date()
            else:
                date_paiement = paiement.date_paiement
            
            jours_diff = (today - date_paiement).days
            if jours_diff == 0:
                temps = "Aujourd'hui"
            elif jours_diff == 1:
                temps = "Hier"
            else:
                temps = f"Il y a {jours_diff} jours"
        else:
            temps = "Date inconnue"
            
        activites.append({
            'type': 'Commission',
            'icon': 'fa-credit-card',
            'couleur': 'f39c12',
            'message': mark_safe(
                f'Commission de <span class="highlight-montant">{paiement.commission_parrain:,.0f} FCFA</span> '
                f'sur le paiement de <span class="highlight-nom">{paiement.etudiant.first_name} {paiement.etudiant.last_name}</span>'
            ),
            'temps': temps
        })
    
    # Derniers dossiers
    for dossier in dossiers_recents[:3]:
        if dossier.date_creation:
            # Convertir le datetime en date si nécessaire
            if hasattr(dossier.date_creation, 'date'):
                date_creation = dossier.date_creation.date()
            else:
                date_creation = dossier.date_creation
            
            jours_diff = (today - date_creation).days
            if jours_diff == 0:
                temps = "Aujourd'hui"
            elif jours_diff == 1:
                temps = "Hier"
            else:
                temps = f"Il y a {jours_diff} jours"
        else:
            temps = "Date inconnue"
            
        statut_msg = "terminé" if dossier.statut else "créé"
        activites.append({
            'type': 'dossier',
            'icon': 'fa-file-pdf',
            'couleur': '3498db',
            'message': f"Dossier {statut_msg} pour {dossier.etudiant.first_name} {dossier.etudiant.last_name}",
            'temps': temps
        })
    
    # Derniers étudiants inscrits
    derniers_etudiants = Etudiant.objects.filter(
        parrain=collaborateur
    ).order_by('-date_inscription')[:3]
    
    for etudiant in derniers_etudiants:
        if etudiant.date_inscription:
            # Convertir le datetime en date si nécessaire
            if hasattr(etudiant.date_inscription, 'date'):
                date_inscription = etudiant.date_inscription.date()
            else:
                date_inscription = etudiant.date_inscription
            
            jours_diff = (today - date_inscription).days
            if jours_diff == 0:
                temps = "Aujourd'hui"
            elif jours_diff == 1:
                temps = "Hier"
            else:
                temps = f"Il y a {jours_diff} jours"
        else:
            temps = "Date inconnue"
            
        activites.append({
            'type': 'inscription',
            'icon': 'fa-user-plus',
            'couleur': '27ae60',
            'message': mark_safe(
                f"Nouvel étudiant inscrit : <span class=\"highlight-nom\">{etudiant.first_name} {etudiant.last_name}</span>"
            ),
            'temps': temps
        })
    
    # Trier les activités par date (les plus récentes d'abord)
    activites.sort(key=lambda x: (
        0 if "Aujourd'hui" in x['temps'] else 
        1 if "Hier" in x['temps'] else 
        2
    ))
    
    # ========== STATISTIQUES DE PERFORMANCE ==========
    # Taux de conversion (étudiants avec dossier)
    etudiants_avec_dossier = Etudiant.objects.filter(
        parrain=collaborateur,
        dossier__isnull=False
    ).distinct().count()
    
    taux_conversion = (etudiants_avec_dossier / nb_etudiant * 100) if nb_etudiant > 0 else 0
    
    # Commission moyenne par étudiant
    commission_moyenne = mon_solde / nb_etudiant if nb_etudiant > 0 else 0
    
    # ========== TÂCHES PRIORITAIRES ==========
    taches_prioritaires = []
    
    # Dossiers en attente depuis plus de 7 jours
    date_limite = today - timedelta(days=7)
    dossiers_en_attente = Dossier.objects.filter(
        etudiant__parrain=collaborateur,
        statut=False,
        livraison=False,
        date_creation__lte=date_limite
    )[:3]
    
    for dossier in dossiers_en_attente:
        if dossier.date_creation:
            # Convertir le datetime en date si nécessaire
            if hasattr(dossier.date_creation, 'date'):
                date_creation = dossier.date_creation.date()
            else:
                date_creation = dossier.date_creation
            
            jours_retard = (today - date_creation).days
            taches_prioritaires.append({
                'titre': f"Dossier en attente - {dossier.etudiant.first_name} {dossier.etudiant.last_name}",
                'echeance': f"En retard de {jours_retard} jours",
                'type': 'warning',
                'urgent': True
            })
    
    # ========== PRÉPARATION DES DONNÉES POUR LES GRAPHIQUES ==========
    chart_data = {
        'evolution': {
            'labels': labels_mois,
            'etudiants': [item['etudiants'] for item in evolution_mensuelle],
            'memoires': [item['memoires'] for item in evolution_mensuelle],
            'paiements': [item['paiements'] for item in evolution_mensuelle],
            'commissions': [item['commission'] for item in evolution_mensuelle]
        },
        'filiere': {
            'labels': [item['abreviation'] or 'N/A' for item in stats_par_filiere[:6]],
            'data': [item['nb_etudiants'] for item in stats_par_filiere[:6]],
            'commissions': [item['commission'] for item in stats_par_filiere[:6]]
        }
    }
    
    # Convertir en JSON pour utilisation dans le template
    chart_data_json = json.dumps(chart_data, cls=DjangoJSONEncoder)
    
    # ========== CONTEXTE POUR LE TEMPLATE ==========
    context = {
        # Informations utilisateur
        'user': request.user,
        'collaborateur': collaborateur,
        
        # Statistiques principales
        'mon_solde': mon_solde,
        'nb_etudiant': nb_etudiant,
        'nb_nouveaux_etudiants': nb_nouveaux_etudiants,
        'nb_memoire_traiter': nb_memoire_traiter,
        'nb_memoire_encours': nb_memoire_encours,
        'nb_memoire_termine': nb_memoire_termine,
        'nb_memoire_livre': nb_memoire_livre,
        
        # Paiements
        'paiements_mois': paiements_mois,
        'dernier_paiement': dernier_paiement,
        
        # Statistiques détaillées
        'stats_par_filiere': stats_par_filiere,
        'evolution_mensuelle': evolution_mensuelle,
        'top_etudiants': top_etudiants_data,
        'dossiers_recents': dossiers_recents_data,
        'activites': activites[:8],  # Limiter à 8 activités
        
        # Métriques de performance
        'taux_conversion': round(taux_conversion, 1),
        'commission_moyenne': round(commission_moyenne),
        'taches_prioritaires': taches_prioritaires,
        
        # Données pour les graphiques
        'chart_data': chart_data_json,
        
        # Dates
        'date_aujourdhui': today.strftime('%d %B %Y'),
        'mois_courant': today.strftime('%B %Y'),
    }
    
    return render(request, 'Collaborateurs/dashboard_collaborateur.html', context)


    
# ============================================
# VIEWS D'ENREGISTREMENT D'UN ETUDIANT
# ============================================

def ajouter_etudiant(request):
    # Récupérer les données pour les listes déroulantes
    filieres = Filiere.objects.all().order_by('nom')
    annee_academiques = AnneeAcademique.objects.all().order_by('annee_academique')
    niveaux = Niveau.objects.all().order_by('niveau')
    parrains = Collaborateur.objects.all()  # ou avec un filtre spécifique

    
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
                    'parrains': parrains,
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
                'parrains': parrains,
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
        'parrains': parrains,
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
        context['total_parraines'] = Etudiant.objects.filter(parrain__isnull=False).count()
        context['revenu'] = Paiement.objects.filter(commission__gt=0).aggregate(total=Sum('commission'))['total'] or 0
        context['etudiants_tombola'] = Paiement.objects.filter(jeu_reduction=True).count()

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





# ==========================================
# LISTE DES FILLEULS
# ===========================================
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse

def liste_filleuls(request):
    # Vérifier l'authentification
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        collaborateur = request.user.collaborateur
    except:
        return redirect('login')
    
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    
    # Récupérer tous les filleuls du collaborateur
    filleuls_query = Etudiant.objects.filter(
        parrain=collaborateur
    ).select_related('filiere', 'niveau', 'annee_academique').order_by('-date_inscription')
    
    # Statistiques
    total_filleuls = filleuls_query.count()
    
    # Filleuls actifs (avec dossier en cours)
    actifs = Dossier.objects.filter(
        etudiant__parrain=collaborateur,
        statut=False
    ).values('etudiant').distinct().count()
    
    # Nouveaux ce mois
    nouveaux_mois = filleuls_query.filter(
        date_inscription__gte=first_day_month
    ).count()
    
    # Commissions totales (convertir en float pour JSON)
    commission_total = float(Paiement.objects.filter(
        etudiant__parrain=collaborateur
    ).aggregate(Sum('commission_parrain'))['commission_parrain__sum'] or 0)
    
    # Mémoires en cours (pour le badge)
    memoires_encours = Dossier.objects.filter(
        etudiant__parrain=collaborateur,
        statut=False,
        livraison=False
    ).count()
    
    # Pagination
    paginator = Paginator(filleuls_query, 10)
    page_number = request.GET.get('page', 1)
    filleuls_page = paginator.get_page(page_number)
    
    # Préparer les données des filleuls (avec conversion Decimal -> float)
    filleuls_data = []
    for etudiant in filleuls_page:
        # Dernier dossier
        dernier_dossier = Dossier.objects.filter(
            etudiant=etudiant
        ).order_by('-date_creation').first()
        
        # Paiements (convertir en float)
        paiements = Paiement.objects.filter(etudiant=etudiant)
        total_paye = float(paiements.aggregate(Sum('montant_total'))['montant_total__sum'] or 0)
        commission = float(paiements.aggregate(Sum('commission_parrain'))['commission_parrain__sum'] or 0)
        
        # Progression du dossier
        progression = 0
        if dernier_dossier:
            if dernier_dossier.livraison:
                progression = 100
            elif dernier_dossier.statut:
                progression = 75
            else:
                progression = 25
        
        # Statut du dossier
        if dernier_dossier:
            if dernier_dossier.livraison:
                statut = "Livré"
            elif dernier_dossier.statut:
                statut = "Terminé"
            else:
                statut = "En cours"
        else:
            statut = "Aucun"
        
        filleuls_data.append({
            'id': etudiant.id,
            'nom': f"{etudiant.first_name} {etudiant.last_name}",
            'initiales': f"{etudiant.first_name[0] if etudiant.first_name else ''}{etudiant.last_name[0] if etudiant.last_name else ''}",
            'filiere': etudiant.filiere.abreviation if etudiant.filiere else 'N/A',
            'matricule': etudiant.matricule or 'N/A',
            'date_inscription': etudiant.date_inscription.strftime('%d/%m/%Y'),
            'niveau': etudiant.niveau.niveau if etudiant.niveau else 'N/A',
            'theme': etudiant.theme_memoire,
            'total_paye': total_paye,
            'commission': commission,
            'progression': progression,
            'statut_dossier': statut,
            'actif': statut == "En cours",
            'etat_dossier': 5 if statut == "Livré" else 4 if statut == "Terminé" else 2 if statut == "En cours" else 0
        })
    
    # Statistiques pour le template (avec conversion float)
    stats = {
        'total': total_filleuls,
        'actifs': actifs,
        'nouveaux_mois': nouveaux_mois,
        'commission_total': commission_total,
        'memoires_encours': memoires_encours
    }
    
    # Données pour le template de base
    user_data = {
        'nbEtudiants': total_filleuls,
        'nbMemoiresEncours': memoires_encours,
        'nbNouveauxEtudiants': nouveaux_mois,
    }
    
    # URLs pour le template de base
    app_urls = {
        'accueil': reverse('dashboard_collaborateur'),
        'listeFilleuls': reverse('liste_filleuls'),
        'rechercheEtudiant': '#',
        'dossiersEncours': '#',
        'nouveauxInscrits': '#',
        'memoiresAImprimer': '#',
        'memoiresAttente': '#',
        'memoiresTermines': '#',
        'memoiresLivres': '#',
        'paiementsEncaisser': '#',
        'paiementsJour': '#',
        'paiementsRecus': '#',
        'paiementsHistorique': '#',
        'statistiques': '#',
        'fileImpression': '#',
        'parametres': '#',
        'aide': '#',
    }
    
    context = {
        'filleuls': filleuls_page,
        'filleuls_data': filleuls_data,
        'stats': stats,
        'stats_json': json.dumps(stats, cls=DjangoJSONEncoder),
        'collaborateur': collaborateur,
        'user_data': json.dumps(user_data, cls=DjangoJSONEncoder),
        'app_urls': json.dumps(app_urls, cls=DjangoJSONEncoder),
        'pagination': filleuls_page.has_other_pages(),
    }
    
    return render(request, 'Collaborateurs/liste_filleul.html', context)





from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum, Count, Q
from django.urls import reverse
import json
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal

from Dossiers.models import Dossier
from Utilisateurs.models import Etudiant, Collaborateur
from Paiements.models import Paiement

def liste_memoires_imprimes(request):
    """Affiche la liste des mémoires imprimés pour le collaborateur connecté"""
    
    # Vérifier l'authentification
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        collaborateur = request.user.collaborateur
    except:
        return redirect('login')
    
    # Date actuelle
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    
    # Récupérer les dossiers des étudiants du collaborateur
    # Un mémoire est considéré comme "imprimé" quand il a un support_pdf
    memoires_query = Dossier.objects.filter(
        etudiant__parrain=collaborateur,
        support_pdf__isnull=False  # Le PDF existe (mémoire imprimé)
    ).select_related(
        'etudiant',
        'etudiant__filiere',
        'etudiant__niveau',
        'paiement'
    ).order_by('-date_modification')
    
    # Statistiques
    stats = {
        'total_imprimes': memoires_query.count(),
        'en_attente_livraison': memoires_query.filter(livraison=False).count(),
        'livres_mois': memoires_query.filter(
            date_livraison__gte=first_day_month,
            livraison=True
        ).count(),
        'ca_total': float(Paiement.objects.filter(
            etudiant__parrain=collaborateur
        ).aggregate(Sum('commission_parrain'))['commission_parrain__sum'] or 0),
    }
   
    # Récupérer les paramètres de filtre
    statut_filter = request.GET.get('statut', 'tous')
    search_query = request.GET.get('search', '')
    
    # Appliquer les filtres
    if statut_filter == 'attente':
        memoires_query = memoires_query.filter(livraison=False)
    elif statut_filter == 'livres':
        memoires_query = memoires_query.filter(livraison=True)
    
    if search_query:
        memoires_query = memoires_query.filter(
            Q(etudiant__first_name__icontains=search_query) |
            Q(etudiant__last_name__icontains=search_query) |
            Q(etudiant__theme_memoire__icontains=search_query) |
            Q(etudiant__filiere__nom__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(memoires_query, 10)
    page_number = request.GET.get('page', 1)
    memoires_page = paginator.get_page(page_number)
    
    # Préparer les données pour le template
    memoires_data = []
    for dossier in memoires_page:
        etudiant = dossier.etudiant
        
        # Récupérer le paiement associé
        paiement = dossier.paiement
        
        # Déterminer le nombre de pages (à adapter selon votre logique)
        # Si vous avez un champ pour le nombre de pages, utilisez-le
        nombre_pages = getattr(dossier, 'nombre_pages', None)
        
        memoires_data.append({
            'id': dossier.id,
            'etudiant_nom': f"{etudiant.first_name} {etudiant.last_name}",
            'etudiant_id': etudiant.id,
            'filiere': etudiant.filiere.abreviation if etudiant.filiere else 'N/A',
            'niveau': etudiant.niveau.niveau if etudiant.niveau else 'N/A',
            'matricule': etudiant.matricule or 'N/A',
            'theme': etudiant.theme_memoire or 'Sans thème',
            'date_impression': dossier.date_modification.strftime('%d/%m/%Y'),
            'date_livraison': dossier.date_livraison.strftime('%d/%m/%Y') if dossier.date_livraison else None,
            'frais_impression': float(paiement.frais_impression) if paiement else 0,
            'commission': float(paiement.commission_parrain) if paiement and paiement.commission_parrain else 0,
            'montant_total': float(paiement.montant_total) if paiement else 0,
            'livre': dossier.livraison,
            'nombre_pages': nombre_pages,
            'pdf_url': dossier.support_pdf.url if dossier.support_pdf else None,
        })
    
    # Données pour les URLs
    app_urls = {
        'details_memoire': reverse('details_memoire', args=[0]),
        'telecharger_pdf': reverse('telecharger_pdf', args=[0]),
        'marquer_livre': reverse('marquer_livre', args=[0]),
        'memoires_encours': reverse('memoires_encours'),
        'accueil': reverse('dashboard_collaborateur'),
        'listeFilleuls': reverse('liste_filleuls'),
        'rechercheEtudiant': '#',
        'nouveauxInscrits': '#',
        'memoiresAttente': '#',
        'memoiresTermines': '#',
        'memoiresLivres': '#',
        'paiementsEncaisser': '#',
        'paiementsJour': '#',
        'paiementsHistorique': '#',
        'statistiques': '#',
        'fileImpression': '#',
        'parametres': '#',
        'aide': '#',
    }
    
    # Données utilisateur pour les badges
    user_data = {
        'nbEtudiants': collaborateur.nombre_etudiant,
        'nbMemoiresEncours': stats['en_attente_livraison'],
        'nbNouveauxEtudiants': Etudiant.objects.filter(
            parrain=collaborateur,
            date_inscription__gte=first_day_month
        ).count(),
    }
    
    context = {
        'memoires': memoires_page,
        'memoires_data': memoires_data,
        'stats': stats,
        'stats_json': json.dumps(stats, cls=DjangoJSONEncoder),
        'user_data': json.dumps(user_data, cls=DjangoJSONEncoder),
        'app_urls': json.dumps(app_urls, cls=DjangoJSONEncoder),
        'pagination': memoires_page.has_other_pages(),
        'filtre_actif': statut_filter,
        'recherche': search_query,
        'collaborateur': collaborateur,
    }
    
    return render(request, 'Collaborateurs/liste_memoires_imprimes.html', context)

def details_memoire(request, dossier_id):
    """Affiche les détails d'un mémoire spécifique"""
    dossier = get_object_or_404(Dossier, id=dossier_id, etudiant__parrain=request.user.collaborateur)
    
    # Logique pour afficher les détails
    return render(request, 'Collaborateurs/details_memoire.html', {'dossier': dossier})

def telecharger_pdf(request, dossier_id):
    """Télécharge le PDF d'un mémoire"""
    dossier = get_object_or_404(Dossier, id=dossier_id, etudiant__parrain=request.user.collaborateur)
    
    if dossier.support_pdf:
        # Rediriger vers l'URL du fichier ou servir le fichier
        return redirect(dossier.support_pdf.url)
    else:
        # Gérer l'erreur
        return redirect('liste_memoires_imprimes')

def marquer_livre(request, dossier_id):
    """Marque un mémoire comme livré"""
    dossier = get_object_or_404(Dossier, id=dossier_id, etudiant__parrain=request.user.collaborateur)
    
    if request.method == 'POST':
        dossier.livraison = True
        dossier.date_livraison = timezone.now()
        dossier.save()
        
        # Message de succès (à adapter avec votre système de messages)
        # messages.success(request, 'Mémoire marqué comme livré avec succès')
    
    return redirect('liste_memoires_imprimes')

def memoires_encours(request):
    """Affiche les mémoires en cours (non imprimés)"""
    # Logique similaire à liste_memoires_imprimes mais avec support_pdf__isnull=True
    pass






# views.py
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Collaborateur
from .forms import CollaborateurForm

class CollaborateurCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer un nouveau collaborateur
    """
    model = Collaborateur
    template_name = "Collaborateurs/inscription.html"
    form_class = CollaborateurForm
    
    def get_success_url(self):
        """
        Définit l'URL de redirection après succès
        """
        return reverse_lazy('recu_collaborateur', kwargs={'collaborateur_id': self.object.id})
    
    def form_valid(self, form):
        """
        Si le formulaire est valide, sauvegarde et affiche un message de succès
        """
        try:
            # Sauvegarder le collaborateur
            self.object = form.save()
            
            # Message de succès avec les informations générées
            messages.success(
                self.request, 
                f"✅ Inscription réussie !\n\n"
                f"📋 Matricule : {self.object.matricule}\n"
                f"🔑 Code parrainage : {self.object.code_parainage}\n"
                f"🔐 Mot de passe par défaut : {Collaborateur.DEFAULT_PASSWORD}\n\n"
                f"Veuillez communiquer ces informations au collaborateur."
            )
            
            # Message d'information pour la connexion
            messages.info(
                self.request,
                "ℹ️ Le collaborateur peut maintenant se connecter avec son email et le mot de passe par défaut."
            )
            
            # Rediriger vers la page de reçu
            return redirect('recu_collaborateur', collaborateur_id=self.object.id)
            
        except Exception as e:
            # En cas d'erreur inattendue
            messages.error(
                self.request, 
                f"❌ Une erreur est survenue lors de l'inscription : {str(e)}"
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """
        Si le formulaire est invalide, affiche les erreurs
        """
        # Afficher les erreurs du formulaire
        for field, errors in form.errors.items():
            field_name = form.fields[field].label if field in form.fields else field
            for error in errors:
                messages.error(
                    self.request, 
                    f"❌ {field_name}: {error}"
                )
        
        # Message général d'erreur
        messages.error(
            self.request,
            "⚠️ Veuillez corriger les erreurs ci-dessous avant de soumettre à nouveau."
        )
        
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """
        Ajoute des données supplémentaires au contexte
        """
        context = super().get_context_data(**kwargs)
        
        # Statistiques pour le panneau latéral
        context.update({
            'page_title': "Inscription Collaborateur",
            'submit_text': "Créer le compte",
            'default_password': Collaborateur.DEFAULT_PASSWORD,
            'total_collaborateurs': Collaborateur.objects.filter(is_active=True).count(),
            'total_etudiants': 0,  # À adapter selon votre modèle Étudiant
            'total_parrainages': 0,  # À adapter selon votre logique de parrainage
            'today': timezone.now(),  # Ajoutez: from django.utils import timezone
        })
        
        return context
    
    def get_initial(self):
        """
        Initialise les valeurs par défaut du formulaire
        """
        initial = super().get_initial()
        # Vous pouvez ajouter des valeurs initiales ici si nécessaire
        return initial
    
    def dispatch(self, request, *args, **kwargs):
        """
        Vérifie les permissions avant d'exécuter la vue
        """
        # Vérifier si l'utilisateur a la permission de créer un collaborateur
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, "Vous n'avez pas la permission de créer des collaborateurs.")
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)




# views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.conf import settings
import qrcode
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import os

def recu_collaborateur(request, collaborateur_id):
    """
    Vue pour afficher le reçu d'inscription d'un collaborateur
    """
    collaborateur = get_object_or_404(Collaborateur, id=collaborateur_id)
    
    # Générer l'URL de connexion avec l'email du collaborateur pour pré-remplissage
    login_url = request.build_absolute_uri('/')
    
    # Créer une URL avec paramètres pour faciliter la connexion
    # Optionnel : encoder l'email pour pré-remplir le formulaire de connexion
    import urllib.parse
    params = urllib.parse.urlencode({'email': collaborateur.email})
    qr_login_url = f"{login_url}?{params}"
    
    # Générer le QR code en mémoire
    qr_image_base64 = generate_qr_code_base64(qr_login_url)
    
    # Pour le mode impression, on va utiliser un template spécial
    is_print = request.GET.get('print', 'false') == 'true'
    
    context = {
        'collaborateur': collaborateur,
        'date_emission': timezone.now(),
        'qr_code_base64': qr_image_base64,
        'qr_login_url': qr_login_url,
        'is_print': is_print,
        # Statistiques (optionnelles)
        'total_etudiants': 150,
        'total_parrainages': getattr(collaborateur, 'nombre_parrainages', 0),
        'total_memos': 45,
    }
    
    # Si c'est une impression, utiliser un template sans éléments de navigation
    template_name = 'Collaborateurs/recu_impression.html' if is_print else 'Collaborateurs/recu.html'
    
    return render(request, template_name, context)

def generate_qr_code_base64(data):
    """
    Génère un QR code et le retourne en base64 pour l'intégrer directement dans le HTML
    """
    try:
        # Créer le QR code
        qr = qrcode.QRCode(
            version=4,  # Version plus élevée pour plus de capacité
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Haute correction d'erreur
            box_size=8,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Redimensionner pour une meilleure qualité
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        
        # Ajouter un logo au centre (optionnel)
        # img = add_logo_to_qr(img)
        
        # Convertir en base64
        buffer = BytesIO()
        img.save(buffer, format='PNG', optimize=True, quality=95)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    except Exception as e:
        print(f"Erreur génération QR code: {e}")
        return None

def add_logo_to_qr(qr_image):
    """
    Optionnel : Ajoute un petit logo au centre du QR code
    """
    try:
        # Créer un logo simple
        logo_size = 40
        logo = Image.new('RGB', (logo_size, logo_size), color='white')
        draw = ImageDraw.Draw(logo)
        
        # Dessiner un cercle ou un carré avec la première lettre
        draw.rectangle([(0, 0), (logo_size, logo_size)], fill='#6a11cb')
        draw.ellipse([(5, 5), (logo_size-5, logo_size-5)], fill='white')
        
        # Essayer d'ajouter du texte (nécessite une police)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            draw.text((logo_size//2-10, logo_size//2-10), "D", fill='#6a11cb', font=font)
        except:
            pass
        
        # Calculer la position pour centrer le logo
        qr_width, qr_height = qr_image.size
        logo_position = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        
        # Coller le logo
        qr_image.paste(logo, logo_position, logo if logo.mode == 'RGBA' else None)
        
        return qr_image
    except:
        return qr_image






class CollaborateurListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des collaborateurs avec recherche et filtres
    """
    model = Collaborateur
    template_name = "Collaborateurs/liste.html"  # Assurez-vous que le nom correspond à votre template
    context_object_name = "collaborateurs"
    paginate_by = 12  # Valeur par défaut
    
    def get_paginate_by(self, queryset):
        """
        Permet de changer le nombre d'éléments par page via l'URL
        """
        paginate_by = self.request.GET.get('paginate_by')
        if paginate_by and paginate_by.isdigit():
            return int(paginate_by)
        return self.paginate_by
    
    def get_queryset(self):
        """
        Récupère la liste des collaborateurs avec filtres et recherche
        """
        # Récupérer le queryset de base
        queryset = Collaborateur.objects.all()
        
        # Annoter avec le nombre d'étudiants
        queryset = queryset.annotate(
            nombre_etudiants=Count('etudiant')  # Utilisez le bon nom de relation
        )
        
        # Récupérer les paramètres de filtre
        search_query = self.request.GET.get('search', '')
        statut = self.request.GET.get('statut', '')
        periode = self.request.GET.get('periode', '')
        
        # Appliquer les filtres
        if search_query:
            queryset = queryset.filter(
                Q(last_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(matricule__icontains=search_query) |
                Q(contact__icontains=search_query) |
                Q(code_parainage__icontains=search_query)
            )
        
        # Filtre par statut
        if statut == 'actif':
            queryset = queryset.filter(is_active=True)
        elif statut == 'inactif':
            queryset = queryset.filter(is_active=False)
        
        # Filtre par date
        if periode == 'aujourdhui':
            queryset = queryset.filter(
                date_inscription_collaborateur__date=timezone.now().date()
            )
        elif periode == 'semaine':
            queryset = queryset.filter(
                date_inscription_collaborateur__gte=timezone.now() - timedelta(days=7)
            )
        elif periode == 'mois':
            queryset = queryset.filter(
                date_inscription_collaborateur__gte=timezone.now() - timedelta(days=30)
            )
        
        # Trier par date d'inscription (la plus récente d'abord)
        queryset = queryset.order_by('-date_inscription_collaborateur')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Ajoute des données supplémentaires au contexte
        """
        context = super().get_context_data(**kwargs)
        
        # Récupérer tous les collaborateurs pour les statistiques (sans filtres)
        all_collaborateurs = Collaborateur.objects.all()
        
        # Statistiques globales
        context['total_collaborateurs'] = all_collaborateurs.count()
        context['collaborateurs_actifs'] = all_collaborateurs.filter(is_active=True).count()
        
        # Nouveaux cette semaine
        semaine_derniere = timezone.now() - timedelta(days=7)
        context['nouveaux_cette_semaine'] = all_collaborateurs.filter(
            date_inscription_collaborateur__gte=semaine_derniere
        ).count()
        
        # Total des étudiants associés à tous les collaborateurs
        from django.db.models import Sum
        total_etudiants = all_collaborateurs.annotate(
            nb_etudiants=Count('etudiant')
        ).aggregate(total=Sum('nb_etudiants'))['total']
        context['total_etudiants_associes'] = total_etudiants or 0
        
        # Valeurs des filtres actuels
        context['search_query'] = self.request.GET.get('search', '')
        context['statut_filtre'] = self.request.GET.get('statut', '')
        context['periode_filtre'] = self.request.GET.get('periode', '')
        
        # Mode d'affichage (cartes ou tableau)
        context['view_mode'] = self.request.GET.get('view', 'cards')
        
        # Nombre d'éléments par page
        context['paginate_by'] = self.get_paginate_by(None)
        
        return context



class CollaborateurDetailView(LoginRequiredMixin, DetailView):
    model = Collaborateur
    template_name = 'Collaborateurs/detail.html'
    context_object_name = 'collaborateur'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Détail du collaborateur'
        return context


class CollaborateurDeleteView(LoginRequiredMixin, DeleteView):
    model = Collaborateur
    template_name = 'Collaborateurs/delete.html'
    success_url = reverse_lazy('liste_collaborateurs')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Supprimer le collaborateur'
        return context


class CollaborateurUpdateView(LoginRequiredMixin, UpdateView):
    model = Collaborateur
    template_name = 'Collaborateurs/update.html'
    fields = ['first_name', 'last_name', 'email','contact','matricule', 'code_parainage', 'is_active']
    success_url = reverse_lazy('liste_collaborateurs')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier le collaborateur'
        return context