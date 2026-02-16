// dashboard.js - Gestion du dashboard admin
document.addEventListener('DOMContentLoaded', function() {

    // Supprimer la scrollbar globale
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    
    // Ajouter le style pour masquer les scrollbars
    const style = document.createElement('style');
    style.textContent = `
        /* Masquer toutes les scrollbars */
        * {
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        
        *::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
        
        /* Conteneurs spécifiques qui ont besoin de défilement */
        .table-container,
        .table-body,
        .modal-content,
        .form-container,
        .student-details,
        .student-details-grid {
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        
        .table-container::-webkit-scrollbar,
        .table-body::-webkit-scrollbar,
        .modal-content::-webkit-scrollbar,
        .form-container::-webkit-scrollbar,
        .student-details::-webkit-scrollbar,
        .student-details-grid::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
        
        /* Empêcher le défilement du body quand on scroll dans les conteneurs */
        .table-container,
        .modal-content {
            overscroll-behavior: contain;
        }
        
        /* S'assurer que le tableau occupe tout l'espace disponible */
        .table-wrapper {
            max-height: calc(100vh - 250px);
            overflow: hidden;
        }
    `;
    document.head.appendChild(style);

    // Éléments DOM
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    const tombolaModal = document.getElementById('tombolaModal');
    const drawTombolaBtn = document.getElementById('drawTombola');
    const notificationBtn = document.querySelector('.notification-btn');
    const currentDateEl = document.getElementById('currentDate');
    const logoutBtn = document.querySelector('.btn-logout');
    
    // Mettre à jour la date actuelle
    function updateCurrentDate() {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        currentDateEl.textContent = now.toLocaleDateString('fr-FR', options);
    }
    
    updateCurrentDate();
    
    // Gestion du mode clair/sombre
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            
            // Sauvegarder la préférence
            const isDarkMode = body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            
            // Animation du bouton
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
        
        // Restaurer la préférence utilisateur
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode !== null) {
            if (savedDarkMode === 'true') {
                body.classList.add('dark-mode');
            } else {
                body.classList.remove('dark-mode');
            }
        }
    }
    
    // Fermer le modal
    const closeModalBtns = document.querySelectorAll('.modal-close, .modal-close-btn');
    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            tombolaModal.classList.remove('active');
        });
    });
    
    // Fermer le modal en cliquant à l'extérieur
    tombolaModal.addEventListener('click', function(e) {
        if (e.target === tombolaModal) {
            tombolaModal.classList.remove('active');
        }
    });
    
    // Gestion des notifications
    if (notificationBtn) {
        notificationBtn.addEventListener('click', function() {
            // Animation du bouton
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // Simuler l'affichage des notifications
            alert('Notifications:\n\n1. Nouveau mémoire soumis par Amara Kouassi\n2. Paiement reçu de Fatou Diop\n3. Problème d\'impression signalé\n4. 5 nouveaux étudiants inscrits\n5. Tombola: tirage prévu demain\n6. Mise à jour système disponible\n7. Rapport mensuel généré');
            
            // Réinitialiser le compteur
            const count = document.querySelector('.notification-count');
            count.textContent = '0';
            count.style.display = 'none';
        });
    }
    
    // Gestion de la déconnexion
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
                // Animation de déconnexion
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Déconnexion...';
                
                setTimeout(() => {
                    alert('Déconnexion réussie. Redirection vers la page de connexion...');
                    window.location.href = 'index.html';
                }, 1500);
            }
        });
    }
    
    // Animation des cartes au survol
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Animation des barres du graphique
    const chartBars = document.querySelectorAll('.chart-bar');
    chartBars.forEach(bar => {
        bar.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        bar.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Animation des lignes du tableau
    const tableRows = document.querySelectorAll('.table-row');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
    
    // Gestion des actions rapides
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.querySelector('span').textContent;
            
            // Animation du bouton
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // Simulation de l'action
            alert(`Action "${action}" déclenchée !\n\nCette fonctionnalité sera implémentée dans la version finale.`);
        });
    });
    
    // Mettre à jour l'heure toutes les minutes
    function updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('fr-FR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // Ajouter l'heure à la date si nécessaire
        const dateDisplay = document.querySelector('.date-display span');
        if (dateDisplay) {
            dateDisplay.textContent = dateDisplay.textContent.split(' - ')[0] + ' - ' + timeString;
        }
    }
    
    setInterval(updateTime, 60000);
    updateTime(); // Initial call
    
    // Effet parallaxe sur les cercles d'arrière-plan
    document.addEventListener('mousemove', function(e) {
        const circles = document.querySelectorAll('.circle');
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        circles.forEach((circle, index) => {
            const speed = (index + 1) * 0.2;
            const x = (mouseX * speed * 20) - 10;
            const y = (mouseY * speed * 20) - 10;
            
            circle.style.transform = `translate(${x}px, ${y}px) rotate(${index * 45}deg)`;
        });
    });
    
    // Animation d'entrée des éléments
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observer les éléments à animer
    document.querySelectorAll('.card, .dashboard-stats').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Simulation de données en temps réel
    function simulateRealTimeUpdates() {
        // Mettre à jour aléatoirement les statistiques
        setInterval(() => {
            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
                const current = parseInt(stat.textContent.replace(/\D/g, ''));
                const change = Math.floor(Math.random() * 5);
                const newValue = current + change;
                stat.textContent = newValue.toLocaleString() + (stat.textContent.includes('FCFA') ? ' FCFA' : '');
                
                // Petite animation
                stat.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    stat.style.transform = 'scale(1)';
                }, 300);
            });
        }, 10000); // Toutes les 10 secondes
    }
    
    simulateRealTimeUpdates();
});



