// etudiant_detail.js - Gestion de la page détail étudiant
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation de la page détail étudiant...');
    
    // Initialisation
    initDetailPage();
    
    function initDetailPage() {
        setupEventListeners();
        initCharts();
        updateLastSeen();
    }
    
    function setupEventListeners() {
        // Gestion des modals (déjà dans le template)
        // On ajoute des fonctionnalités supplémentaires ici
        
        // Téléchargement du mémoire
        const downloadButtons = document.querySelectorAll('.file-link');
        downloadButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                // Vous pouvez ajouter du tracking ici
                console.log('Téléchargement du fichier:', this.href);
            });
        });
        
        // Impression de la fiche
        document.getElementById('printBtn')?.addEventListener('click', printStudentCard);
        
        // Export des données
        document.getElementById('exportBtn')?.addEventListener('click', exportStudentData);
    }
    
    function initCharts() {
        // Initialisation des graphiques si nécessaire
        // Exemple avec Chart.js (vous devez l'inclure dans votre base.html)
        
        // Graphique d'historique des paiements
        const paymentChart = document.getElementById('paymentChart');
        if (paymentChart) {
            const ctx = paymentChart.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
                    datasets: [{
                        label: 'Paiements',
                        data: [12000, 19000, 3000, 5000, 2000, 30000],
                        borderColor: '#6a11cb',
                        backgroundColor: 'rgba(106, 17, 203, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString() + ' FCFA';
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    function printStudentCard() {
        // Créer une fenêtre d'impression avec les données de l'étudiant
        const printWindow = window.open('', '_blank');
        const studentName = document.querySelector('.profile-info h2').textContent;
        const studentMatricule = document.querySelector('.matricule').textContent;
        
        printWindow.document.write(`
            <html>
                <head>
                    <title>Fiche Étudiant - ${studentName}</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            padding: 30px;
                            max-width: 800px;
                            margin: 0 auto;
                        }
                        .header {
                            text-align: center;
                            margin-bottom: 30px;
                            border-bottom: 2px solid #6a11cb;
                            padding-bottom: 20px;
                        }
                        .header h1 {
                            color: #6a11cb;
                            margin-bottom: 5px;
                        }
                        .info-grid {
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 20px;
                            margin-bottom: 30px;
                        }
                        .info-section {
                            margin-bottom: 20px;
                            page-break-inside: avoid;
                        }
                        .info-section h3 {
                            background: #f8f9fa;
                            padding: 10px;
                            border-left: 4px solid #6a11cb;
                            margin-bottom: 15px;
                        }
                        .info-row {
                            display: flex;
                            justify-content: space-between;
                            padding: 8px 0;
                            border-bottom: 1px solid #eee;
                        }
                        .label {
                            font-weight: 600;
                            color: #666;
                        }
                        .value {
                            color: #333;
                        }
                        @media print {
                            body {
                                padding: 20px;
                            }
                            .no-print {
                                display: none;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Fiche Étudiant</h1>
                        <h2>${studentName}</h2>
                        <p>Matricule: ${studentMatricule}</p>
                        <p>Date d'impression: ${new Date().toLocaleDateString('fr-FR')}</p>
                    </div>
                    
                    <!-- Contenu dynamique serait ajouté ici via JS -->
                    <div class="info-section">
                        <h3>Informations personnelles</h3>
                        <!-- Ajouter les infos ici -->
                    </div>
                    
                    <script>
                        window.onload = function() {
                            window.print();
                            setTimeout(() => window.close(), 1000);
                        }
                    </script>
                </body>
            </html>
        `);
        printWindow.document.close();
    }
    
    function exportStudentData() {
        // Exporter les données de l'étudiant en Excel
        const studentName = document.querySelector('.profile-info h2').textContent;
        const matricule = document.querySelector('.matricule').textContent;
        
        // Récupérer les données du DOM
        const data = {
            'Nom': document.querySelector('.profile-info h2').textContent,
            'Matricule': matricule,
            'Email': document.querySelector('.profile-email').textContent,
            'Téléphone': document.querySelector('.info-item:nth-child(4) .info-value').textContent,
            'Filière': document.querySelector('.info-item:nth-child(1) .info-value').textContent,
            'Niveau': document.querySelector('.info-item:nth-child(3) .info-value').textContent,
            'Année académique': document.querySelector('.info-item:nth-child(4) .info-value').textContent,
            'Thème mémoire': document.querySelector('.full-width .info-value').textContent,
            'Date inscription': document.querySelector('.info-item:nth-child(5) .info-value').textContent
        };
        
        // Convertir en CSV (simplifié)
        const csvContent = "data:text/csv;charset=utf-8," 
            + Object.keys(data).join(",") + "\n"
            + Object.values(data).join(",");
        
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `etudiant_${matricule}_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    function updateLastSeen() {
        // Mettre à jour la dernière consultation (stockage local)
        const studentId = window.location.pathname.split('/').filter(Boolean).pop();
        if (studentId) {
            const lastSeen = {
                id: studentId,
                name: document.querySelector('.profile-info h2').textContent,
                time: new Date().toISOString()
            };
            localStorage.setItem(`student_${studentId}_last_seen`, JSON.stringify(lastSeen));
        }
    }
    
    // Fonction pour afficher une notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Fermer la notification
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        });
        
        // Auto-fermeture après 5 secondes
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
    }
    
    // Ajouter le CSS pour les notifications
    const notificationStyle = document.createElement('style');
    notificationStyle.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow);
            transform: translateX(100px);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
            max-width: 400px;
        }
        
        .notification.show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .notification-success {
            border-left: 4px solid #27ae60;
        }
        
        .notification-info {
            border-left: 4px solid #3498db;
        }
        
        .notification-warning {
            border-left: 4px solid #f39c12;
        }
        
        .notification-error {
            border-left: 4px solid #e74c3c;
        }
        
        .notification i {
            font-size: 20px;
        }
        
        .notification-success i {
            color: #27ae60;
        }
        
        .notification-info i {
            color: #3498db;
        }
        
        .notification-warning i {
            color: #f39c12;
        }
        
        .notification-error i {
            color: #e74c3c;
        }
        
        .notification span {
            color: var(--text-color);
            flex: 1;
        }
        
        .notification-close {
            background: none;
            border: none;
            color: var(--text-light);
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .notification-close:hover {
            color: var(--text-color);
        }
    `;
    document.head.appendChild(notificationStyle);
});