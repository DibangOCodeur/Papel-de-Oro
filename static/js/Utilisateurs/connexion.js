// script.js - Gestion de la page de connexion (version corrigée)
document.addEventListener('DOMContentLoaded', function() {
    // Éléments DOM
    const loginForm = document.getElementById('loginForm');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    
    // Gestion du mode clair/sombre
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            
            // Sauvegarder la préférence dans localStorage
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
    
    // Afficher/masquer le mot de passe
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Changer l'icône
            const icon = togglePasswordBtn.querySelector('i');
            if (type === 'password') {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
            
            // Ajouter une animation
            togglePasswordBtn.style.transform = 'scale(1.1)';
            setTimeout(() => {
                togglePasswordBtn.style.transform = 'scale(1)';
            }, 200);
        });
    }
    
    // Gestion de la soumission du formulaire de connexion
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // VALIDATION CLIENT AVANT SOUMISSION
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            
            // Validation
            let isValid = true;
            
            // Réinitialiser les erreurs
            document.querySelectorAll('.input-error').forEach(el => {
                el.classList.remove('input-error');
            });
            
            // Validation email
            if (!email.value || !isValidEmail(email.value)) {
                email.classList.add('input-error');
                isValid = false;
            }
            
            // Validation mot de passe
            if (!password.value || password.value.length < 6) {
                password.classList.add('input-error');
                isValid = false;
            }
            
            if (!isValid) {
                // Animation de secousse pour le formulaire
                loginForm.style.animation = 'inputShake 0.5s ease';
                setTimeout(() => {
                    loginForm.style.animation = '';
                }, 500);
                
                e.preventDefault(); // Empêche la soumission si invalide
                return;
            }
            
            // Si validation réussie, laisser Django gérer la soumission
            // On peut ajouter une animation de chargement sans empêcher la soumission
            const submitBtn = loginForm.querySelector('.btn-login');
            const originalHTML = submitBtn.innerHTML;
            
            // Afficher l'animation de chargement
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span class="btn-text">Connexion en cours...</span>';
            submitBtn.disabled = true;
            
            // La soumission se fera normalement via Django
            // Pas besoin de setTimeout car Django va rediriger
            
            // Réinitialiser le bouton après 3 secondes au cas où la requête échouerait
            // (ce sera écrasé par le rechargement de la page si la connexion réussit)
            setTimeout(() => {
                submitBtn.innerHTML = originalHTML;
                submitBtn.disabled = false;
            }, 3000);
        });
    }
    
    // Fonction de validation d'email
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Animation au focus des inputs
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
        });
    });
    
    // Animation des statistiques au survol
    const stats = document.querySelectorAll('.stat');
    stats.forEach(stat => {
        stat.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.05)';
        });
        
        stat.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Animation des features au survol
    const features = document.querySelectorAll('.feature');
    features.forEach(feature => {
        feature.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px)';
        });
        
        feature.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
    
    // Effet parallaxe léger sur les cercles d'arrière-plan
    document.addEventListener('mousemove', function(e) {
        const circles = document.querySelectorAll('.circle');
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        circles.forEach((circle, index) => {
            const speed = (index + 1) * 0.3;
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
    document.querySelectorAll('.feature, .stat, .form-group').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Animation de la section logo
    const logoSection = document.querySelector('.logo-section');
    if (logoSection) {
        logoSection.style.opacity = '0';
        logoSection.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            logoSection.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            logoSection.style.opacity = '1';
            logoSection.style.transform = 'translateX(0)';
        }, 300);
    }
    
    // Animation de la section formulaire
    const formSection = document.querySelector('.form-section');
    if (formSection) {
        formSection.style.opacity = '0';
        formSection.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            formSection.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            formSection.style.opacity = '1';
            formSection.style.transform = 'translateX(0)';
        }, 500);
    }
});