// liste.js - Gestion de la liste des collaborateurs
// Version adaptée avec le style de la liste des étudiants

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation de la page liste des collaborateurs...');
    initListeCollaborateurs();
});

function initListeCollaborateurs() {
    // Supprimer la scrollbar globale
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    
    // Ajouter le style pour masquer les scrollbars
    addScrollbarStyles();
    
    // Initialisation des tooltips
    initTooltips();
    
    // Animation des cartes
    animateCards();
    
    // Configuration des exports
    setupExports();
}

function addScrollbarStyles() {
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
        .table-responsive,
        .collaborateurs-grid,
        .modal-content,
        .actions-menu {
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        
        .table-responsive::-webkit-scrollbar,
        .collaborateurs-grid::-webkit-scrollbar,
        .modal-content::-webkit-scrollbar,
        .actions-menu::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
            height: 0 !important;
        }
        
        /* Empêcher le défilement du body quand on scroll dans les conteneurs */
        .table-responsive,
        .modal-content {
            overscroll-behavior: contain;
        }
    `;
    document.head.appendChild(style);
}

function initTooltips() {
    const tooltips = document.querySelectorAll('[title]');
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const el = e.target;
    const title = el.getAttribute('title');
    if (!title) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = title;
    tooltip.style.cssText = `
        position: fixed;
        background: var(--text-color);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 10000;
        pointer-events: none;
        animation: fadeIn 0.2s ease;
    `;
    
    const rect = el.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - 50 + 'px';
    tooltip.style.top = rect.top - 30 + 'px';
    
    document.body.appendChild(tooltip);
    el._tooltip = tooltip;
    
    el.setAttribute('data-title', title);
    el.removeAttribute('title');
}

function hideTooltip(e) {
    const el = e.target;
    if (el._tooltip) {
        el._tooltip.remove();
        el._tooltip = null;
        
        const title = el.getAttribute('data-title');
        if (title) {
            el.setAttribute('title', title);
            el.removeAttribute('data-title');
        }
    }
}

function animateCards() {
    const cards = document.querySelectorAll('.collaborateur-card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

function setupExports() {
    // Export Excel
    const exportExcelBtn = document.getElementById('exportExcel');
    if (exportExcelBtn) {
        exportExcelBtn.addEventListener('click', function() {
            exportToExcel();
        });
    }
    
    // Export PDF
    const exportPDFBtn = document.getElementById('exportPDF');
    if (exportPDFBtn) {
        exportPDFBtn.addEventListener('click', function() {
            exportToPDF();
        });
    }
    
    // Export Print
    const exportPrintBtn = document.getElementById('exportPrint');
    if (exportPrintBtn) {
        exportPrintBtn.addEventListener('click', function() {
            window.print();
        });
    }
}

function exportToExcel() {
    showLoader('Préparation de l\'export Excel...');
    
    fetch('/collaborateurs/export/excel/?' + new URLSearchParams(window.location.search))
        .then(response => {
            if (!response.ok) throw new Error('Erreur réseau');
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `collaborateurs_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showExportSuccess('Excel');
        })
        .catch(error => {
            console.error('Erreur:', error);
            showExportError('Excel');
        })
        .finally(() => {
            hideLoader();
        });
}

function exportToPDF() {
    showLoader('Préparation de l\'export PDF...');
    
    fetch('/collaborateurs/export/pdf/?' + new URLSearchParams(window.location.search))
        .then(response => {
            if (!response.ok) throw new Error('Erreur réseau');
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `collaborateurs_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showExportSuccess('PDF');
        })
        .catch(error => {
            console.error('Erreur:', error);
            showExportError('PDF');
        })
        .finally(() => {
            hideLoader();
        });
}

function showLoader(message = 'Chargement...') {
    const loader = document.createElement('div');
    loader.className = 'export-notification loader-notification';
    loader.id = 'globalLoader';
    loader.innerHTML = `
        <i class="fas fa-spinner fa-spin"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(loader);
    
    setTimeout(() => {
        loader.classList.add('show');
    }, 10);
}

function hideLoader() {
    const loader = document.getElementById('globalLoader');
    if (loader) {
        loader.classList.remove('show');
        setTimeout(() => {
            if (loader.parentNode) {
                document.body.removeChild(loader);
            }
        }, 300);
    }
}

function showExportSuccess(format) {
    const notification = document.createElement('div');
    notification.className = 'export-notification';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>Export ${format} réussi ! Le téléchargement a commencé.</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function showExportError(format) {
    const notification = document.createElement('div');
    notification.className = 'export-notification error';
    notification.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>Erreur lors de l'export ${format}. Veuillez réessayer.</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Ajouter le CSS pour les notifications
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
    .export-notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: var(--shadow);
        transform: translateY(100px);
        opacity: 0;
        transition: all 0.3s ease;
        z-index: 1000;
        min-width: 300px;
    }
    
    .export-notification.show {
        transform: translateY(0);
        opacity: 1;
    }
    
    .export-notification i {
        color: #27ae60;
        font-size: 20px;
    }
    
    .export-notification.error i {
        color: #e74c3c;
    }
    
    .export-notification span {
        color: var(--text-color);
        font-weight: 500;
    }
    
    .loader-notification {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
    }
    
    .loader-notification i {
        color: white;
    }
    
    .loader-notification span {
        color: white;
    }
`;
document.head.appendChild(notificationStyle);

// Fonction pour rafraîchir la liste
function refreshList() {
    location.reload();
}

// Gestionnaire d'erreur global
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('Erreur:', msg, 'à', url, 'ligne', lineNo);
    return false;
};

// Nettoyage à la déconnexion
window.addEventListener('beforeunload', function() {
    // Nettoyer les tooltips
    document.querySelectorAll('.custom-tooltip').forEach(el => el.remove());
    
    // Nettoyer les notifications
    document.querySelectorAll('.export-notification').forEach(el => el.remove());
});