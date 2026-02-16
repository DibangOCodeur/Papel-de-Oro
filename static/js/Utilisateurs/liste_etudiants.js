// liste_etudiants.js - Version adaptée pour Django
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation de la page liste des étudiants...');

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
    const studentsTableBody = document.getElementById('studentsTableBody');
    const selectAllCheckbox = document.getElementById('selectAll');
    const selectionSummary = document.getElementById('selectionSummary');
    const selectedCount = document.getElementById('selectedCount');
    const deselectAllBtn = document.getElementById('deselectAll');
    const sendBulkEmailBtn = document.getElementById('sendBulkEmail');
    const exportExcelBtn = document.getElementById('exportExcel');
    const exportSelectedBtn = document.getElementById('exportSelected');
    const exportPDFBtn = document.getElementById('exportPDF');
    const exportPrintBtn = document.getElementById('exportPrint');

    // Initialisation
    initStudentsPage();

    function initStudentsPage() {
        setupEventListeners();
        updateSelectionSummary();
    }

    function setupEventListeners() {
        // Sélection
        selectAllCheckbox.addEventListener('change', toggleSelectAll);
        deselectAllBtn.addEventListener('click', deselectAll);

        // Export
        exportExcelBtn.addEventListener('click', exportToExcel);
        exportPDFBtn.addEventListener('click', exportToPDF);
        exportPrintBtn.addEventListener('click', printTable);
        exportSelectedBtn.addEventListener('click', exportSelectedToExcel);

        // Email
        sendBulkEmailBtn.addEventListener('click', sendBulkEmail);

        // Fermer les modals
        document.querySelectorAll('.modal-close, .modal-close-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const modal = this.closest('.modal');
                if (modal) modal.classList.remove('active');
            });
        });

        // Fermer modals en cliquant à l'extérieur
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    this.classList.remove('active');
                }
            });
        });

        // Boutons du modal détails
        document.getElementById('printStudentCard')?.addEventListener('click', printStudentCard);
    }

    // Sélection
    function toggleSelectAll() {
        const isChecked = selectAllCheckbox.checked;
        const checkboxes = document.querySelectorAll('.student-checkbox');
        const selectedIds = [];
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            const studentId = parseInt(checkbox.dataset.id);
            
            if (isChecked) {
                selectedIds.push(studentId);
            }
        });
        
        // Stocker les IDs sélectionnés
        localStorage.setItem('selectedStudents', JSON.stringify(isChecked ? selectedIds : []));
        updateSelectionSummary();
    }

    function deselectAll() {
        selectedStudents.clear();
        selectAllCheckbox.checked = false;
        document.querySelectorAll('.student-checkbox').forEach(cb => cb.checked = false);
        localStorage.removeItem('selectedStudents');
        updateSelectionSummary();
    }

    function updateSelectionSummary() {
        const checkboxes = document.querySelectorAll('.student-checkbox:checked');
        const count = checkboxes.length;
        
        if (count > 0) {
            selectionSummary.style.display = 'block';
            selectedCount.textContent = count;
            
            // Stocker les IDs sélectionnés
            const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));
            localStorage.setItem('selectedStudents', JSON.stringify(selectedIds));
        } else {
            selectionSummary.style.display = 'none';
            localStorage.removeItem('selectedStudents');
        }
    }

    // Export Excel
    async function exportToExcel() {
        try {
            const response = await fetch('/etudiants/export/excel/');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `liste_etudiants_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showExportSuccess('Excel');
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'export Excel');
        }
    }

    async function exportSelectedToExcel() {
        const checkboxes = document.querySelectorAll('.student-checkbox:checked');
        if (checkboxes.length === 0) {
            alert('Veuillez sélectionner au moins un étudiant à exporter.');
            return;
        }

        const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));
        
        try {
            const response = await fetch('/etudiants/export/excel/selection/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ student_ids: selectedIds })
            });
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `etudiants_selectionnes_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showExportSuccess('Excel');
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'export des étudiants sélectionnés');
        }
    }

    // Export PDF
    function exportToPDF() {
        alert('Export PDF en cours de développement...');
        // Implémentation avec jsPDF
    }

    // Impression
    function printTable() {
        window.print();
    }

    // Email groupé
    function sendBulkEmail() {
        const checkboxes = document.querySelectorAll('.student-checkbox:checked');
        if (checkboxes.length === 0) {
            alert('Veuillez sélectionner au moins un étudiant.');
            return;
        }

        const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));
        
        // Rediriger vers la page d'envoi d'emails avec les IDs sélectionnés
        const url = `/email/envoi-multiple/?ids=${selectedIds.join(',')}`;
        window.location.href = url;
    }

    function printStudentCard() {
        alert('Impression de la fiche étudiante...');
        // Implémentation réelle avec jsPDF
    }

    // Utilitaires
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
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Ajouter le CSS pour la notification
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
        }
        
        .export-notification.show {
            transform: translateY(0);
            opacity: 1;
        }
        
        .export-notification i {
            color: #27ae60;
            font-size: 20px;
        }
        
        .export-notification span {
            color: var(--text-color);
            font-weight: 500;
        }
    `;
    document.head.appendChild(notificationStyle);
});