"""
Script de migration - Hache tous les mots de passe existants en clair

Usage:
    python hash_passwords.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys
import os

# Ajouter le chemin de l'app au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import Utilisateur
from app.security import hash_password
from app.db import Base, DATABASE_URL

async def main():
    """Hache tous les mots de passe existants"""
    
    # Créer le moteur
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Récupérer tous les utilisateurs
            result = await session.execute(select(Utilisateur))
            users = result.scalars().all()
            
            if not users:
                print("✅ Aucun utilisateur trouvé. Rien à migrer.")
                return
            
            print(f"📊 Trouvé {len(users)} utilisateur(s)")
            
            # Hacher les mots de passe
            hashed_count = 0
            for user in users:
                # Vérifier si le mot de passe n'est pas déjà hashé (commence par $2b$)
                if not user.mot_de_passe.startswith("$2b$"):
                    old_password = user.mot_de_passe
                    user.mot_de_passe = hash_password(user.mot_de_passe)
                    hashed_count += 1
                    print(f"  ✓ {user.email} - Mot de passe hashé")
                else:
                    print(f"  ⊘ {user.email} - Mot de passe déjà hashé")
            
            # Sauvegarder les changements
            if hashed_count > 0:
                await session.commit()
                print(f"\n✅ Migration complète! {hashed_count} mot(s) de passe hashé(s)")
            else:
                print("\n✅ Tous les mots de passe sont déjà hachés.")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
