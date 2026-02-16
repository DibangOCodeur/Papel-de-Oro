// etudiant_form.js - Version corrigée selon votre logique
document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('studentForm')) {
        return;
    }

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
    const form = document.getElementById('studentForm');
    const tabs = document.querySelectorAll('.form-tab');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitOptions = document.getElementById('submitOptions');
    const steps = document.querySelectorAll('.step');
    const stepIndicator = document.querySelector('.form-step');
    const themeTextarea = document.getElementById('theme_memoire');
    const charCount = document.getElementById('themeCharCount');
    const pdfInput = document.getElementById('support_pdf');
    const pdfPreview = document.getElementById('pdfPreview');
    
    // Champs de paiement
    const fraisImpressionInput = document.getElementById('frais_impression');
    const commissionInput = document.getElementById('commission');
    const serviceAnnexeCheckbox = document.getElementById('service_annexe');
    const intituleAnnexeSelect = document.getElementById('intitule_annexes');
    const fraisAnnexeDisplay = document.getElementById('frais_annexe_display');
    const fraisAnnexeHidden = document.getElementById('frais_annexe');
    const jeuReductionCheckbox = document.getElementById('jeu_reduction');
    
    // Résumé
    const summaryElements = {
        frais_impression: document.getElementById('summary_frais_impression'),
        commission: document.getElementById('summary_commission'),
        annexe: document.getElementById('summary_annexe'),
        total: document.getElementById('summary_total'),
        reduction: document.getElementById('summary_reduction'),
    };

    // Prix des services annexes
    const PRIX_ANNEXE = {
        'PAGE_DE_GARDE': 1000,
        'MISE_EN_FORME': 4000,
        'COMPLET': 5000
    };

    // État
    let currentStep = 1;
    
    // Initialisation
    initForm();
    
    function initForm() {
        if (!form || !nextBtn || !prevBtn) {
            return;
        }
        
        showStep(1);
        updateFormStep();
        setupEventListeners();
        updateCalculations();
        updatePreview();
        initFromExistingData();
    }
    
    function initFromExistingData() {
        if (themeTextarea && charCount) {
            updateCharCount();
        }
        
        if (serviceAnnexeCheckbox && serviceAnnexeCheckbox.checked) {
            toggleAnnexeFields(true);
        }
        
        if (intituleAnnexeSelect && intituleAnnexeSelect.value) {
            updateAnnexeFrais();
        }
    }
    
    function setupEventListeners() {
        // Navigation par onglets
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const targetTab = this.dataset.tab;
                const step = targetTab === 'personal' ? 1 : 
                            targetTab === 'academic' ? 2 : 3;
                if (validateCurrentStep()) {
                    showStep(step);
                } else {
                    showValidationError();
                }
            });
        });
        
        // Navigation par étapes
        nextBtn.addEventListener('click', nextStep);
        prevBtn.addEventListener('click', prevStep);
        
        // Compteur de caractères
        if (themeTextarea && charCount) {
            themeTextarea.addEventListener('input', updateCharCount);
        }
        
        // Service annexe
        if (serviceAnnexeCheckbox) {
            serviceAnnexeCheckbox.addEventListener('change', function() {
                toggleAnnexeFields(this.checked);
                updateCalculations();
                updatePreview();
            });
        }
        
        // Type de service annexe
        if (intituleAnnexeSelect) {
            intituleAnnexeSelect.addEventListener('change', function() {
                updateAnnexeFrais();
                updateCalculations();
                updatePreview();
            });
        }
        
        // Jeu de réduction
        if (jeuReductionCheckbox) {
            jeuReductionCheckbox.addEventListener('change', function() {
                updateCalculations();
                updatePreview();
            });
        }
        
        // Calculs automatiques
        [fraisImpressionInput, commissionInput].forEach(input => {
            if (input) {
                input.addEventListener('input', function() {
                    updateCalculations();
                    updatePreview();
                });
            }
        });
        
        // Soumission
        form.addEventListener('submit', handleSubmit);
        
        // Mise à jour de l'aperçu
        form.addEventListener('input', updatePreview);
        form.addEventListener('change', updatePreview);
    }
    
    function toggleAnnexeFields(show) {
        const annexeTypeGroup = document.getElementById('annexe_type_group');
        const fraisAnnexeGroup = document.getElementById('frais_annexe_group');
        
        if (annexeTypeGroup) {
            annexeTypeGroup.style.display = show ? 'block' : 'none';
        }
        if (fraisAnnexeGroup) {
            fraisAnnexeGroup.style.display = show ? 'block' : 'none';
        }
        
        if (!show && intituleAnnexeSelect) {
            intituleAnnexeSelect.value = '';
        }
        
        updateAnnexeFrais();
    }
    
    function updateAnnexeFrais() {
        const serviceAnnexeActive = serviceAnnexeCheckbox && serviceAnnexeCheckbox.checked;
        const typeAnnexe = intituleAnnexeSelect ? intituleAnnexeSelect.value : '';
        
        if (serviceAnnexeActive && typeAnnexe && PRIX_ANNEXE[typeAnnexe]) {
            const frais = PRIX_ANNEXE[typeAnnexe];
            fraisAnnexeDisplay.value = frais;
            fraisAnnexeHidden.value = frais;
        } else {
            fraisAnnexeDisplay.value = 0;
            fraisAnnexeHidden.value = 0;
        }
    }
    
    function showStep(step) {
        currentStep = step;
        
        // Masquer tous les contenus
        document.querySelectorAll('.form-step-content').forEach(content => {
            content.classList.remove('active');
            content.style.display = 'none';
        });
        
        // Désactiver tous les onglets
        tabs.forEach(tab => tab.classList.remove('active'));
        
        // Afficher le contenu de l'étape
        const stepContent = document.getElementById(getStepTabId(step) + '-tab');
        const activeTab = document.querySelector(`.form-tab[data-tab="${getStepTabId(step)}"]`);
        
        if (stepContent) {
            stepContent.classList.add('active');
            stepContent.style.display = 'block';
        }
        
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        updateFormStep();
    }
    
    function getStepTabId(step) {
        switch(step) {
            case 1: return 'personal';
            case 2: return 'academic';
            case 3: return 'payment';
            default: return 'personal';
        }
    }
    
    function updateFormStep() {
        // Mettre à jour l'indicateur
        if (stepIndicator) {
            stepIndicator.textContent = `Étape ${currentStep}/3`;
        }
        
        // Mettre à jour les indicateurs visuels
        steps.forEach((step, index) => {
            if (index + 1 <= currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        // Mettre à jour les boutons
        if (prevBtn) {
            prevBtn.style.display = currentStep > 1 ? 'flex' : 'none';
        }
        
        if (nextBtn && submitOptions) {
            if (currentStep === 3) {
                nextBtn.style.display = 'none';
                submitOptions.style.display = 'flex';
            } else {
                nextBtn.style.display = 'flex';
                submitOptions.style.display = 'none';
            }
        }
    }
    
    function nextStep() {
        if (validateCurrentStep()) {
            if (currentStep < 3) {
                showStep(currentStep + 1);
            }
        } else {
            showValidationError();
        }
    }
    
    function prevStep() {
        if (currentStep > 1) {
            showStep(currentStep - 1);
        }
    }
    
    function validateCurrentStep() {
        const currentContent = document.querySelector('.form-step-content.active');
        const requiredInputs = currentContent.querySelectorAll('input[required], select[required], textarea[required]');
        
        let isValid = true;
        
        // Types de documents acceptés (simples)
        const acceptedDocumentTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.oasis.opendocument.text', // ODT
            'text/plain' // TXT
        ];
        
        requiredInputs.forEach(input => {
            input.classList.remove('input-error');
            
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('input-error');
            } else if (input.type === 'email') {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value.trim())) {
                    isValid = false;
                    input.classList.add('input-error');
                }
            } else if (input.name === 'contact') {
                const phoneRegex = /^[0-9\s\+\-]{10,15}$/;
                if (!phoneRegex.test(input.value.trim())) {
                    isValid = false;
                    input.classList.add('input-error');
                }
            } else if (input.type === 'file') {
                if (!input.files || input.files.length === 0) {
                    isValid = false;
                    input.classList.add('input-error');
                    alert('Veuillez sélectionner un fichier');
                } else {
                    const file = input.files[0];
                    
                    // Vérifier si c'est un type de document accepté
                    const isValidDocument = acceptedDocumentTypes.includes(file.type) || 
                                        file.name.toLowerCase().endsWith('.pdf') ||
                                        file.name.toLowerCase().endsWith('.doc') ||
                                        file.name.toLowerCase().endsWith('.docx') ||
                                        file.name.toLowerCase().endsWith('.odt') ||
                                        file.name.toLowerCase().endsWith('.txt');
                    
                    if (!isValidDocument) {
                        isValid = false;
                        input.classList.add('input-error');
                        alert('Veuillez sélectionner un document valide (PDF, DOC, DOCX, ODT, TXT)');
                    }
                    
                    // Taille maximum : 50MB
                    if (file.size > 50 * 1024 * 1024) {
                        isValid = false;
                        input.classList.add('input-error');
                        alert('Le fichier ne doit pas dépasser 50MB');
                    }
                }
            }
        });
        
        return isValid;
    }
    
    function showValidationError() {
        const currentContent = document.querySelector('.form-step-content.active');
        const firstError = currentContent.querySelector('.input-error');
        
        if (firstError) {
            firstError.focus();
        }
        
        currentContent.style.animation = 'none';
        setTimeout(() => {
            currentContent.style.animation = 'inputShake 0.5s ease';
        }, 10);
    }
    
    function updateCharCount() {
        if (themeTextarea && charCount) {
            const length = themeTextarea.value.length;
            charCount.textContent = length;
            
            if (length > 500) {
                themeTextarea.value = themeTextarea.value.substring(0, 500);
                charCount.textContent = 500;
            }
            
            if (length > 450) {
                charCount.style.color = '#e74c3c';
            } else if (length > 400) {
                charCount.style.color = '#f39c12';
            } else {
                charCount.style.color = 'var(--primary-color)';
            }
        }
    }
    
    function updateCalculations() {
        // Récupérer les valeurs
        const fraisImpression = parseFloat(fraisImpressionInput?.value) || 0;
        const commission = parseFloat(commissionInput?.value) || 0;
        const serviceAnnexeActive = serviceAnnexeCheckbox && serviceAnnexeCheckbox.checked;
        const typeAnnexe = intituleAnnexeSelect ? intituleAnnexeSelect.value : '';
        const jeuReduction = jeuReductionCheckbox && jeuReductionCheckbox.checked;
        
        // Calculer les frais annexes
        let fraisAnnexe = 0;
        if (serviceAnnexeActive && typeAnnexe && PRIX_ANNEXE[typeAnnexe]) {
            fraisAnnexe = PRIX_ANNEXE[typeAnnexe];
        }
        
        // Calculer le montant total (sans commission)
        let montantTotal = fraisImpression + fraisAnnexe;
        
        // Mettre à jour le résumé
        if (summaryElements.frais_impression) {
            summaryElements.frais_impression.textContent = formatCurrency(fraisImpression);
            summaryElements.commission.textContent = formatCurrency(commission);
            summaryElements.annexe.textContent = formatCurrency(fraisAnnexe);
            summaryElements.total.textContent = formatCurrency(fraisImpression + fraisAnnexe);
            
        }
        
        // Mettre à jour les champs cachés
        if (fraisAnnexeHidden) {
            fraisAnnexeHidden.value = fraisAnnexe;
        }
    }
    
    function formatCurrency(amount) {
        return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA';
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function updatePreview() {
        // Nom
        const last_name = document.getElementById('last_name')?.value || 'NOM';
        const first_name = document.getElementById('first_name')?.value || 'Prénom';
        const namePreview = document.getElementById('previewName');
        if (namePreview) namePreview.textContent = `${last_name} ${first_name}`;
        
        // Matricule
        const matricule = document.getElementById('matricule')?.value || 'Non défini';
        const idPreview = document.getElementById('previewId');
        if (idPreview) idPreview.textContent = `Matricule: ${matricule}`;
        
        // Filière
        const filiereSelect = document.getElementById('filiere');
        const filierePreview = document.getElementById('previewFiliere');
        if (filiereSelect && filierePreview) {
            const selectedOption = filiereSelect.options[filiereSelect.selectedIndex];
            filierePreview.textContent = `Filière: ${selectedOption.text || 'Non définie'}`;
        }
        
        // Source de paiement
        const sourceSelect = document.getElementById('source');
        const sourcePreview = document.getElementById('previewSource');
        if (sourceSelect && sourcePreview) {
            const selectedOption = sourceSelect.options[sourceSelect.selectedIndex];
            sourcePreview.textContent = selectedOption.text || '-';
        }
        
        // Calculs pour l'aperçu des montants
        const fraisImpression = parseFloat(fraisImpressionInput?.value) || 0;
        const commission = parseFloat(commissionInput?.value) || 0;
        const serviceAnnexeActive = serviceAnnexeCheckbox && serviceAnnexeCheckbox.checked;
        const typeAnnexe = intituleAnnexeSelect ? intituleAnnexeSelect.value : '';
        const jeuReduction = jeuReductionCheckbox && jeuReductionCheckbox.checked;
        
        // Calculer les frais annexes
        let fraisAnnexe = 0;
        if (serviceAnnexeActive && typeAnnexe && PRIX_ANNEXE[typeAnnexe]) {
            fraisAnnexe = PRIX_ANNEXE[typeAnnexe];
        }
        
        // Calculer le montant total (sans commission)
        let montantTotal = fraisImpression + fraisAnnexe;
        
        // Calculer le montant final (avec commission)
        
        // Mettre à jour l'aperçu
        const impressionPreview = document.getElementById('previewImpression');
        const commissionPreview = document.getElementById('previewCommission');
        const servicesPreview = document.getElementById('previewServices');
        const reductionPreview = document.getElementById('previewReduction');
        const totalPreview = document.getElementById('previewTotal');
        
        if (impressionPreview) impressionPreview.textContent = formatCurrency(fraisImpression);
        if (commissionPreview) commissionPreview.textContent = formatCurrency(commission);
        if (servicesPreview) servicesPreview.textContent = formatCurrency(fraisAnnexe);
    }
    
    function handleSubmit(event) {
        event.preventDefault();
        
        if (!validateCurrentStep()) {
            showValidationError();
            return;
        }
        
        // Validation supplémentaire pour les montants
        const fraisImpression = parseFloat(fraisImpressionInput?.value) || 0;
        if (fraisImpression <= 0) {
            alert('Le frais d\'impression doit être supérieur à 0');
            if (fraisImpressionInput) {
                fraisImpressionInput.focus();
                fraisImpressionInput.classList.add('input-error');
            }
            return;
        }
        
        // Désactiver les boutons pendant le traitement
        const submitButtons = form.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(btn => {
            btn.disabled = true;
            if (btn.name === 'imprimer_reçu') {
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement & Impression...';
            } else {
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement...';
            }
        });
        
        // Soumettre le formulaire
        form.submit();
    }
    
    // Initialisation finale
    setTimeout(() => {
        updateCalculations();
        updatePreview();
    }, 500);
});