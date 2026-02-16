from django.core import paginator
from django.shortcuts import render
from .models import Dossier, AnneeAcademique, Niveau
from Utilisateurs.models import Filiere
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.db.models import Sum, Count, Q
from decimal import Decimal

class ListDossierView(ListView):
    model = Dossier
    template_name = 'Dossiers/liste_memoire.html'
    context_object_name = 'dossiers'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_dossiers'] = Dossier.objects.count()
        context['filieres'] = Filiere.objects.all()
        context['support'] = Dossier.objects.filter(support_pdf__isnull=False).count()
        context['total_valides'] = Dossier.objects.filter(statut__exact=True).count()
        context['total_livres'] = Dossier.objects.filter(livraison__exact=True).count()
        context['total_attente'] = Dossier.objects.filter(statut__exact=False).count()

        context['annees_academiques'] = AnneeAcademique.objects.all()
        context['niveaux'] = Niveau.objects.all()
        
        return context

    def get_queryset(self):
        queryset = Dossier.objects.select_related(
            'etudiant',
            'paiement',
            'etudiant__filiere',
            'etudiant__annee_academique',
            'etudiant__niveau',
        ).all()    
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(etudiant__first_name__icontains=search) |
                Q(etudiant__last_name__icontains=search) |
                Q(etudiant__matricule__icontains=search) |
                Q(etudiant__filiere__nom__icontains=search)
            )
        
        filiere = self.request.GET.get('filiere')
        if filiere:
            queryset = queryset.filter(etudiant__filiere__nom=filiere)

        niveau = self.request.GET.get('niveau')
        if niveau:
            queryset = queryset.filter(etudiant__niveau_id=niveau)

        annee_academique = self.request.GET.get('annee_academique')
        if annee_academique:
            queryset = queryset.filter(etudiant__annee_academique_id=annee_academique)

        paginate_by = self.request.GET.get('paginate_by')
        if paginate_by:
            self.paginate_by = int(paginate_by)
        
        return queryset


class UpdateDossierView(UpdateView):
    model = Dossier
    template_name = 'Dossiers/modifier.html'
    paginator_by = 10

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)





from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from Paiements.models import Paiement
from Utilisateurs.models import Etudiant, Filiere
from Dossiers.models import Dossier
import json
from django.http import JsonResponse