// Gestion des sous-menus interactifs
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter la classe has-submenu aux li qui ont des ul
    const menuItems = document.querySelectorAll('.sidebar-nav li');
    menuItems.forEach(item => {
        if (item.querySelector('ul')) {
            item.classList.add('has-submenu');
            
            // Ajouter une flèche
            const link = item.querySelector('> a');
            const arrow = document.createElement('i');
            arrow.className = 'fas fa-chevron-down arrow';
            link.appendChild(arrow);
        }
    });
    
    // Gestion du clic sur les éléments avec sous-menu
    const submenuParents = document.querySelectorAll('.sidebar-nav li.has-submenu > a');
    submenuParents.forEach(parent => {
        parent.addEventListener('click', function(e) {
            e.preventDefault();
            const parentLi = this.parentElement;
            
            // Fermer les autres sous-menus
            document.querySelectorAll('.sidebar-nav li.has-submenu').forEach(item => {
                if (item !== parentLi) {
                    item.classList.remove('active');
                }
            });
            
            // Basculer le sous-menu courant
            parentLi.classList.toggle('active');
            
            // Animation supplémentaire
            const submenu = parentLi.querySelector('ul');
            if (parentLi.classList.contains('active')) {
                submenu.style.maxHeight = submenu.scrollHeight + 'px';
            } else {
                submenu.style.maxHeight = '0';
            }
        });
    });
    
    // Fermer les sous-menus en cliquant ailleurs
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.sidebar-nav')) {
            document.querySelectorAll('.sidebar-nav li.has-submenu').forEach(item => {
                item.classList.remove('active');
                const submenu = item.querySelector('ul');
                if (submenu) {
                    submenu.style.maxHeight = '0';
                }
            });
        }
    });
    
    // Animation des statistiques au survol
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.stat-icon');
            icon.style.transform = 'scale(1.1) rotate(5deg)';
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.stat-icon');
            icon.style.transform = 'scale(1) rotate(0)';
        });
    });
    
    // Animation des badges de notification
    const notificationBadges = document.querySelectorAll('.notification-badge');
    notificationBadges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.2)';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Animation pour les liens du sous-menu
    const submenuLinks = document.querySelectorAll('.sidebar-nav li ul li a');
    submenuLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
});