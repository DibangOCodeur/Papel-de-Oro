/**
 * dashboard.js — DbgMemo Collaborateur
 * Version mobile avec données réelles et URLs intégrées
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    /* ============================================================
       ATTENDRE QUE CHART.JS SOIT CHARGÉ
       ============================================================ */
    if (typeof Chart === 'undefined') {
        console.error('Chart.js non chargé!');
        setTimeout(init, 100);
    } else {
        init();
    }

    function init() {
        /* ============================================================
           ÉLÉMENTS DOM
           ============================================================ */
        const body = document.body;
        const themeToggle = document.getElementById('themeToggle');
        const notificationBtn = document.getElementById('notificationBtn');
        const currentDateEl = document.getElementById('currentDate');
        const searchInput = document.getElementById('searchInput');
        const searchContainer = document.getElementById('searchContainer');
        const periodSelect = document.getElementById('evolutionPeriod');
        
        // Vérifier que chartData existe
        if (typeof window.chartData === 'undefined') {
            console.warn('chartData non défini, utilisation des données par défaut');
            window.chartData = {
                evolution: {
                    labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
                    etudiants: [0, 0, 0, 0, 0, 0],
                    memoires: [0, 0, 0, 0, 0, 0]
                },
                filiere: {
                    labels: ['Aucune donnée'],
                    data: [1]
                }
            };
        }

        // Vérifier que menuItems existe
        if (typeof window.menuItems === 'undefined') {
            console.warn('menuItems non défini');
            window.menuItems = {
                etudiants: [],
                memoires: [],
                paiements: [],
                plus: [],
                accueil: []
            };
        }

        // Bottom navigation
        const bottomNavItems = document.querySelectorAll('.bottom-nav-item');
        const contextMenu = document.getElementById('contextMenu');
        const contextMenuBackdrop = document.getElementById('contextMenuBackdrop');

        /* ============================================================
           THÈME CLAIR / SOMBRE
           ============================================================ */
        function applyTheme(theme) {
            if (theme === 'light') {
                body.classList.remove('dark-mode');
            } else {
                body.classList.add('dark-mode');
            }
            setTimeout(() => {
                refreshAllCharts();
            }, 50);
        }

        function initTheme() {
            const savedTheme = localStorage.getItem('dbgmemo_theme');
            if (savedTheme) {
                applyTheme(savedTheme);
            }
        }

        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                const isDark = body.classList.contains('dark-mode');
                const newTheme = isDark ? 'light' : 'dark';
                localStorage.setItem('dbgmemo_theme', newTheme);
                applyTheme(newTheme);
                
                if (window.navigator && window.navigator.vibrate) {
                    window.navigator.vibrate(10);
                }
            });
        }

        /* ============================================================
           DATE DYNAMIQUE
           ============================================================ */
        function updateDateTime() {
            if (!currentDateEl) return;
            
            const now = new Date();
            const options = { 
                weekday: 'long', 
                day: 'numeric', 
                month: 'long'
            };
            
            currentDateEl.textContent = now.toLocaleDateString('fr-FR', options);
        }

        updateDateTime();
        setInterval(updateDateTime, 3600000);

        /* ============================================================
           RECHERCHE EXPANDABLE
           ============================================================ */
        if (searchContainer && searchInput) {
            searchContainer.addEventListener('click', function(e) {
                e.stopPropagation();
                this.classList.add('expanded');
                searchInput.focus();
            });

            document.addEventListener('click', function(e) {
                if (!searchContainer.contains(e.target)) {
                    searchContainer.classList.remove('expanded');
                    searchInput.value = '';
                    
                    document.querySelectorAll('.top-student-item, .order-item').forEach(item => {
                        item.style.background = '';
                    });
                }
            });

            searchInput.addEventListener('input', function() {
                const term = this.value.toLowerCase().trim();
                
                if (term.length < 2) {
                    document.querySelectorAll('.top-student-item, .order-item').forEach(item => {
                        item.style.background = '';
                    });
                    return;
                }

                document.querySelectorAll('.top-student-item').forEach(item => {
                    const nameElement = item.querySelector('strong');
                    if (nameElement) {
                        const name = nameElement.textContent.toLowerCase();
                        const match = name.includes(term);
                        item.style.background = match ? 'var(--hover)' : '';
                    }
                });

                document.querySelectorAll('.order-item').forEach(item => {
                    const nameElement = item.querySelector('strong');
                    if (nameElement) {
                        const name = nameElement.textContent.toLowerCase();
                        const match = name.includes(term);
                        item.style.background = match ? 'var(--hover)' : '';
                    }
                });
            });
        }

        /* ============================================================
           GRAPHIQUES AVEC DONNÉES RÉELLES
           ============================================================ */
        
        let evolutionChart = null;
        let filiereChart = null;

        function getChartColors() {
            const isDark = body.classList.contains('dark-mode');
            return {
                text: isDark ? '#e8eaf6' : '#1e2a3a',
                grid: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                tooltipBg: isDark ? 'rgba(20,25,41,0.95)' : 'rgba(255,255,255,0.95)',
            };
        }

        function initCharts() {
            const colors = getChartColors();

            // Graphique d'évolution
            const evolutionCanvas = document.getElementById('evolutionChart');
            if (evolutionCanvas) {
                if (evolutionChart) {
                    evolutionChart.destroy();
                }

                const ctx = evolutionCanvas.getContext('2d');
                
                evolutionChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: window.chartData.evolution?.labels || ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
                        datasets: [
                            {
                                label: 'Étudiants',
                                data: window.chartData.evolution?.etudiants || [0, 0, 0, 0, 0, 0],
                                borderColor: '#6a11cb',
                                backgroundColor: 'rgba(106,17,203,0.1)',
                                borderWidth: 3,
                                tension: 0.4,
                                fill: true,
                                pointBackgroundColor: '#6a11cb',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                            },
                            {
                                label: 'Mémoires',
                                data: window.chartData.evolution?.memoires || [0, 0, 0, 0, 0, 0],
                                borderColor: '#f39c12',
                                backgroundColor: 'rgba(243,156,18,0.1)',
                                borderWidth: 3,
                                tension: 0.4,
                                fill: true,
                                pointBackgroundColor: '#f39c12',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    color: colors.text,
                                    font: { 
                                        size: 11, 
                                        family: 'Poppins',
                                        weight: '500'
                                    },
                                    boxWidth: 12,
                                    padding: 15,
                                    usePointStyle: true,
                                    pointStyle: 'circle'
                                }
                            },
                            tooltip: {
                                backgroundColor: colors.tooltipBg,
                                titleColor: colors.text,
                                bodyColor: colors.text,
                                titleFont: { size: 12, weight: '600' },
                                bodyFont: { size: 11 },
                                padding: 12,
                                cornerRadius: 10,
                                displayColors: true,
                                borderColor: '#6a11cb',
                                borderWidth: 1,
                                callbacks: {
                                    label: function(context) {
                                        return `${context.dataset.label}: ${context.raw}`;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { 
                                    color: colors.grid,
                                    drawBorder: false,
                                    lineWidth: 1
                                },
                                ticks: { 
                                    color: colors.text, 
                                    font: { size: 10 },
                                    stepSize: 1,
                                    callback: function(value) {
                                        return Number.isInteger(value) ? value : null;
                                    }
                                }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { 
                                    color: colors.text, 
                                    font: { size: 10 },
                                    maxRotation: 30
                                }
                            }
                        }
                    }
                });
            }

            // Graphique des filières
            const filiereCanvas = document.getElementById('filiereChart');
            if (filiereCanvas) {
                if (filiereChart) {
                    filiereChart.destroy();
                }

                const ctx = filiereCanvas.getContext('2d');
                const colorsPalette = ['#6a11cb', '#f39c12', '#27ae60', '#e74c3c', '#3498db', '#9b59b6', '#1abc9c'];

                // Vérifier s'il y a des données
                const hasData = window.chartData.filiere?.data && 
                               window.chartData.filiere.data.length > 0 && 
                               window.chartData.filiere.data[0] > 0;

                filiereChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: hasData ? window.chartData.filiere.labels : ['Aucune donnée'],
                        datasets: [{
                            data: hasData ? window.chartData.filiere.data : [1],
                            backgroundColor: hasData ? 
                                colorsPalette.slice(0, window.chartData.filiere.data.length) : 
                                ['#95a5a6'],
                            borderColor: 'transparent',
                            borderWidth: 0,
                            hoverOffset: 8,
                            borderRadius: 5,
                            spacing: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '65%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    color: colors.text,
                                    font: { 
                                        size: 10, 
                                        family: 'Poppins' 
                                    },
                                    boxWidth: 10,
                                    padding: 15,
                                    usePointStyle: true,
                                    pointStyle: 'circle'
                                }
                            },
                            tooltip: {
                                backgroundColor: colors.tooltipBg,
                                titleColor: colors.text,
                                bodyColor: colors.text,
                                titleFont: { size: 12, weight: '600' },
                                bodyFont: { size: 11 },
                                padding: 12,
                                cornerRadius: 10,
                                callbacks: {
                                    label: function(context) {
                                        if (!hasData) {
                                            return 'Aucune donnée disponible';
                                        }
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const value = context.raw;
                                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                        return `${context.label}: ${value} étud. (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            console.info('Graphiques initialisés avec les données réelles');
        }

        function refreshAllCharts() {
            const colors = getChartColors();
            
            if (evolutionChart) {
                evolutionChart.options.plugins.legend.labels.color = colors.text;
                evolutionChart.options.scales.y.ticks.color = colors.text;
                evolutionChart.options.scales.y.grid.color = colors.grid;
                evolutionChart.options.scales.x.ticks.color = colors.text;
                evolutionChart.options.plugins.tooltip.backgroundColor = colors.tooltipBg;
                evolutionChart.options.plugins.tooltip.titleColor = colors.text;
                evolutionChart.options.plugins.tooltip.bodyColor = colors.text;
                evolutionChart.update();
            }
            
            if (filiereChart) {
                filiereChart.options.plugins.legend.labels.color = colors.text;
                filiereChart.options.plugins.tooltip.backgroundColor = colors.tooltipBg;
                filiereChart.options.plugins.tooltip.titleColor = colors.text;
                filiereChart.options.plugins.tooltip.bodyColor = colors.text;
                filiereChart.update();
            }
        }

        // Initialiser les graphiques
        setTimeout(() => {
            initCharts();
        }, 100);

        /* ============================================================
           SÉLECTEUR DE PÉRIODE
           ============================================================ */
        if (periodSelect) {
            periodSelect.addEventListener('change', function() {
                const chartCard = this.closest('.chart-card');
                if (chartCard) chartCard.classList.add('loading');
                
                // Simulation de chargement
                setTimeout(() => {
                    if (chartCard) chartCard.classList.remove('loading');
                    
                    // TODO: Faire un appel AJAX pour charger les données de la période
                    console.log('Période sélectionnée:', this.value);
                }, 800);
            });
        }

        /* ============================================================
           MENUS CONTEXTUELS AVEC DONNÉES RÉELLES ET URLs
           ============================================================ */
        
        // Utiliser les données de window.menuItems
        const menuItems = window.menuItems;

        function showContextMenu(menuType) {
            if (!contextMenu || !contextMenuBackdrop) return;
            
            contextMenu.innerHTML = '';
            
            const items = menuItems[menuType] || [];
            
            if (items.length === 0) {
                hideContextMenu();
                return;
            }
            
            items.forEach(item => {
                const button = document.createElement('button');
                button.className = 'context-menu-item';
                
                let badgeHtml = '';
                if (item.badge && parseInt(item.badge) > 0) {
                    badgeHtml = `<em class="menu-badge">${item.badge}</em>`;
                }
                
                button.innerHTML = `
                    <i class="fas ${item.icon}"></i>
                    <span>${item.label}</span>
                    ${badgeHtml}
                `;
                
                button.addEventListener('click', function() {
                    console.log('Action:', item.label);
                    
                    if (window.navigator && window.navigator.vibrate) {
                        window.navigator.vibrate(10);
                    }
                    
                    hideContextMenu();
                    
                    // Redirection vers l'URL si elle existe
                    if (item.url) {
                        window.location.href = item.url;
                    }
                });
                
                contextMenu.appendChild(button);
            });
            
            contextMenu.classList.add('show');
            contextMenuBackdrop.classList.add('show');
        }

        function hideContextMenu() {
            if (contextMenu) contextMenu.classList.remove('show');
            if (contextMenuBackdrop) contextMenuBackdrop.classList.remove('show');
        }

        if (bottomNavItems.length > 0) {
            bottomNavItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    bottomNavItems.forEach(nav => nav.classList.remove('active'));
                    this.classList.add('active');
                    
                    const menuType = this.dataset.menu;
                    
                    if (window.navigator && window.navigator.vibrate) {
                        window.navigator.vibrate(10);
                    }
                    
                    if (menuType === 'accueil') {
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        hideContextMenu();
                    } else {
                        showContextMenu(menuType);
                    }
                });
            });
        }

        if (contextMenuBackdrop) {
            contextMenuBackdrop.addEventListener('click', hideContextMenu);
        }

        /* ============================================================
           NOTIFICATIONS
           ============================================================ */
        if (notificationBtn) {
            notificationBtn.addEventListener('click', function() {
                const badge = this.querySelector('.notif-badge');
                if (badge) {
                    badge.style.display = 'none';
                }
                
                // Compter les tâches prioritaires réelles
                const tachesPrioritaires = document.querySelectorAll('.task-item').length;
                if (tachesPrioritaires > 0) {
                    alert(`${tachesPrioritaires} tâche(s) prioritaire(s) en attente`);
                } else {
                    alert('Aucune nouvelle notification');
                }
                
                if (window.navigator && window.navigator.vibrate) {
                    window.navigator.vibrate(20);
                }
            });
        }

        /* ============================================================
           GESTION DU SCROLL
           ============================================================ */
        let lastScrollTop = 0;
        const header = document.querySelector('.mobile-header');
        
        if (header) {
            window.addEventListener('scroll', () => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    header.style.transform = 'translateY(-100%)';
                    header.style.opacity = '0';
                } else {
                    header.style.transform = 'translateY(0)';
                    header.style.opacity = '1';
                }
                
                lastScrollTop = scrollTop;
            }, { passive: true });
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
        }, { 
            threshold: 0.1,
            rootMargin: '0px 0px -20px 0px'
        });

        document.querySelectorAll('.card, .chart-card, .stat-card, .activity-summary-card').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(el);
        });

        /* ============================================================
           MISE À JOUR DES BADGES AVEC DONNÉES RÉELLES
           ============================================================ */
        function updateBadges() {
            const userData = window.userData || {};
            
            // Mettre à jour les badges de la bottom navigation
            const etudiantsBadge = document.querySelector('.bottom-nav-item[data-menu="etudiants"] .bottom-nav-badge');
            const memoiresBadge = document.querySelector('.bottom-nav-item[data-menu="memoires"] .bottom-nav-badge');
            
            if (etudiantsBadge && userData.nbNouveauxEtudiants > 0) {
                etudiantsBadge.textContent = userData.nbNouveauxEtudiants;
            }
            
            if (memoiresBadge && userData.nbMemoiresEncours > 0) {
                memoiresBadge.textContent = userData.nbMemoiresEncours;
            }
        }

        updateBadges();

        /* ============================================================
           INITIALISATION
           ============================================================ */
        initTheme();
        
        console.info('[DbgMemo] Interface mobile prête avec données réelles et URLs');
    }
});