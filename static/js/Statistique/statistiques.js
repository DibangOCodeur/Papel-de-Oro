// statistiques.js - Gestion complète des graphiques et des données
document.addEventListener('DOMContentLoaded', function() {
    
    // Vérifier que les données existent
    if (typeof chartData !== 'undefined') {
        // Initialisation de tous les graphiques
        initRevenueChart();
        initServicePieChart();
        initFiliereChart();
        initStudentsChart();
    } else {
        console.error('chartData non défini');
    }
    
    // Configuration des événements
    setupRefreshButton();
    setupRealTimeUpdates();
    setupScrollAnimations();
    
    // Animation d'entrée des éléments
    animateCardsOnLoad();
});

// ============================================
// INITIALISATION DES GRAPHIQUES
// ============================================

let revenueChart, servicePieChart, filiereChart, studentsChart;

function initRevenueChart() {
    const canvas = document.getElementById('revenueChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Vérifier que les données existent
    if (!chartData.revenus || !chartData.labels) {
        ctx.font = '14px Poppins';
        ctx.fillStyle = '#888';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée disponible', canvas.width/2, canvas.height/2);
        return;
    }
    
    // Dégradé pour le remplissage
    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, 'rgba(106, 17, 203, 0.3)');
    gradient.addColorStop(1, 'rgba(106, 17, 203, 0.0)');
    
    revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Revenus (FCFA)',
                data: chartData.revenus,
                borderColor: '#6a11cb',
                backgroundColor: gradient,
                borderWidth: 3,
                pointBackgroundColor: '#6a11cb',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    callbacks: {
                        label: function(context) {
                            return 'Revenus: ' + context.parsed.y.toLocaleString() + ' FCFA';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        maxTicksLimit: 8,
                        color: getComputedStyle(document.body).getPropertyValue('--text-light').trim() || '#888'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(106, 17, 203, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + ' FCFA';
                        },
                        color: getComputedStyle(document.body).getPropertyValue('--text-light').trim() || '#888'
                    }
                }
            }
        }
    });
}

function initServicePieChart() {
    const canvas = document.getElementById('servicePieChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Vérifier que les données existent
    if (!chartData.servicesData || !chartData.servicesLabels) {
        ctx.font = '14px Poppins';
        ctx.fillStyle = '#888';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée disponible', canvas.width/2, canvas.height/2);
        return;
    }
    
    servicePieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.servicesLabels,
            datasets: [{
                data: chartData.servicesData,
                backgroundColor: [
                    '#6a11cb',
                    '#2575fc',
                    '#27ae60',
                    '#f39c12'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-color').trim() || '#333',
                        font: {
                            size: 11,
                            family: 'Poppins'
                        },
                        padding: 10,
                        boxWidth: 12,
                        boxHeight: 12
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

function initFiliereChart() {
    const canvas = document.getElementById('filiereChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Vérifier que les données existent
    if (!chartData.filieresData || !chartData.filieresLabels) {
        ctx.font = '14px Poppins';
        ctx.fillStyle = '#888';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée disponible', canvas.width/2, canvas.height/2);
        return;
    }
    
    filiereChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.filieresLabels,
            datasets: [{
                label: 'Nombre de mémoires',
                data: chartData.filieresData,
                backgroundColor: 'rgba(106, 17, 203, 0.8)',
                hoverBackgroundColor: '#6a11cb',
                borderRadius: 5,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y + ' mémoire' + (context.parsed.y > 1 ? 's' : '');
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-light').trim() || '#888',
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(106, 17, 203, 0.1)'
                    },
                    ticks: {
                        stepSize: 1,
                        color: getComputedStyle(document.body).getPropertyValue('--text-light').trim() || '#888'
                    }
                }
            }
        }
    });
}

function initStudentsChart() {
    const canvas = document.getElementById('studentsChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Vérifier que les données existent
    if (!chartData.inscriptions || !chartData.labels) {
        ctx.font = '14px Poppins';
        ctx.fillStyle = '#888';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée disponible', canvas.width/2, canvas.height/2);
        return;
    }
    
    // Dégradé pour le remplissage
    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, 'rgba(39, 174, 96, 0.3)');
    gradient.addColorStop(1, 'rgba(39, 174, 96, 0.0)');
    
    studentsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Nouveaux étudiants',
                data: chartData.inscriptions,
                borderColor: '#27ae60',
                backgroundColor: gradient,
                borderWidth: 3,
                pointBackgroundColor: '#27ae60',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y + ' étudiant' + (context.parsed.y > 1 ? 's' : '');
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        maxTicksLimit: 8,
                        color: getComputedStyle(document.body).getPropertyValue('--text-light').trim() || '#888'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(106, 17, 203, 0.1)'
                    },
                    ticks: {
                        stepSize: 1,
                        color: getComputedStyle(document.body).getPropertyValue('--text-light').trim() || '#888'
                    }
                }
            }
        }
    });
}

