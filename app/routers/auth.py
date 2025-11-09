from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/auth", tags=["Authentification"])

@router.post("/login", response_model=schemas.auth.LoginResponse)
async def login(payload: schemas.auth.LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Utilisateur).where(models.Utilisateur.email == payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Email introuvable")

    # ⚙️ Vérifie le mot de passe (en clair pour l’instant)
    if getattr(user, "mot_de_passe", None) != payload.mot_de_passe:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    # ✅ Retourne l'utilisateur au frontend
    return {
        "access_token": f"token-{user.id}",
        "user": {
            "id": user.id,
            "email": user.email,
            "nom_complet": getattr(user, "nom", user.email),
            "role": user.role,
            "mfa_active": False,
              # "dernier_login": str(user.dernier_login) if user.dernier_login else None,
        }
    }
