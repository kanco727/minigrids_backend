"""
Script d'initialisation - Crée des utilisateurs de démonstration avec vrais emails

Usage:
    python init_demo_users.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys
import os
from datetime import datetime

# Ajouter le chemin de l'app au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import Utilisateur
from app.security import hash_password
from app.db import DATABASE_URL

# Graines de données d'utilisateurs
DEMO_USERS = [
    {
        "nom": "Admin System",
        "email": "admin@solarpro.com",
        "mot_de_passe": "admin123",
        "role": "admin"
    },
    {
        "nom": "Superviser Principal",
        "email": "superviseur@minigrids.local",
        "mot_de_passe": "superviseur123",
        "role": "superviseur"
    },
    {
        "nom": "Technicien Principal",
        "email": "tech@solarpro.com",
        "mot_de_passe": "tech123",
        "role": "technicien"
    },
    {
        "nom": "Technicien Marie",
        "email": "marie.technicien@minigrids.local",
        "mot_de_passe": "tech123",
        "role": "technicien"
    },
    {
        "nom": "Opérateur Site A",
        "email": "operateur.sitea@minigrids.local",
        "mot_de_passe": "op123",
        "role": "operateur"
    },
    {
        "nom": "Opérateur Site B",
        "email": "operateur.siteb@minigrids.local",
        "mot_de_passe": "op123",
        "role": "operateur"
    },
]

async def main():
    """Crée les utilisateurs de démonstration"""
    
    # Créer le moteur
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            print("🔄 Initialisation des utilisateurs de démonstration...\n")
            
            created = 0
            skipped = 0
            
            for user_data in DEMO_USERS:
                # Vérifier si l'utilisateur existe déjà
                result = await session.execute(
                    select(Utilisateur).where(Utilisateur.email == user_data["email"])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"  ⊘ {user_data['email']} - Existe déjà")
                    skipped += 1
                else:
                    # Créer le nouvel utilisateur
                    user = Utilisateur(
                        nom=user_data["nom"],
                        email=user_data["email"],
                        mot_de_passe=hash_password(user_data["mot_de_passe"]),
                        role=user_data["role"],
                        actif=True
                    )
                    session.add(user)
                    created += 1
                    print(f"  ✓ {user_data['email']} - Créé ({user_data['role']})")
            
            # Sauvegarder les changements
            if created > 0:
                await session.commit()
                print(f"\n✅ Initialisatin complète!")
                print(f"   - {created} utilisateur(s) créé(s)")
                print(f"   - {skipped} utilisateur(s) existant(s)")
            else:
                print(f"\n✅ Tous les utilisateurs existent déjà.")
            
            print("\n📝 Utilisateurs de démonstration:")
            print("-" * 60)
            for user in DEMO_USERS:
                print(f"  Email: {user['email']}")
                print(f"  Mot de passe: {user['mot_de_passe']}")
                print(f"  Rôle: {user['role']}")
                print()
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