// ============================================
// FONCTIONS UTILITAIRES
// ============================================

function setupRefreshButton() {
    const refreshBtn = document.getElementById('refreshDailyPoints');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // Animation de chargement
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualisation...';
            this.disabled = true;
            
            // Simuler un chargement
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-sync-alt"></i> Actualiser';
                this.disabled = false;
                
                // Afficher une notification
                showNotification('Points journaliers mis à jour');
                
                // Animation sur les lignes du tableau
                document.querySelectorAll('.stats-table tbody tr').forEach(row => {
                    row.style.backgroundColor = 'rgba(106, 17, 203, 0.1)';
                    setTimeout(() => {
                        row.style.backgroundColor = '';
                    }, 500);
                });
            }, 1000);
        });
    }
}

function setupRealTimeUpdates() {
    // Mise à jour des données en temps réel toutes les 30 secondes
    fetchRealTimeData();
    setInterval(fetchRealTimeData, 30000);
}

function fetchRealTimeData() {
    fetch('/statistiques/api/')
        .then(response => response.json())
        .then(data => {
            // Mettre à jour les éléments de la sidebar
            const revenusEl = document.getElementById('revenusAujourdhui');
            const nouveauxEl = document.getElementById('nouveauxAujourdhui');
            const dernierEl = document.getElementById('dernierPaiement');
            
            if (revenusEl) {
                revenusEl.textContent = data.revenus_aujourd_hui.toLocaleString() + ' FCFA';
                animateElement(revenusEl);
            }
            
            if (nouveauxEl) {
                nouveauxEl.textContent = data.nouveaux_aujourd_hui;
                animateElement(nouveauxEl);
            }
            
            if (dernierEl && data.dernier_paiement && data.dernier_paiement.etudiant) {
                dernierEl.textContent = `${data.dernier_paiement.etudiant} (${data.dernier_paiement.montant.toLocaleString()} FCFA)`;
                animateElement(dernierEl);
            }
        })
        .catch(error => console.error('Erreur lors de la mise à jour:', error));
}

function animateElement(el) {
    el.style.transform = 'scale(1.1)';
    el.style.color = '#6a11cb';
    setTimeout(() => {
        el.style.transform = 'scale(1)';
        el.style.color = '';
    }, 300);
}

function setupScrollAnimations() {
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
    document.querySelectorAll('.chart-card, .table-section, .status-stat-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

function animateCardsOnLoad() {
    // Animation d'entrée pour les KPI cards
    const kpiCards = document.querySelectorAll('.kpi-card');
    kpiCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'real-time-notification';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ============================================
// GESTION DU REDIMENSIONNEMENT
// ============================================

let resizeTimeout;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
        // Redessiner les graphiques pour s'adapter à la nouvelle taille
        if (revenueChart) revenueChart.update();
        if (servicePieChart) servicePieChart.update();
        if (filiereChart) filiereChart.update();
        if (studentsChart) studentsChart.update();
    }, 250);
});