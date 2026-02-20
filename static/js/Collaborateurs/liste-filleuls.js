/**
 * liste-filleuls.js - Gestion de la liste des filleuls
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    /* ============================================================
       ÉLÉMENTS DOM
       ============================================================ */
    const body = document.body;
    const backButton = document.getElementById('backButton');
    const searchInput = document.getElementById('searchFilleuls');
    const filterBtn = document.getElementById('filterBtn');
    const sortBtn = document.getElementById('sortBtn');
    const filterChips = document.querySelectorAll('.chip');
    const filleulsCards = document.querySelectorAll('.filleul-card');
    const contextMenu = document.getElementById('contextMenu');
    const contextMenuBackdrop = document.getElementById('contextMenuBackdrop');

    /* ============================================================
       RETOUR À LA PAGE PRÉCÉDENTE
       ============================================================ */
    if (backButton) {
        backButton.addEventListener('click', function() {
            window.history.back();
        });
    }

    /* ============================================================
       RECHERCHE EN DIRECT
       ============================================================ */
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            filleulsCards.forEach(card => {
                const nom = card.dataset.nom || '';
                const filiere = card.dataset.filiere || '';
                
                if (searchTerm === '' || nom.includes(searchTerm) || filiere.includes(searchTerm)) {
                    card.style.display = 'block';
                    
                    // Animation de surbrillance
                    if (searchTerm !== '') {
                        card.style.transform = 'scale(1.01)';
                        card.style.borderColor = 'var(--primary)';
                        setTimeout(() => {
                            card.style.transform = '';
                        }, 300);
                    } else {
                        card.style.borderColor = '';
                    }
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    /* ============================================================
       FILTRES PAR STATUT
       ============================================================ */
    filterChips.forEach(chip => {
        chip.addEventListener('click', function() {
            // Retirer la classe active de tous les chips
            filterChips.forEach(c => c.classList.remove('active'));
            
            // Ajouter la classe active au chip cliqué
            this.classList.add('active');
            
            const filterValue = this.dataset.filter;
            
            filleulsCards.forEach(card => {
                if (filterValue === 'all') {
                    card.style.display = 'block';
                } else {
                    const statut = card.dataset.statut;
                    if (filterValue === 'actif' && (statut === 'encours' || statut === 'en cours')) {
                        card.style.display = 'block';
                    } else if (filterValue === 'termine' && (statut === 'terminé' || statut === 'livré')) {
                        card.style.display = 'block';
                    } else if (filterValue === 'en_attente' && statut === 'aucun') {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
            
            // Feedback haptique
            if (window.navigator && window.navigator.vibrate) {
                window.navigator.vibrate(5);
            }
        });
    });

    /* ============================================================
       TRI
       ============================================================ */
    if (sortBtn) {
        sortBtn.addEventListener('click', function() {
            showSortMenu();
        });
    }

    function showSortMenu() {
        if (!contextMenu || !contextMenuBackdrop) return;
        
        const sortOptions = [
            { icon: 'fa-sort-alpha-down', label: 'Nom (A-Z)', value: 'nom_asc' },
            { icon: 'fa-sort-alpha-up', label: 'Nom (Z-A)', value: 'nom_desc' },
            { icon: 'fa-sort-numeric-down', label: 'Date (récent)', value: 'date_desc' },
            { icon: 'fa-sort-numeric-up', label: 'Date (ancien)', value: 'date_asc' },
            { icon: 'fa-coins', label: 'Commission (décroissant)', value: 'commission_desc' }
        ];
        
        contextMenu.innerHTML = '';
        
        sortOptions.forEach(option => {
            const button = document.createElement('button');
            button.className = 'context-menu-item';
            button.innerHTML = `
                <i class="fas ${option.icon}"></i>
                <span>${option.label}</span>
            `;
            
            button.addEventListener('click', function() {
                console.log('Trier par:', option.label);
                hideContextMenu();
                
                if (window.navigator && window.navigator.vibrate) {
                    window.navigator.vibrate(10);
                }
                
                // Rediriger avec le paramètre de tri
                window.location.href = `?sort=${option.value}`;
            });
            
            contextMenu.appendChild(button);
        });
        
        contextMenu.classList.add('show');
        contextMenuBackdrop.classList.add('show');
    }

    /* ============================================================
       MENU FILTRE
       ============================================================ */
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            showFilterMenu();
        });
    }

    function showFilterMenu() {
        if (!contextMenu || !contextMenuBackdrop) return;
        
        const filterOptions = [
            { icon: 'fa-calendar', label: 'Ce mois', value: 'mois' },
            { icon: 'fa-calendar-week', label: 'Cette semaine', value: 'semaine' },
            { icon: 'fa-check-circle', label: 'Dossiers terminés', value: 'termine' },
            { icon: 'fa-clock', label: 'En attente', value: 'attente' },
            { icon: 'fa-money-bill', label: 'Avec paiement', value: 'paye' }
        ];
        
        contextMenu.innerHTML = '';
        
        filterOptions.forEach(option => {
            const button = document.createElement('button');
            button.className = 'context-menu-item';
            button.innerHTML = `
                <i class="fas ${option.icon}"></i>
                <span>${option.label}</span>
            `;
            
            button.addEventListener('click', function() {
                console.log('Filtrer par:', option.label);
                hideContextMenu();
                
                if (window.navigator && window.navigator.vibrate) {
                    window.navigator.vibrate(10);
                }
                
                // Rediriger avec le paramètre de filtre
                window.location.href = `?filter=${option.value}`;
            });
            
            contextMenu.appendChild(button);
        });
        
        contextMenu.classList.add('show');
        contextMenuBackdrop.classList.add('show');
    }

    /* ============================================================
       FERMETURE DU MENU CONTEXTUEL
       ============================================================ */
    function hideContextMenu() {
        if (contextMenu) contextMenu.classList.remove('show');
        if (contextMenuBackdrop) contextMenuBackdrop.classList.remove('show');
    }

    if (contextMenuBackdrop) {
        contextMenuBackdrop.addEventListener('click', hideContextMenu);
    }

    /* ============================================================
       ANIMATIONS D'ENTRÉE
       ============================================================ */
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.filleul-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(el);
    });

    /* ============================================================
       INITIALISATION
       ============================================================ */
    console.info('[DbgMemo] Page liste des filleuls prête');
});

