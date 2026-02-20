// inscription.js - Gestion du formulaire d'inscription des collaborateurs
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier qu'on est sur la bonne page
    if (!document.getElementById('collaborateurForm')) {
        return;
    }

    // Supprimer la scrollbar globale pour un design plus propre
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
        
        /* Conteneurs qui ont besoin de défilement */
        .form-panel,
        .summary-panel,
        .register-section {
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
            max-height: calc(100vh - 100px);
        }
        
        .form-panel::-webkit-scrollbar,
        .summary-panel::-webkit-scrollbar,
        .register-section::-webkit-scrollbar {
            display: none !important;
        }
        
        /* Empêcher le défilement du body */
        .form-panel,
        .summary-panel {
            overscroll-behavior: contain;
        }
    `;
    document.head.appendChild(style);

    // Éléments DOM
    const form = document.getElementById('collaborateurForm');
    const submitBtn = document.getElementById('submitBtn');
    const resetBtn = document.getElementById('resetBtn');
    const copyBtn = document.querySelector('.copy-btn');
    
    // Champs du formulaire
    const lastNameInput = document.getElementById('id_last_name');
    const firstNameInput = document.getElementById('id_first_name');
    const emailInput = document.getElementById('id_email');
    const contactInput = document.getElementById('id_contact');
    
    // Éléments de prévisualisation
    const previewName = document.getElementById('previewName');
    const previewEmail = document.getElementById('previewEmail');
    const previewContact = document.getElementById('previewContact');
    const previewMatricule = document.getElementById('previewMatricule');
    const previewCode = document.getElementById('previewCode');
    const previewDate = document.getElementById('previewDate');
    
    // État du formulaire
    let formSubmitted = false;
    
    // Initialisation
    initForm();
    
    function initForm() {
        if (!form) return;
        
        setupEventListeners();
        updatePreview();
        generateRandomValues();
        initInputMasks();
        checkExistingData();
    }
    
    function setupEventListeners() {
        // Mise à jour en temps réel de l'aperçu
        if (lastNameInput) {
            lastNameInput.addEventListener('input', updatePreview);
            lastNameInput.addEventListener('blur', validateField);
        }
        
        if (firstNameInput) {
            firstNameInput.addEventListener('input', updatePreview);
            firstNameInput.addEventListener('blur', validateField);
        }
        
        if (emailInput) {
            emailInput.addEventListener('input', updatePreview);
            emailInput.addEventListener('blur', validateField);
        }
        
        if (contactInput) {
            contactInput.addEventListener('input', function(e) {
                formatPhoneNumber(e);
                updatePreview();
            });
            contactInput.addEventListener('blur', validateField);
        }
        
        // Validation à la saisie
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('input', function() {
                removeError(this);
            });
        });
        
        // Soumission du formulaire
        if (form) {
            form.addEventListener('submit', handleSubmit);
        }
        
        // Réinitialisation
        if (resetBtn) {
            resetBtn.addEventListener('click', handleReset);
        }
        
        // Copie du mot de passe
        if (copyBtn) {
            copyBtn.addEventListener('click', copyPassword);
        }
        
        // Gestion des touches
        document.addEventListener('keydown', function(e) {
            // Ctrl+Enter pour soumettre
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                if (!formSubmitted) {
                    formSubmitted = true;
                    form.dispatchEvent(new Event('submit'));
                }
            }
            
            // Échap pour réinitialiser (avec confirmation)
            if (e.key === 'Escape' && !e.ctrlKey && !e.altKey && !e.shiftKey) {
                e.preventDefault();
                if (hasUnsavedChanges()) {
                    showConfirmDialog(
                        'Réinitialiser le formulaire ?',
                        'Toutes les modifications non enregistrées seront perdues.',
                        handleReset
                    );
                } else {
                    handleReset();
                }
            }
        });
    }
    
    function initInputMasks() {
        // Masque pour le téléphone (format français)
        if (contactInput) {
            contactInput.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 0) {
                    if (value.length <= 2) {
                        value = value;
                    } else if (value.length <= 4) {
                        value = value.slice(0,2) + ' ' + value.slice(2);
                    } else if (value.length <= 6) {
                        value = value.slice(0,2) + ' ' + value.slice(2,4) + ' ' + value.slice(4);
                    } else if (value.length <= 8) {
                        value = value.slice(0,2) + ' ' + value.slice(2,4) + ' ' + value.slice(4,6) + ' ' + value.slice(6);
                    } else {
                        value = value.slice(0,2) + ' ' + value.slice(2,4) + ' ' + value.slice(4,6) + ' ' + value.slice(6,8) + ' ' + value.slice(8,10);
                    }
                }
                e.target.value = value;
            });
        }
    }
    
    function formatPhoneNumber(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 10) {
            value = value.slice(0, 10);
        }
        
        if (value.length >= 6) {
            value = value.slice(0,2) + ' ' + value.slice(2,4) + ' ' + value.slice(4,6) + ' ' + value.slice(6);
        } else if (value.length >= 4) {
            value = value.slice(0,2) + ' ' + value.slice(2,4) + ' ' + value.slice(4);
        } else if (value.length >= 2) {
            value = value.slice(0,2) + ' ' + value.slice(2);
        }
        
        e.target.value = value;
    }
    
    function generateRandomValues() {
        // Générer un matricule aléatoire pour l'aperçu
        if (previewMatricule) {
            const year = new Date().getFullYear();
            const random = Math.floor(Math.random() * 900 + 100);
            previewMatricule.textContent = `COL${year}${random}`;
        }
        
        // Générer un code de parrainage aléatoire pour l'aperçu
        if (previewCode) {
            const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
            let code = 'DBG';
            for (let i = 0; i < 5; i++) {
                code += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            previewCode.textContent = code;
        }
    }
    
    function updatePreview() {
        // Mettre à jour le nom complet
        if (previewName) {
            const lastName = lastNameInput ? (lastNameInput.value || 'NOM').toUpperCase() : 'NOM';
            const firstName = firstNameInput ? (firstNameInput.value || 'Prénom') : 'Prénom';
            previewName.textContent = `${lastName} ${firstName}`;
        }
        
        // Mettre à jour l'email
        if (previewEmail) {
            previewEmail.textContent = emailInput && emailInput.value ? emailInput.value : 'email@exemple.com';
        }
        
        // Mettre à jour le téléphone
        if (previewContact) {
            previewContact.textContent = contactInput && contactInput.value ? contactInput.value : 'Téléphone';
        }
        
        // Animer la carte d'aperçu
        const previewCard = document.getElementById('previewCard');
        if (previewCard) {
            previewCard.style.animation = 'none';
            setTimeout(() => {
                previewCard.style.animation = 'pulse 0.3s ease';
            }, 10);
        }
    }
    
    function validateField(e) {
        const field = e.target;
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Réinitialiser les erreurs
        removeError(field);
        
        // Validation selon le champ
        if (field === lastNameInput || field === firstNameInput) {
            if (value.length < 2) {
                isValid = false;
                errorMessage = 'Ce champ doit contenir au moins 2 caractères';
            } else if (value.length > 50) {
                isValid = false;
                errorMessage = 'Ce champ ne peut pas dépasser 50 caractères';
            } else if (!/^[a-zA-ZÀ-ÿ\s\-']+$/.test(value)) {
                isValid = false;
                errorMessage = 'Ce champ ne peut contenir que des lettres';
            }
        }
        
        if (field === emailInput) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Veuillez entrer une adresse email valide';
            }
        }
        
        if (field === contactInput && value) {
            const phoneRegex = /^(\+?[0-9]{1,3}[\s\-]?)?[0-9]{2}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = 'Format de téléphone invalide';
            }
        }
        
        if (!isValid && value) {
            showFieldError(field, errorMessage);
        }
        
        return isValid || !value; // Les champs optionnels sont valides même vides
    }
    
    function showFieldError(field, message) {
        field.classList.add('input-error');
        
        // Chercher ou créer le conteneur d'erreur
        let errorContainer = field.parentElement.parentElement.querySelector('.errorlist');
        if (!errorContainer) {
            errorContainer = document.createElement('ul');
            errorContainer.className = 'errorlist';
            field.parentElement.parentElement.appendChild(errorContainer);
        }
        
        errorContainer.innerHTML = `<li>${message}</li>`;
    }
    
    function removeError(field) {
        field.classList.remove('input-error');
        const errorContainer = field.parentElement.parentElement.querySelector('.errorlist');
        if (errorContainer) {
            errorContainer.remove();
        }
    }
    
    function validateForm() {
        let isValid = true;
        
        // Valider chaque champ requis
        if (lastNameInput) {
            lastNameInput.dispatchEvent(new Event('blur'));
            if (lastNameInput.classList.contains('input-error')) isValid = false;
        }
        
        if (firstNameInput) {
            firstNameInput.dispatchEvent(new Event('blur'));
            if (firstNameInput.classList.contains('input-error')) isValid = false;
        }
        
        if (emailInput) {
            emailInput.dispatchEvent(new Event('blur'));
            if (emailInput.classList.contains('input-error')) isValid = false;
        }
        
        if (contactInput && contactInput.value) {
            contactInput.dispatchEvent(new Event('blur'));
            if (contactInput.classList.contains('input-error')) isValid = false;
        }
        
        return isValid;
    }
    
    function hasUnsavedChanges() {
        if (!lastNameInput || !firstNameInput || !emailInput) return false;
        
        return lastNameInput.value || firstNameInput.value || 
               (emailInput.value && emailInput.value !== '') ||
               (contactInput && contactInput.value);
    }
    
    function showConfirmDialog(title, message, onConfirm) {
        // Créer une modale de confirmation simple
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            animation: fadeIn 0.3s ease;
        `;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: var(--card-bg);
            padding: 30px;
            border-radius: 20px;
            max-width: 400px;
            width: 90%;
            box-shadow: var(--box-shadow-hover);
            border: 1px solid var(--border-color);
            animation: slideInDown 0.3s ease;
        `;
        
        modal.innerHTML = `
            <h3 style="margin-bottom: 15px; color: var(--text-color);">${title}</h3>
            <p style="margin-bottom: 25px; color: var(--text-light);">${message}</p>
            <div style="display: flex; gap: 15px; justify-content: flex-end;">
                <button class="btn-reset" style="flex: 0 1 auto; padding: 10px 20px;">Annuler</button>
                <button class="btn-submit" style="flex: 0 1 auto; padding: 10px 20px;">Confirmer</button>
            </div>
        `;
        
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        // Gestion des boutons
        modal.querySelector('.btn-reset').onclick = () => overlay.remove();
        modal.querySelector('.btn-submit').onclick = () => {
            overlay.remove();
            onConfirm();
        };
        
        // Fermer en cliquant sur l'overlay
        overlay.onclick = (e) => {
            if (e.target === overlay) overlay.remove();
        };
    }
    
    function handleSubmit(e) {
        e.preventDefault();
        
        if (formSubmitted) return;
        
        // Désactiver les validations HTML5 par défaut
        form.setAttribute('novalidate', 'novalidate');
        
        // Valider le formulaire
        if (!validateForm()) {
            showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
            
            // Faire défiler jusqu'à la première erreur
            const firstError = form.querySelector('.input-error');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }
        
        // Demander confirmation
        showConfirmDialog(
            'Créer le collaborateur ?',
            'Vérifiez les informations avant de confirmer.',
            () => {
                submitForm();
            }
        );
    }
    
    function submitForm() {
        // Désactiver les boutons
        formSubmitted = true;
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Création en cours...';
        }
        
        // Ajouter la classe loading
        form.classList.add('loading');
        
        // Afficher une notification de chargement
        showNotification('Création du collaborateur en cours...', 'info');
        
        // Soumettre le formulaire
        setTimeout(() => {
            form.submit();
        }, 500);
    }
    
    function handleReset() {
        if (form) {
            form.reset();
            formSubmitted = false;
            
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Créer le collaborateur';
            }
            
            form.classList.remove('loading');
            
            // Réinitialiser les erreurs
            form.querySelectorAll('.input-error').forEach(field => {
                removeError(field);
            });
            
            // Mettre à jour l'aperçu
            updatePreview();
            
            // Générer de nouvelles valeurs aléatoires
            generateRandomValues();
            
            // Afficher une notification
            showNotification('Formulaire réinitialisé', 'success');
        }
    }
    
    function copyPassword() {
        const password = '@papel@';
        
        // Copier dans le presse-papier
        navigator.clipboard.writeText(password).then(() => {
            const copyBtn = document.querySelector('.copy-btn');
            const originalHtml = copyBtn.innerHTML;
            
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            copyBtn.classList.add('copied');
            
            showNotification('Mot de passe copié !', 'success');
            
            setTimeout(() => {
                copyBtn.innerHTML = originalHtml;
                copyBtn.classList.remove('copied');
            }, 2000);
        }).catch(() => {
            showNotification('Erreur lors de la copie', 'error');
        });
    }
    
    function showNotification(message, type = 'info') {
        // Créer la notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideInRight 0.3s ease;
            box-shadow: var(--box-shadow-hover);
        `;
        
        const icon = type === 'success' ? 'fa-check-circle' :
                    type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
        
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 3000);
    }
    
    function checkExistingData() {
        // Vérifier s'il y a des données pré-remplies
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('edit')) {
            showNotification('Mode édition', 'info');
        }
    }
    
    // Ajouter les animations supplémentaires
    const extraStyles = document.createElement('style');
    extraStyles.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .pulse-animation {
            animation: pulse 0.3s ease;
        }
    `;
    document.head.appendChild(extraStyles);
    
    // Initialisation des tooltips
    initTooltips();
    
    function initTooltips() {
        document.querySelectorAll('[title]').forEach(el => {
            el.addEventListener('mouseenter', showTooltip);
            el.addEventListener('mouseleave', hideTooltip);
        });
    }
    
    function showTooltip(e) {
        const el = e.target;
        const title = el.getAttribute('title');
        if (!title) return;
        
        // Créer le tooltip
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
        
        // Positionner le tooltip
        const rect = el.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - 50 + 'px';
        tooltip.style.top = rect.top - 30 + 'px';
        
        document.body.appendChild(tooltip);
        el._tooltip = tooltip;
        
        // Supprimer l'attribut title pour éviter le tooltip natif
        el.setAttribute('data-title', title);
        el.removeAttribute('title');
    }
    
    function hideTooltip(e) {
        const el = e.target;
        if (el._tooltip) {
            el._tooltip.remove();
            el._tooltip = null;
            
            // Restaurer l'attribut title
            const title = el.getAttribute('data-title');
            if (title) {
                el.setAttribute('title', title);
                el.removeAttribute('data-title');
            }
        }
    }
});