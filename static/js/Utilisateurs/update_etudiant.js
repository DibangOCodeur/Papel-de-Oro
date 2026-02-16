// Ajouter ce code à votre fichier etudiant_form.js (après le code existant)

// Fonction pour gérer le défilement sur mobile
function initResponsiveScroll() {
    const isMobile = window.innerWidth <= 768;
    const cardBody = document.querySelector('.card-body');
    const previewCard = document.querySelector('.preview-card');
    
    if (!cardBody || !previewCard) return;
    
    if (isMobile) {
        // Mode mobile : activation du défilement
        cardBody.style.overflowY = 'auto';
        cardBody.style.maxHeight = 'calc(70vh - 120px)';
        
        previewCard.style.overflowY = 'auto';
        previewCard.style.maxHeight = 'calc(70vh - 120px)';
        
        // Ajouter du padding pour éviter que le contenu ne touche les bords
        cardBody.style.paddingRight = '10px';
        
        // Désactiver le défilement sur le body quand on scroll dans les sections
        const sections = [cardBody, previewCard];
        
        sections.forEach(section => {
            section.addEventListener('touchstart', function() {
                this.classList.add('scrolling');
            });
            
            section.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('scrolling');
                }, 100);
            });
            
            section.addEventListener('scroll', function() {
                if (this.scrollTop <= 0) {
                    this.scrollTop = 1;
                }
                if (this.scrollTop + this.clientHeight >= this.scrollHeight) {
                    this.scrollTop = this.scrollHeight - this.clientHeight - 1;
                }
            });
        });
        
        // Désactiver l'overscroll sur mobile
        document.body.style.overscrollBehavior = 'none';
        
        // Prévenir le zoom sur les champs
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('touchstart', function(e) {
                e.stopPropagation();
            });
        });
        
        // Smooth scroll pour la navigation entre les onglets
        const tabs = document.querySelectorAll('.form-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const contentId = this.dataset.tab + '-tab';
                const content = document.getElementById(contentId);
                if (content) {
                    content.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Smooth scroll pour la navigation entre les étapes
        const nextBtn = document.getElementById('nextBtn');
        const prevBtn = document.getElementById('prevBtn');
        
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                setTimeout(() => {
                    const currentContent = document.querySelector('.form-step-content.active');
                    if (currentContent) {
                        currentContent.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }, 300);
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                setTimeout(() => {
                    const currentContent = document.querySelector('.form-step-content.active');
                    if (currentContent) {
                        currentContent.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }, 300);
            });
        }
        
    } else {
        // Mode desktop : désactivation du défilement
        cardBody.style.overflowY = 'visible';
        cardBody.style.maxHeight = 'none';
        
        previewCard.style.overflowY = 'visible';
        previewCard.style.maxHeight = 'none';
        
        document.body.style.overscrollBehavior = 'auto';
    }
}

// Fonction pour ajuster la hauteur des sections
function adjustSectionHeights() {
    const isMobile = window.innerWidth <= 768;
    const viewportHeight = window.innerHeight;
    const headerHeight = document.querySelector('.dashboard-header')?.offsetHeight || 80;
    
    if (isMobile) {
        // Calculer la hauteur disponible
        const availableHeight = viewportHeight - headerHeight - 50; // 50px pour le padding/margin
        
        // Ajuster la hauteur de la section principale
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.minHeight = availableHeight + 'px';
        }
        
        // Ajuster la hauteur des cartes
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.maxHeight = (availableHeight * 0.8) + 'px';
        });
    } else {
        // Réinitialiser les hauteurs sur desktop
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.minHeight = 'auto';
        }
        
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.maxHeight = 'none';
        });
    }
}

// Initialisation du défilement responsive
function initResponsiveLayout() {
    initResponsiveScroll();
    adjustSectionHeights();
    
    // Écouter les changements de taille de fenêtre
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            initResponsiveScroll();
            adjustSectionHeights();
        }, 200);
    });
    
    // Écouter les changements d'orientation
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            initResponsiveScroll();
            adjustSectionHeights();
        }, 300);
    });
    
    // Prévenir le zoom sur iOS pour les champs
    if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
        const viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {
            viewport.content = viewport.content + ', maximum-scale=1.0, user-scalable=no';
        }
    }
}

// Ajouter ces fonctions à l'initialisation existante
document.addEventListener('DOMContentLoaded', function() {
    // ... votre code existant ...
    
    // Initialiser le layout responsive
    setTimeout(() => {
        initResponsiveLayout();
    }, 100);
    
    // Ajuster la hauteur initiale
    window.dispatchEvent(new Event('resize'));
});

// Fonction pour la gestion des formulaires en mode mobile
function initMobileFormBehavior() {
    const form = document.getElementById('studentForm');
    if (!form) return;
    
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Focus sur le premier champ lors du changement d'onglet
        const tabs = document.querySelectorAll('.form-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                setTimeout(() => {
                    const activeTab = document.querySelector('.form-step-content.active');
                    const firstInput = activeTab.querySelector('input, select, textarea');
                    if (firstInput) {
                        firstInput.focus();
                        
                        // Pour iOS, on scroll vers l'élément
                        setTimeout(() => {
                            firstInput.scrollIntoView({
                                behavior: 'smooth',
                                block: 'center'
                            });
                        }, 100);
                    }
                }, 300);
            });
        });
        
        // Ajuster la position lors du focus sur un champ
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                // Ajuster la position pour éviter que le clavier masque le champ
                setTimeout(() => {
                    const inputRect = this.getBoundingClientRect();
                    const viewportHeight = window.innerHeight;
                    
                    // Si le champ est dans la moitié inférieure de l'écran
                    if (inputRect.bottom > viewportHeight / 2) {
                        this.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }
                }, 300);
            });
        });
    }
}

// Ajouter à l'initialisation
document.addEventListener('DOMContentLoaded', function() {
    // ... votre code existant ...
    
    setTimeout(() => {
        initMobileFormBehavior();
    }, 100);
});