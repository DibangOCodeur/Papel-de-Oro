/**
 * liste-memoires.js - Gestion de la liste des mémoires imprimés
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    /* ============================================================
       ÉLÉMENTS DOM
       ============================================================ */
    const backButton = document.getElementById('backButton');
    const searchInput = document.getElementById('searchMemoires');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const memoiresCards = document.querySelectorAll('.memoire-card');
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
            
            memoiresCards.forEach(card => {
                const nom = card.dataset.nom || '';
                const filiere = card.dataset.filiere || '';
                const theme = card.dataset.theme || '';
                
                if (searchTerm === '' || 
                    nom.includes(searchTerm) || 
                    filiere.includes(searchTerm) ||
                    theme.includes(searchTerm)) {
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
       FILTRES PAR ONGLET
       ============================================================ */
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Retirer la classe active de tous les onglets
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // Ajouter la classe active à l'onglet cliqué
            this.classList.add('active');
            
            const tabValue = this.dataset.tab;
            
            memoiresCards.forEach(card => {
                if (tabValue === 'tous') {
                    card.style.display = 'block';
                } else {
                    const statut = card.dataset.statut;
                    if (statut === tabValue) {
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

    document.querySelectorAll('.memoire-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(el);
    });

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
       INITIALISATION
       ============================================================ */
    console.info('[DbgMemo] Page des mémoires imprimés prête');
});

/* ============================================================
   FONCTIONS GLOBALES POUR LES ACTIONS
   ============================================================ */
function voirDetails(id) {
    console.log('Voir détails:', id);
    const url = window.appUrls?.details_memoire + id + '/';
    if (url && url !== '#/') {
        window.location.href = url;
    } else {
        alert('URL des détails non configurée');
    }
}

function telechargerPDF(id) {
    console.log('Télécharger PDF:', id);
    const url = window.appUrls?.telecharger_pdf + id + '/';
    if (url && url !== '#/') {
        window.location.href = url;
    } else {
        alert('URL de téléchargement non configurée');
    }
}

function marquerLivre(id) {
    if (confirm('Marquer ce mémoire comme livré ?')) {
        console.log('Marquer livré:', id);
        const url = window.appUrls?.marquer_livre + id + '/';
        if (url && url !== '#/') {
            window.location.href = url;
        } else {
            alert('Action non configurée');
        }
    }
}

function plusOptions(id) {
    console.log('Plus options:', id);
    
    // Créer un menu contextuel simple
    const options = [
        { label: 'Modifier', action: `modifierMemoire(${id})` },
        { label: 'Voir paiements', action: `voirPaiements(${id})` },
        { label: 'Contacter étudiant', action: `contacterEtudiant(${id})` },
        { label: 'Supprimer', action: `supprimerMemoire(${id})` }
    ];
    
    // Afficher une boîte de dialogue simple
    const choix = prompt(
        `Options pour le mémoire #${id}:\n` +
        options.map((opt, index) => `${index + 1}. ${opt.label}`).join('\n')
    );
    
    if (choix && options[parseInt(choix) - 1]) {
        eval(options[parseInt(choix) - 1].action);
    }
}

function voirEnCours() {
    console.log('Voir mémoires en cours');
    const url = window.appUrls?.memoires_encours;
    if (url && url !== '#') {
        window.location.href = url;
    }
}

function changerPage(page) {
    console.log('Changer page:', page);
    const url = new URL(window.location.href);
    url.searchParams.set('page', page);
    window.location.href = url.toString();
}

function modifierMemoire(id) {
    console.log('Modifier mémoire:', id);
    window.location.href = `/collaborateur/memoires/modifier/${id}/`;
}

function voirPaiements(id) {
    console.log('Voir paiements:', id);
    window.location.href = `/collaborateur/paiements/memoire/${id}/`;
}

function contacterEtudiant(id) {
    console.log('Contacter étudiant du mémoire:', id);
    alert('Fonctionnalité de contact à venir');
}

function supprimerMemoire(id) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce mémoire ?')) {
        console.log('Supprimer mémoire:', id);
        window.location.href = `/collaborateur/memoires/supprimer/${id}/`;
    }
}