def statistiques(request):
    """Page de statistiques globales"""
    context = {}
    
    # Période sélectionnée (par défaut 30 jours)
    periode = request.GET.get('periode', '30')
    if periode == 'all':
        jours = None
    else:
        jours = int(periode)
    
    # Dates pour les filtres
    date_fin = timezone.now()
    if jours:
        date_debut = date_fin - timedelta(days=jours)
    else:
        date_debut = None
    
    # ============================================
    # KPI CARDS - Statistiques globales
    # ============================================
    
    # Nombre total d'étudiants
    context['total_etudiants'] = Etudiant.objects.count()
    
    # Étudiants actifs
    if jours:
        etudiants_actifs = Etudiant.objects.filter(
            paiements__date_paiement__gte=date_debut
        ).distinct().count()
    else:
        etudiants_actifs = Etudiant.objects.filter(
            paiements__isnull=False
        ).distinct().count()
    context['etudiants_actifs'] = etudiants_actifs
    
    # Croissance des étudiants
    if jours and date_debut:
        periode_precedente_debut = date_debut - timedelta(days=jours)
        periode_precedente_fin = date_debut
        etudiants_precedent = Etudiant.objects.filter(
            date_inscription__range=[periode_precedente_debut, periode_precedente_fin]
        ).count()
        etudiants_actuels = Etudiant.objects.filter(
            date_inscription__range=[date_debut, date_fin]
        ).count()
        
        if etudiants_precedent > 0:
            croissance_etudiants = ((etudiants_actuels - etudiants_precedent) / etudiants_precedent * 100)
        else:
            croissance_etudiants = 100 if etudiants_actuels > 0 else 0
        context['croissance_etudiants'] = round(croissance_etudiants, 1)
    else:
        context['croissance_etudiants'] = 0
    
    # Mémoires traités
    context['memoires_traites'] = Dossier.objects.filter(statut=True).count()
    
    # Croissance des mémoires
    if jours and date_debut:
        memoires_actuels = Dossier.objects.filter(
            date_creation__range=[date_debut, date_fin]
        ).count()
        memoires_precedent = Dossier.objects.filter(
            date_creation__range=[periode_precedente_debut, periode_precedente_fin]
        ).count()
        
        if memoires_precedent > 0:
            croissance_memoires = ((memoires_actuels - memoires_precedent) / memoires_precedent * 100)
        else:
            croissance_memoires = 100 if memoires_actuels > 0 else 0
        context['croissance_memoires'] = round(croissance_memoires, 1)
    else:
        context['croissance_memoires'] = 0
    
    # Chiffre d'affaires total
    chiffre_affaires = Paiement.objects.aggregate(
        total=Sum('montant_total')
    )['total'] or Decimal('0')
    context['chiffre_affaires'] = f"{int(chiffre_affaires):,}".replace(',', ' ')
    
    # Croissance du CA
    if jours and date_debut:
        ca_actuel = Paiement.objects.filter(
            date_paiement__range=[date_debut, date_fin]
        ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
        
        ca_precedent = Paiement.objects.filter(
            date_paiement__range=[periode_precedente_debut, periode_precedente_fin]
        ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
        
        if ca_precedent > 0:
            croissance_ca = ((ca_actuel - ca_precedent) / ca_precedent * 100)
        else:
            croissance_ca = 100 if ca_actuel > 0 else 0
        context['croissance_ca'] = round(croissance_ca, 1)
    else:
        context['croissance_ca'] = 0
    
    # Taux de conversion
    etudiants_avec_paiement = Etudiant.objects.filter(paiements__isnull=False).distinct().count()
    if context['total_etudiants'] > 0:
        taux_conversion = (etudiants_avec_paiement / context['total_etudiants'] * 100)
    else:
        taux_conversion = 0
    context['taux_conversion'] = round(taux_conversion, 1)
    
    # ============================================
    # DONNÉES POUR LES GRAPHIQUES
    # ============================================
    
    # 1. Évolution des revenus par jour
    revenus_par_jour = []
    labels_jours = []
    
    if jours:
        for i in range(jours - 1, -1, -1):
            date_jour = date_fin.date() - timedelta(days=i)
            jour_suivant = date_jour + timedelta(days=1)
            
            total_jour = Paiement.objects.filter(
                date_paiement__date__gte=date_jour,
                date_paiement__date__lt=jour_suivant
            ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
            
            revenus_par_jour.append(float(total_jour))
            labels_jours.append(date_jour.strftime('%d/%m'))
    else:
        # Derniers 30 jours par défaut
        for i in range(29, -1, -1):
            date_jour = date_fin.date() - timedelta(days=i)
            jour_suivant = date_jour + timedelta(days=1)
            
            total_jour = Paiement.objects.filter(
                date_paiement__date__gte=date_jour,
                date_paiement__date__lt=jour_suivant
            ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
            
            revenus_par_jour.append(float(total_jour))
            labels_jours.append(date_jour.strftime('%d/%m'))
    
    context['revenus_par_jour'] = json.dumps(revenus_par_jour)
    context['labels_jours'] = json.dumps(labels_jours)
    
    # 2. Répartition par service
    impression_seule = Paiement.objects.filter(
        frais_impression__gt=0, 
        service_annexe=False
    ).count()
    
    mise_en_forme = Paiement.objects.filter(
        service_annexe=True, 
        intitule_annexes='MISE_EN_FORME'
    ).count()
    
    page_garde = Paiement.objects.filter(
        service_annexe=True, 
        intitule_annexes='PAGE_DE_GARDE'
    ).count()
    
    complet = Paiement.objects.filter(
        service_annexe=True, 
        intitule_annexes='COMPLET'
    ).count()
    
    # Éviter les données vides
    services_data = [
        impression_seule or 1,  # Valeur minimale pour éviter graphique vide
        mise_en_forme or 1,
        page_garde or 1,
        complet or 1
    ]
    
    context['services_labels'] = json.dumps([
        'Impression seule', 
        'Mise en forme', 
        'Page de garde', 
        'Pack complet'
    ])
    context['services_data'] = json.dumps(services_data)
    
    # 3. Mémoires par filière (Top 8)
    filieres_data = []
    filieres_labels = []
    
    top_filieres = Filiere.objects.annotate(
        nb_memoires=Count('etudiant__dossier')
    ).filter(nb_memoires__gt=0).order_by('-nb_memoires')[:8]
    
    if top_filieres.exists():
        for filiere in top_filieres:
            filieres_labels.append(filiere.abreviation or filiere.nom[:12])
            filieres_data.append(filiere.nb_memoires)
        
        # Ajouter "Autres" si nécessaire
        autres_filieres = Filiere.objects.exclude(
            id__in=top_filieres.values_list('id', flat=True)
        ).aggregate(total=Count('etudiant__dossier'))['total'] or 0
        
        if autres_filieres > 0:
            filieres_labels.append('Autres')
            filieres_data.append(autres_filieres)
    else:
        # Données par défaut si aucune filière
        filieres_labels = ['Aucune donnée']
        filieres_data = [1]
    
    context['filieres_labels'] = json.dumps(filieres_labels)
    context['filieres_data'] = json.dumps(filieres_data)
    
    # 4. Évolution des inscriptions d'étudiants
    inscriptions_par_jour = []
    
    if jours:
        for i in range(jours - 1, -1, -1):
            date_jour = date_fin.date() - timedelta(days=i)
            jour_suivant = date_jour + timedelta(days=1)
            
            nb_inscriptions = Etudiant.objects.filter(
                date_inscription__gte=date_jour,
                date_inscription__lt=jour_suivant
            ).count()
            
            inscriptions_par_jour.append(nb_inscriptions)
    else:
        for i in range(29, -1, -1):
            date_jour = date_fin.date() - timedelta(days=i)
            jour_suivant = date_jour + timedelta(days=1)
            
            nb_inscriptions = Etudiant.objects.filter(
                date_inscription__gte=date_jour,
                date_inscription__lt=jour_suivant
            ).count()
            
            inscriptions_par_jour.append(nb_inscriptions)
    
    context['inscriptions_par_jour'] = json.dumps(inscriptions_par_jour)
    
    # ============================================
    # TABLEAU DES POINTS JOURNALIERS (7 derniers jours)
    # ============================================
    
    points_journaliers = []
    jours_semaine = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    for i in range(6, -1, -1):
        date_jour = date_fin.date() - timedelta(days=i)
        jour_suivant = date_jour + timedelta(days=1)
        
        revenus_jour = Paiement.objects.filter(
            date_paiement__date__gte=date_jour,
            date_paiement__date__lt=jour_suivant
        ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
        
        nb_paiements = Paiement.objects.filter(
            date_paiement__date__gte=date_jour,
            date_paiement__date__lt=jour_suivant
        ).count()
        
        nb_nouveaux_etudiants = Etudiant.objects.filter(
            date_inscription__gte=date_jour,
            date_inscription__lt=jour_suivant
        ).count()
        
        nb_memoires_traites = Dossier.objects.filter(
            date_modification__date__gte=date_jour,
            date_modification__date__lt=jour_suivant,
            statut=True
        ).count()
        
        nb_memoires_livres = Dossier.objects.filter(
            date_livraison__date__gte=date_jour,
            date_livraison__date__lt=jour_suivant,
            livraison=True
        ).count()
        
        reductions_jour = Paiement.objects.filter(
            date_paiement__date__gte=date_jour,
            date_paiement__date__lt=jour_suivant,
            reduction_revealed=True
        ).aggregate(total=Sum('montant_reduction'))['total'] or Decimal('0')
        
        top_paiement = Paiement.objects.filter(
            date_paiement__date__gte=date_jour,
            date_paiement__date__lt=jour_suivant
        ).order_by('-montant_total').first()
        
        points_journaliers.append({
            'date': date_jour.strftime('%d/%m/%Y'),
            'jour_semaine': jours_semaine[date_jour.weekday()],
            'revenus': f"{int(revenus_jour):,}".replace(',', ' '),
            'nb_paiements': nb_paiements,
            'nb_nouveaux_etudiants': nb_nouveaux_etudiants,
            'nb_memoires_traites': nb_memoires_traites,
            'nb_memoires_livres': nb_memoires_livres,
            'reductions': f"{int(reductions_jour):,}".replace(',', ' '),
            'top_paiement_nom': f"{top_paiement.etudiant.first_name} {top_paiement.etudiant.last_name}" if top_paiement else '-',
            'top_paiement_montant': f"{int(top_paiement.montant_total):,}".replace(',', ' ') if top_paiement else '-'
        })
    
    context['points_journaliers'] = points_journaliers
    
    # ============================================
    # TABLEAU DES PERFORMANCES HEBDOMADAIRES (5 dernières semaines)
    # ============================================
    
    performances_hebdomadaires = []
    
    for i in range(4, -1, -1):
        # Début de semaine (lundi)
        date_fin_semaine = date_fin.date() - timedelta(weeks=i)
        debut_semaine = date_fin_semaine - timedelta(days=date_fin_semaine.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        # Pour la semaine en cours, on ajuste la date de fin
        if i == 0:
            fin_semaine = date_fin.date()
        
        # Données de la semaine
        nb_etudiants = Etudiant.objects.filter(
            date_inscription__gte=debut_semaine,
            date_inscription__lte=fin_semaine
        ).count()
        
        nb_memoires = Dossier.objects.filter(
            date_creation__gte=debut_semaine,
            date_creation__lte=fin_semaine
        ).count()
        
        revenus = Paiement.objects.filter(
            date_paiement__date__gte=debut_semaine,
            date_paiement__date__lte=fin_semaine
        ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
        
        tombola = Paiement.objects.filter(
            date_paiement__date__gte=debut_semaine,
            date_paiement__date__lte=fin_semaine,
            jeu_reduction=True
        ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
        
        # Calcul du bénéfice (30% du CA)
        benefice = revenus * Decimal('0.3')
        
        # Évolution par rapport à la semaine précédente
        if i < 4:
            semaine_precedente_debut = debut_semaine - timedelta(days=7)
            semaine_precedente_fin = fin_semaine - timedelta(days=7)
            revenus_precedent = Paiement.objects.filter(
                date_paiement__date__gte=semaine_precedente_debut,
                date_paiement__date__lte=semaine_precedente_fin
            ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
            
            if revenus_precedent > 0:
                evolution = ((revenus - revenus_precedent) / revenus_precedent * 100)
            else:
                evolution = 100 if revenus > 0 else 0
        else:
            evolution = 0
        
        performances_hebdomadaires.append({
            'semaine': f"S{5-i}",
            'periode': f"{debut_semaine.strftime('%d/%m')} - {fin_semaine.strftime('%d/%m')}",
            'etudiants': nb_etudiants,
            'memoires': nb_memoires,
            'revenus': f"{int(revenus):,}".replace(',', ' '),
            'tombola': f"{int(tombola):,}".replace(',', ' '),
            'benefice': f"{int(benefice):,}".replace(',', ' '),
            'evolution': round(evolution, 1),
            'revenus_float': float(revenus)
        })
    
    context['performances_hebdomadaires'] = performances_hebdomadaires
    
    # ============================================
    # STATISTIQUES PAR STATUT
    # ============================================
    
    total_dossiers = Dossier.objects.count()
    
    if total_dossiers > 0:
        en_attente = Dossier.objects.filter(statut=False, livraison=False).count()
        en_traitement = Dossier.objects.filter(statut=True, livraison=False).count()
        livres = Dossier.objects.filter(livraison=True).count()
    else:
        en_attente = en_traitement = livres = 0
    
    context['en_attente'] = en_attente
    context['en_traitement'] = en_traitement
    context['livres'] = livres
    
    context['pourcentage_attente'] = round((en_attente / total_dossiers * 100), 1) if total_dossiers > 0 else 0
    context['pourcentage_traitement'] = round((en_traitement / total_dossiers * 100), 1) if total_dossiers > 0 else 0
    context['pourcentage_livres'] = round((livres / total_dossiers * 100), 1) if total_dossiers > 0 else 0
    
    context['date_actuelle'] = date_fin.strftime('%d %B %Y')
    
    return render(request, 'Dossiers/statistique.html', context)


def statistiques_api(request):
    """API pour les mises à jour en temps réel"""
    date_fin = timezone.now()
    
    # Revenus du jour
    revenus_aujourd_hui = Paiement.objects.filter(
        date_paiement__date=date_fin.date()
    ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0')
    
    # Nouveaux étudiants aujourd'hui
    nouveaux_aujourd_hui = Etudiant.objects.filter(
        date_inscription=date_fin.date()
    ).count()
    
    # Dernier paiement
    dernier_paiement = Paiement.objects.order_by('-date_paiement').first()
    
    data = {
        'revenus_aujourd_hui': float(revenus_aujourd_hui),
        'nouveaux_aujourd_hui': nouveaux_aujourd_hui,
        'dernier_paiement': {
            'etudiant': str(dernier_paiement.etudiant) if dernier_paiement else None,
            'montant': float(dernier_paiement.montant_total) if dernier_paiement else 0,
            'heure': dernier_paiement.date_paiement.strftime('%H:%M') if dernier_paiement else None
        } if dernier_paiement else None
    }
    
    return JsonResponse(data)