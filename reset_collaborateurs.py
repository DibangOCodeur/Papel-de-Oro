# reset_collaborateurs.py
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Memo.settings')  # Remplacez 'Memo' par le nom de votre projet
django.setup()

from Utilisateurs.models import Collaborateur
from Utilisateurs.models import Utilisateur

def reset_all_passwords():
    """Réinitialise tous les mots de passe des collaborateurs à @papel@"""
    print("=" * 60)
    print("RÉINITIALISATION DES MOTS DE PASSE DES COLLABORATEURS")
    print("=" * 60)
    
    # Récupérer tous les collaborateurs
    collaborateurs = Collaborateur.objects.all()
    
    if not collaborateurs:
        print("❌ Aucun collaborateur trouvé dans la base de données.")
        return
    
    print(f"🔍 {collaborateurs.count()} collaborateurs trouvés\n")
    
    count_success = 0
    count_failed = 0
    
    for collab in collaborateurs:
        try:
            # Sauvegarder l'email pour l'affichage
            email = collab.email
            nom = f"{collab.first_name} {collab.last_name}"
            
            # Réinitialiser le mot de passe
            collab.set_password('@papel@')
            collab.save()
            
            # Vérifier que le mot de passe a bien été changé
            if collab.check_password('@papel@'):
                print(f"✅ {email} - {nom} - Mot de passe réinitialisé avec succès")
                count_success += 1
            else:
                print(f"❌ {email} - {nom} - Échec de la réinitialisation")
                count_failed += 1
                
        except Exception as e:
            print(f"❌ Erreur pour {collab.email}: {str(e)}")
            count_failed += 1
    
    print("\n" + "=" * 60)
    print(f"RÉSUMÉ : {count_success} succès, {count_failed} échecs sur {collaborateurs.count()} collaborateurs")
    print("=" * 60)

def create_test_collaborateur():
    """Crée un collaborateur de test si aucun n'existe"""
    print("\n" + "=" * 60)
    print("CRÉATION D'UN COLLABORATEUR DE TEST")
    print("=" * 60)
    
    email = "test.collaborateur@iipea.com"
    
    # Vérifier s'il existe déjà
    if Collaborateur.objects.filter(email=email).exists():
        print(f"⚠️ Le collaborateur {email} existe déjà")
        collab = Collaborateur.objects.get(email=email)
        print(f"📧 Email: {collab.email}")
        print(f"👤 Nom: {collab.first_name} {collab.last_name}")
        print(f"🔑 Le mot de passe actuel est : {'@papel@' if collab.check_password('@papel@') else 'MODIFIÉ'}")
        return
    
    try:
        # Créer le collaborateur
        collaborateur = Collaborateur.objects.create_user(
            email=email,
            first_name="Test",
            last_name="Collaborateur",
            password="@papel@",
            role="collaborateur",
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
        
        print(f"✅ Collaborateur de test créé avec succès !")
        print(f"📧 Email: {collaborateur.email}")
        print(f"👤 Nom: {collaborateur.first_name} {collaborateur.last_name}")
        print(f"🔑 Mot de passe: @papel@")
        
        # Vérification
        if collaborateur.check_password('@papel@'):
            print("✅ Vérification du mot de passe réussie")
        else:
            print("❌ Problème avec le mot de passe")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création: {str(e)}")

def verify_users():
    """Vérifie tous les utilisateurs dans la base"""
    print("\n" + "=" * 60)
    print("VÉRIFICATION DE TOUS LES UTILISATEURS")
    print("=" * 60)
    
    utilisateurs = Utilisateur.objects.all()
    print(f"📊 Total utilisateurs: {utilisateurs.count()}")
    
    for user in utilisateurs:
        print(f"\n--- {user.email} ---")
        print(f"👤 Nom: {user.first_name} {user.last_name}")
        print(f"🎭 Rôle: {user.role}")
        print(f"✅ Actif: {user.is_active}")
        print(f"🔐 A un mot de passe: {'Oui' if user.password else 'Non'}")
        
        # Vérifier les sous-classes
        try:
            if hasattr(user, 'collaborateur'):
                print(f"👥 Type: Collaborateur (ID: {user.collaborateur.id})")
            elif hasattr(user, 'etudiant'):
                print(f"👥 Type: Étudiant (ID: {user.etudiant.id})")
            else:
                print(f"👥 Type: Utilisateur de base")
        except:
            print(f"👥 Type: Utilisateur de base")

if __name__ == "__main__":
    # Exécuter les vérifications
    verify_users()
    reset_all_passwords()
    create_test_collaborateur()
    
    print("\n" + "=" * 60)
    print("🎉 OPÉRATION TERMINÉE")
    print("=" * 60)