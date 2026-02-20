from re import search
from django.shortcuts import render
from .models import Paiement
from Dossiers.models import AnneeAcademique, Niveau
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from Dossiers.models import Dossier
from django.views.decorators.http import require_POST
from django.db.models import Sum


from django.shortcuts import get_object_or_404
import qrcode
from io import BytesIO
import base64
import json
from django.core.cache import cache
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from decimal import Decimal
import random




# ============================================
# VIEWS DE LA LISTE DES PAIEMENTS
# ============================================
class PaiementListView(ListView):
    model = Paiement
    template_name = 'Paiements/liste_paiement.html'
    context_object_name = 'paiements'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer tous les paiements pour les statistiques
        paiements_all = Paiement.objects.all()
        paiements_filtres = self.get_queryset()
        
        # Statistiques de base
        context['nb_paiements'] = paiements_all.count()
        context['paiement_total'] = paiements_all.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        context['tombola'] = paiements_all.filter(jeu_reduction=True).count()
        context['commission'] = paiements_all.aggregate(Sum('commission'))['commission__sum'] or 0
        context['frais_annexe'] = paiements_all.aggregate(Sum('frais_annexe'))['frais_annexe__sum'] or 0

        # Calculs supplémentaires
        total_commission = context['commission'] + context['frais_annexe']
        montant_tombola = context['tombola'] * 500

        # Formater les montants
        context['montant_tombola_formate'] = f"{montant_tombola:,.0f}".replace(",", " ")
        context['total_commission_formate'] = f"{total_commission:,.0f}".replace(",", " ")
        
        # Statistiques pour le template avancé
        context['total_revenus'] = context['paiement_total']
        context['paiements_complets'] = paiements_all.filter(statut=True).count()
        context['paiements_payes'] = paiements_all.filter(statut=True).count()
        context['montant_paye'] = paiements_all.filter(statut=True).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        context['paiements_attente'] = paiements_all.filter(statut=False).count()
        context['montant_attente'] = paiements_all.filter(statut=False).aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        
        # Paiements ce mois-ci
        today = datetime.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        paiements_mois = paiements_all.filter(date_paiement__gte=first_day)
        context['paiements_mois'] = paiements_mois.count()
        context['revenus_mois'] = paiements_mois.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        
        # Pour le tableau filtré
        context['total_filtre'] = paiements_filtres.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
        context['paiements_attente_filtre'] = paiements_filtres.filter(statut=False).count()
        
        # Données pour les graphiques
        context['paiements_payes_count'] = context['paiements_payes']
        context['paiements_partiels'] = 0  # À adapter si vous avez un statut partiel
        context['paiements_annules'] = 0   # À adapter si vous avez un statut annulé
        
        # Données pour graphique mensuel (simplifié)
        monthly_data = []
        monthly_labels = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i*30)
            month_payments = paiements_all.filter(
                date_paiement__month=date.month,
                date_paiement__year=date.year
            )
            monthly_data.append(float(month_payments.aggregate(Sum('montant_total'))['montant_total__sum'] or 0))
            monthly_labels.append(date.strftime('%b'))
        
        context['monthly_data'] = monthly_data
        context['monthly_labels'] = monthly_labels
        
        # Ajouter les années académiques et niveaux pour les filtres
        context['annees_academiques'] = AnneeAcademique.objects.all()
        context['niveaux'] = Niveau.objects.all()
        
        # Ajouter les filières pour les filtres
        from Utilisateurs.models import Filiere
        context['filieres'] = Filiere.objects.all()

        return context

    def get_queryset(self):
        # Base queryset avec les relations CORRIGÉES
        queryset = Paiement.objects.select_related(
            'etudiant',
            'etudiant__filiere',
            'etudiant__annee_academique',
            'etudiant__niveau',
        ).all()

        # Filtre de recherche - CORRIGÉ pour utiliser etudiant au lieu de dossier
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(etudiant__first_name__icontains=search_query) |
                Q(etudiant__last_name__icontains=search_query) |
                Q(etudiant__matricule__icontains=search_query) |
                Q(etudiant__filiere__nom__icontains=search_query) |
                Q(reference__icontains=search_query)
            )

        # Filtre par statut (adapté à votre modèle)
        statut = self.request.GET.get('statut')
        if statut == 'paye':
            queryset = queryset.filter(statut=True)
        elif statut == 'attente':
            queryset = queryset.filter(statut=False)

        # Filtre par filière - CORRIGÉ
        filiere = self.request.GET.get('filiere')
        if filiere:
            queryset = queryset.filter(etudiant__filiere_id=filiere)

        # Filtre par niveau - CORRIGÉ
        niveau = self.request.GET.get('niveau')
        if niveau:
            queryset = queryset.filter(etudiant__niveau_id=niveau)

        # Filtre par année académique - CORRIGÉ
        annee_academique = self.request.GET.get('annee_academique')
        if annee_academique:
            queryset = queryset.filter(etudiant__annee_academique_id=annee_academique)

        # Filtre par période
        periode = self.request.GET.get('periode')
        if periode == 'today':
            today = datetime.now().date()
            queryset = queryset.filter(date_paiement__date=today)
        elif periode == 'week':
            week_ago = datetime.now() - timedelta(days=7)
            queryset = queryset.filter(date_paiement__gte=week_ago)
        elif periode == 'month':
            first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(date_paiement__gte=first_day)
        elif periode == 'year':
            first_day = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(date_paiement__gte=first_day)
        elif periode == 'custom':
            date_debut = self.request.GET.get('date_debut')
            date_fin = self.request.GET.get('date_fin')
            if date_debut:
                queryset = queryset.filter(date_paiement__date__gte=date_debut)
            if date_fin:
                queryset = queryset.filter(date_paiement__date__lte=date_fin)

        # Filtre par montant
        montant_min = self.request.GET.get('montant_min')
        montant_max = self.request.GET.get('montant_max')
        if montant_min:
            queryset = queryset.filter(montant_total__gte=montant_min)
        if montant_max:
            queryset = queryset.filter(montant_total__lte=montant_max)

        # Tri
        tri = self.request.GET.get('tri')
        if tri:
            queryset = queryset.order_by(tri)
        else:
            queryset = queryset.order_by('-date_paiement')

        # Gestion du nombre d'éléments par page
        paginate_by = self.request.GET.get('paginate_by')
        if paginate_by:
            try:
                self.paginate_by = int(paginate_by)
            except ValueError:
                pass  # Garder la valeur par défaut si conversion échoue

        return queryset




