// recu.js - Gestion du reçu d'inscription collaborateur
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation
    initReceipt();
    
    function initReceipt() {
        setupEventListeners();
        animateReceipt();
        checkPrintMode();
        detectColorMode();
    }
    
    function setupEventListeners() {
        // Gestion de l'impression
        window.addEventListener('beforeprint', function() {
            prepareForPrint();
        });
        
        window.addEventListener('afterprint', function() {
            restoreAfterPrint();
        });
        
        // Animation au chargement
        setTimeout(() => {
            document.querySelector('.receipt-card')?.classList.add('loaded');
        }, 100);
        
        // Empêcher le mélange avec le dashboard
        preventDashboardOverlap();
    }
    
    function preventDashboardOverlap() {
        // S'assurer que le reçu est au-dessus de tout
        const receiptCard = document.querySelector('.receipt-card');
        if (receiptCard) {
            receiptCard.style.position = 'relative';
            receiptCard.style.zIndex = '1000';
        }
        
        // Désactiver les interactions avec le dashboard
        document.body.style.overflow = 'auto';
    }
    
    function detectColorMode() {
        // Détecter si le mode sombre est activé
        const isDarkMode = document.body.classList.contains('dark-mode') || 
                          window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Ajuster le QR code si nécessaire
        const qrImage = document.querySelector('.qr-code-image');
        if (qrImage && isDarkMode) {
            qrImage.style.filter = 'brightness(0.9)';
        }
    }
    
    function animateReceipt() {
        const receiptCard = document.querySelector('.receipt-card');
        if (receiptCard) {
            receiptCard.style.opacity = '0';
            receiptCard.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                receiptCard.style.transition = 'all 0.5s ease';
                receiptCard.style.opacity = '1';
                receiptCard.style.transform = 'translateY(0)';
            }, 100);
        }
        
        // Animer les sections une par une
        const sections = document.querySelectorAll('.info-section');
        sections.forEach((section, index) => {
            section.style.opacity = '0';
            section.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                section.style.transition = 'all 0.5s ease';
                section.style.opacity = '1';
                section.style.transform = 'translateX(0)';
            }, 300 + (index * 100));
        });
    }
    
    function prepareForPrint() {
        // Ajouter des classes spécifiques pour l'impression
        document.body.classList.add('printing');
        
        // Forcer le mode clair pour l'impression
        document.documentElement.style.setProperty('--receipt-bg', '#ffffff');
        document.documentElement.style.setProperty('--receipt-text', '#000000');
        document.documentElement.style.setProperty('--receipt-card-bg', '#ffffff');
        document.documentElement.style.setProperty('--receipt-border', '#e0e0e0');
        
        // Ajuster la taille pour tenir sur une page
        adjustForPrint();
    }
    
    function adjustForPrint() {
        const receiptCard = document.querySelector('.receipt-card');
        if (!receiptCard) return;
        
        // Calculer la hauteur et ajuster
        const contentHeight = receiptCard.scrollHeight;
        const pageHeight = 1123; // Hauteur A4 en pixels
        
        if (contentHeight > pageHeight) {
            // Réduire légèrement la taille
            receiptCard.style.fontSize = '10pt';
            receiptCard.style.padding = '15px';
        }
    }
    
    function restoreAfterPrint() {
        document.body.classList.remove('printing');
        
        // Restaurer les couleurs
        document.documentElement.style.removeProperty('--receipt-bg');
        document.documentElement.style.removeProperty('--receipt-text');
        document.documentElement.style.removeProperty('--receipt-card-bg');
        document.documentElement.style.removeProperty('--receipt-border');
        
        // Restaurer la taille
        const receiptCard = document.querySelector('.receipt-card');
        if (receiptCard) {
            receiptCard.style.fontSize = '';
            receiptCard.style.padding = '';
        }
    }
    
    function checkPrintMode() {
        // Vérifier si on est en mode impression
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('print') === 'true') {
            setTimeout(() => {
                window.print();
            }, 500);
        }
    }
    
    // Raccourcis clavier
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            // Ouvrir dans une nouvelle fenêtre pour l'impression
            const printUrl = window.location.href + 
                (window.location.href.includes('?') ? '&' : '?') + 'print=true';
            window.open(printUrl, '_blank');
        }
        
        if (e.key === 'Escape') {
            const backBtn = document.querySelector('.btn-back');
            if (backBtn) {
                backBtn.click();
            }
        }
    });
});