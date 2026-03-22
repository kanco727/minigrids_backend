"""
Test simple - Vérifie que les nouveaux composants fonctionnent

Usage:
    python test_new_features.py
"""

import sys
import os

# Ajouter le chemin de l'app au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Tester les imports"""
    print("[*] Test des imports...")
    try:
        from app.enums import RoleEnum, PermissionEnum, ROLE_PERMISSIONS
        print("  [OK] app/enums.py")
        
        from app.security import hash_password, verify_password, create_access_token, decode_access_token
        print("  [OK] app/security.py")
        
        from app.dependencies import get_current_user, get_admin_user, require_permission
        print("  [OK] app/dependencies.py")
        
        from app.services.email_service import EmailService
        print("  [OK] app/services/email_service.py")
        
        from app.models import Utilisateur
        print("  [OK] app/models/utilisateur.py")
        
        from app.schemas import UtilisateurRead
        print("  [OK] app/schemas/utilisateur.py")
        
        print("\n[SUCCESS] Tous les imports OK!\n")
        return True
    except Exception as e:
        print(f"\n[ERROR] Erreur d'import: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_password_hashing():
    """Tester le hachage de mots de passe"""
    print("[*] Test du hachage de mots de passe...")
    try:
        from app.security import hash_password, verify_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        print(f"  Password: {password}")
        print(f"  Hashed: {hashed[:20]}...")
        
        # Vérifier le mot de passe
        assert verify_password(password, hashed), "Verification du mot de passe echouee"
        assert not verify_password("wrong_password", hashed), "Mauvais mot de passe devrait echouer"
        
        print("  [OK] Hachage et verification OK")
        print()
        return True
    except Exception as e:
        print(f"  [ERROR] Erreur: {e}\n")
        return False

def test_jwt_tokens():
    """Tester les tokens JWT"""
    print("[*] Test des tokens JWT...")
    try:
        from app.security import create_access_token, decode_access_token
        
        # Créer un token
        token = create_access_token(data={"sub": "1"})
        print(f"  Token cree: {token[:20]}...")
        
        # Décoder le token
        payload = decode_access_token(token)
        assert payload is not None, "Decodage du token echoue"
        assert payload.get("sub") == "1", "Subject ne correspond pas"
        
        print(f"  Payload: {payload}")
        print("  [OK] Tokens JWT OK")
        print()
        return True
    except Exception as e:
        print(f"  [ERROR] Erreur: {e}\n")
        return False

def test_enums():
    """Tester les énumérations"""
    print("[*] Test des enumerations...")
    try:
        from app.enums import RoleEnum, PermissionEnum, ROLE_PERMISSIONS
        
        print(f"  Roles disponibles: {[r.value for r in RoleEnum]}")
        print(f"  Permissions disponibles: {len(list(PermissionEnum))} permissions")
        
        # Vérifier les permissions des admin
        admin_permissions = ROLE_PERMISSIONS[RoleEnum.ADMIN]
        print(f"  Admin permissions: {len(admin_permissions)} permissions")
        assert len(admin_permissions) > 0, "Admin devrait avoir des permissions"
        
        # Vérifier les permissions des opérateurs
        operateur_permissions = ROLE_PERMISSIONS[RoleEnum.OPERATEUR]
        print(f"  Operateur permissions: {len(operateur_permissions)} permissions")
        assert len(operateur_permissions) > 0, "Operateur devrait avoir des permissions"
        assert admin_permissions != operateur_permissions, "Admin et operateur devraient avoir des permissions differentes"
        
        print("  [OK] Enumerations OK")
        print()
        return True
    except Exception as e:
        print(f"  [ERROR] Erreur: {e}\n")
        return False

def test_schemas():
    """Tester les schémas Pydantic"""
    print("[*] Test des schemas...")
    try:
        from app.schemas import UtilisateurCreate, UtilisateurRead, UtilisateurLogin
        from app.enums import RoleEnum
        
        # Créer un utilisateur
        user_create = UtilisateurCreate(
            email="test@example.com",
            nom_complet="Test User",
            mot_de_passe="password123",
            role=RoleEnum.TECHNICIEN
        )
        
        print(f"  [OK] UtilisateurCreate: {user_create.email}")
        
        # Lire un utilisateur
        data = {
            "id": 1,
            "email": "test@example.com",
            "nom_complet": "Test User",
            "role": "technicien",
            "actif": True
        }
        user_read = UtilisateurRead(**data)
        print(f"  [OK] UtilisateurRead: {user_read.email}")
        
        # Login
        user_login = UtilisateurLogin(
            id=1,
            email="test@example.com",
            role="technicien",
            actif=True
        )
        print(f"  [OK] UtilisateurLogin: {user_login.email}")
        print()
        return True
    except Exception as e:
        print(f"  [ERROR] Erreur: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("TESTS DES NOUVELLES FONCTIONNALITES")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_password_hashing,
        test_jwt_tokens,
        test_enums,
        test_schemas,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"ERREUR dans le test: {e}\n")
            results.append(False)
    
    print("=" * 60)
    print("RESULTATS")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"[OK] {passed}/{total} tests reussis")
    
    if passed == total:
        print("\n*** Tous les tests sont passes! Lapplication est prete.")
    else:
        print(f"\n*** {total - passed} test(s) echoue(s).")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