# ============================================
# VIEWS DE gratter la réduction
# ============================================

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def gratter_reduction(request, paiement_id):
    """Vue pour gratter et révéler la réduction"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Méthode non autorisée'
        }, status=405)
    
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    if not paiement.jeu_reduction:
        return JsonResponse({
            'success': False,
            'error': 'Ce paiement n\'a pas de jeu de réduction'
        })
    
    if paiement.reduction_grattee:
        return JsonResponse({
            'success': False,
            'error': 'La réduction a déjà été grattée'
        })
    
    # Révéler la réduction
    try:
        if paiement.reveler_reduction():
            return JsonResponse({
                'success': True,
                'reduction_percentage': float(paiement.reduction_percentage),
                'montant_reduction': float(paiement.montant_reduction),
                'montant_final': float(paiement.montant_total),
                'message': f'Félicitations ! Vous avez obtenu {paiement.reduction_percentage}% de réduction'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Impossible de révéler la réduction'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        })



def scanner_qr_code(request, reference):
    """Vue appelée quand on scanne le QR code"""
    paiement = get_object_or_404(Paiement, reference=reference)
    
    # Calculer les montants
    montant_avant_reduction = paiement.frais_impression + paiement.frais_annexe
    
    # Générer QR code
    qr_code = None
    if paiement.jeu_reduction:
        qr_data = {
            'type': 'reduction_universitaire',
            'reference': paiement.reference,
            'etudiant': f"{paiement.etudiant.last_name} {paiement.etudiant.first_name}",
            'montant_initial': str(montant_avant_reduction),
            'url_grattage': request.build_absolute_uri()
        }
        
        try:
            import qrcode
            import base64
            from io import BytesIO
            
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
            qr_code = base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"Erreur génération QR code: {e}")
            qr_code = None
    
    context = {
        'paiement': paiement,
        'etudiant': paiement.etudiant,
        'deja_gratté': paiement.reduction_grattee,
        'reduction_revelee': paiement.reduction_revealed,
        'reduction_percentage': float(paiement.reduction_percentage) if paiement.reduction_revealed else None,
        'montant_avant_reduction': montant_avant_reduction,
        'qr_code': qr_code,
    }
    
    return render(request, 'Tombola/grattage_reduction.html', context)




# ============================================
# VIEWS DE LA TOMBOLA
# ============================================
class TombolaListView(ListView):
    model = Paiement
    template_name = 'Paiements/tombola_list.html'
    context_object_name = 'paiements'
    paginate_by = 10
    
    def get_queryset(self):
        # Filtrer uniquement les paiements avec jeu_reduction=True
        return Paiement.objects.filter(jeu_reduction=True).select_related('etudiant')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
                
        # Récupérer les données statistiques
        paiements_tombola = Paiement.objects.filter(jeu_reduction=True)
        montant_Perdu = Paiement.objects.filter(
            reduction_percentage__gt=0
        ).aggregate(total_reduction=Sum('montant_reduction'))

        nb_gagnant = Paiement.objects.filter(
            reduction_percentage__gt=0
        ).count()



        # Compter le nombre total de participants à la tombola
        nb_tombola = paiements_tombola.count()
        montant_Perdu = montant_Perdu['total_reduction'] or 0
        nb_gagnant = nb_gagnant 

        
        # Calculer le montant total des paiements tombola
        total_montant = 0
        for paiement in paiements_tombola:
            total_montant += 500
        
        # Récupérer les étudiants uniques qui participent à la tombola
        etudiants_participants = list(set(
            p.etudiant for p in paiements_tombola.select_related('etudiant')
        ))
        
        # Pour chaque étudiant participant, vérifier s'il a un dossier
        dossiers_etudiants = {}
        for etudiant in etudiants_participants:
            try:
                dossier = Dossier.objects.get(etudiant=etudiant)
                dossiers_etudiants[etudiant.id] = dossier
            except Dossier.DoesNotExist:
                dossiers_etudiants[etudiant.id] = None
        
        # Ajouter les données au contexte
        context['nb_tombola'] = nb_tombola
        context['total_montant'] = total_montant
        context['montant_Perdu'] = montant_Perdu
        context['nb_gagnant'] = nb_gagnant
        context['dossiers_etudiants'] = dossiers_etudiants 
        
        # Optionnel : pour un affichage par étudiant avec leurs paiements tombola
        etudiants_data = []
        for etudiant in etudiants_participants:
            paiements_etudiant = paiements_tombola.filter(etudiant=etudiant)
            etudiants_data.append({
                'etudiant': etudiant,
                'paiements': paiements_etudiant,
                'nombre_paiements': paiements_etudiant.count(),
                'total_etudiant': paiements_etudiant.aggregate(
                    total=Sum('montant_total')
                )['total'] or 0,
                'dossier': dossiers_etudiants.get(etudiant.id)
            })
        
        context['etudiants_data'] = etudiants_data
        
        return context

    
# ============================================
# VIEWS DE DETAIL D'UN PAIEMENT
# ============================================

class PaiementDetailView(DetailView):
    model = Paiement
    template_name = 'Paiements/detail_paiement.html'
    context_object_name = 'paiement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paiement = self.get_object()
    
        # Récupère l'étudiant associé au paiement
        etudiant = paiement.etudiant
        
        # Essaie de récupérer le dossier de l'étudiant associé au paiement
        try:
            dossier = Dossier.objects.get(etudiant=etudiant)
            context['dossier'] = dossier
        except Dossier.DoesNotExist:
            context['dossier'] = None

        # Essaie de récupérer les paiements
        paiements = Paiement.objects.filter(etudiant=etudiant)
        context['paiements'] = paiements
        context['nb_paie_etudiant'] = paiements.count()
        context['Montant'] = paiement.frais_impression + paiement.frais_annexe
        context['Montant_formate'] = f"{context['Montant']:,.0f}".replace(",", " ")

        context['etudiant'] = etudiant
        
        # Générer QR code uniquement si jeu_reduction est coché
        if paiement.jeu_reduction:
            context['qr_code'] = self.generate_qr_code(paiement)
            context['reduction_grattee'] = paiement.reduction_grattee
            context['reduction_percentage'] = paiement.reduction_percentage
            context['montant_sans_reduction'] = (paiement.frais_impression or Decimal('0')) + (paiement.frais_annexe or Decimal('0'))
            
            # Statistiques de probabilité
            context['probabilites'] = {
                '0': 80,
                '10': 15,
                '15': 5
            }
        else:
            context['qr_code'] = None
            context['reduction_grattee'] = False
            
        return context
    
    def generate_qr_code(self, paiement):
        """Génère un QR code pour le paiement avec réduction"""
        # Créer une clé unique pour le cache
        cache_key = f"qr_code_{paiement.id}_{paiement.reference}"
        
        # Vérifier si le QR code est déjà en cache
        cached_qr = cache.get(cache_key)
        if cached_qr:
            return cached_qr
        
        # Construire l'URL absolue pour le grattage
        request = self.request
        url_grattage = request.build_absolute_uri(f'/paiements/jeu/{paiement.reference}/')
        
        # Données à encoder dans le QR code
        qr_data = {
            'type': 'jeu_reduction_universitaire',
            'reference': paiement.reference,
            'etudiant': {
                'nom': paiement.etudiant.last_name,
                'prenom': paiement.etudiant.first_name,
                'matricule': paiement.etudiant.matricule,
            },
            'montant_initial': str((paiement.frais_impression or Decimal('0')) + (paiement.frais_annexe or Decimal('0'))),
            'date': paiement.date_paiement.isoformat(),
            'statut': paiement.statut,
            'jeu_reduction': True,
            'reduction_grattee': paiement.reduction_grattee,
            'url_grattage': url_grattage
        }
        
        # Convertir en chaîne JSON
        qr_string = json.dumps(qr_data, ensure_ascii=False)
        
        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Créer une image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Mettre en cache pendant 1 heure
        cache.set(cache_key, img_str, 3600)
        
        return img_str

# Vue pour gratter le jeu
@csrf_exempt
@require_POST
def gratter_jeu_view(request, paiement_id):
    """Vue pour gratter le jeu et obtenir la réduction"""
    try:
        paiement = get_object_or_404(Paiement, id=paiement_id)
        
        # Vérifier si le paiement a le jeu de réduction
        if not paiement.jeu_reduction:
            return JsonResponse({
                'success': False,
                'error': 'Ce paiement n\'a pas de jeu de réduction'
            })
        
        # Vérifier si le jeu a déjà été gratté
        if paiement.reduction_grattee:
            return JsonResponse({
                'success': False,
                'error': 'Ce jeu a déjà été gratté',
                'reduction_percentage': float(paiement.reduction_percentage),
                'montant_reduction': float(paiement.montant_reduction),
                'montant_final': float(paiement.montant_total)
            })
        
        # Générer la réduction aléatoire
        # Probabilités: 0% = 80%, 10% = 15%, 15% = 5%
        rand = random.random() * 100
        
        if rand <= 80:  # 80% de chance
            reduction_percentage = Decimal('0.00')
        elif rand <= 95:  # 15% de chance (80-95)
            reduction_percentage = Decimal('10.00')
        else:  # 5% de chance (95-100)
            reduction_percentage = Decimal('15.00')
        
        # Calculer le montant de la réduction
        montant_sans_reduction = (paiement.frais_impression or Decimal('0')) + (paiement.frais_annexe or Decimal('0'))
        montant_reduction = montant_sans_reduction * (reduction_percentage / Decimal('100'))
        
        # Mettre à jour le paiement
        paiement.reduction_percentage = reduction_percentage
        paiement.montant_reduction = montant_reduction
        paiement.montant_total = montant_sans_reduction - montant_reduction
        paiement.reduction_grattee = True
        paiement.date_reduction_grattee = timezone.now()
        paiement.save()
        
        # Créer un historique pour le jeu gratté
        HistoriqueJeu.objects.create(
            paiement=paiement,
            pourcentage_reduction=reduction_percentage,
            montant_reduction=montant_reduction
        )
        
        return JsonResponse({
            'success': True,
            'reduction_percentage': float(reduction_percentage),
            'montant_reduction': float(montant_reduction),
            'montant_final': float(paiement.montant_total),
            'montant_initial': float(montant_sans_reduction),
            'message': f'Félicitations ! Vous avez obtenu une réduction de {reduction_percentage}%'
        })
            
    except Paiement.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Paiement non trouvé'
        })

# Vue pour afficher l'interface de grattage
def interface_grattage(request, code_jeu):
    """Interface de grattage accessible via QR code"""
    try:
        paiement = Paiement.objects.get(code_jeu=code_jeu)
        
        context = {
            'paiement': paiement,
            'etudiant': paiement.etudiant,
            'montant_initial': (paiement.frais_impression or Decimal('0')) + (paiement.frais_annexe or Decimal('0')),
            'reduction_grattee': paiement.reduction_grattee,
            'reduction_percentage': paiement.reduction_percentage,
            'montant_reduction': paiement.montant_reduction,
            'probabilites': {
                '0': 80,
                '10': 15,
                '15': 5
            }
        }
        
        return render(request, 'Paiements/interface_grattage.html', context)
        
    except Paiement.DoesNotExist:
        messages.error(request, 'Code de jeu invalide')
        return redirect('home')