/* ============================================================
   FONCTIONS GLOBALES POUR LES ACTIONS (avec URLs)
   ============================================================ */
function voirDossier(id) {
    console.log('Voir dossier:', id);
    const url = window.appUrls?.dossier + id + '/';
    if (url !== '#/') {
        window.location.href = url;
    } else {
        alert('URL du dossier non configurée');
    }
}

function voirPaiements(id) {
    console.log('Voir paiements:', id);
    const url = window.appUrls?.paiements + id + '/';
    if (url !== '#/') {
        window.location.href = url;
    } else {
        alert('URL des paiements non configurée');
    }
}

function contacter(id) {
    console.log('Contacter:', id);
    // Ouvrir le chat ou envoyer un message
    alert(`Fonctionnalité de contact pour l'étudiant ${id} à venir`);
}

function plusOptions(id) {
    console.log('Plus options:', id);
    // Afficher menu contextuel avec plus d'options
    const options = [
        { label: 'Modifier', action: `modifier(${id})` },
        { label: 'Historique', action: `historique(${id})` },
        { label: 'Supprimer', action: `supprimer(${id})` }
    ];
    
    // Créer un menu simple
    const action = prompt(`Options pour l'étudiant ${id}:\n1. Modifier\n2. Historique\n3. Supprimer`);
    if (action === '1') modifier(id);
    else if (action === '2') historique(id);
    else if (action === '3') supprimer(id);
}

function ajouterFilleul() {
    console.log('Ajouter un filleul');
    const url = window.appUrls?.ajouter;
    if (url && url !== '#') {
        window.location.href = url;
    } else {
        alert('URL d\'ajout non configurée');
    }
}

function changerPage(page) {
    console.log('Changer page:', page);
    const url = new URL(window.location.href);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
}

function modifier(id) {
    console.log('Modifier:', id);
    window.location.href = `/collaborateur/etudiants/modifier/${id}/`;
}

function historique(id) {
    console.log('Historique:', id);
    window.location.href = `/collaborateur/etudiants/historique/${id}/`;
}

function supprimer(id) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer l'étudiant ${id} ?`)) {
        console.log('Supprimer:', id);
        window.location.href = `/collaborateur/etudiants/supprimer/${id}/`;
    }
}