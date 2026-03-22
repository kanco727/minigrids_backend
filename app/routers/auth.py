from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from .. import models, schemas
from ..db import get_db
from ..schemas.auth import LoginRequest, LoginResponse, UserInfo
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login avec email et mot de passe"""
    stmt = select(models.Utilisateur).where(models.Utilisateur.email == payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Email introuvable")

    if not verify_password(payload.mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    if not user.actif:
        raise HTTPException(status_code=403, detail="Utilisateur désactivé")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            email=user.email,
            role=user.role,
            actif=user.actif
        )
    )


@router.post("/register", response_model=schemas.UtilisateurRead)
async def register(payload: schemas.UtilisateurCreate, db: AsyncSession = Depends(get_db)):
    """Créer un nouvel utilisateur (inscription)"""

    stmt = select(models.Utilisateur).where(models.Utilisateur.email == payload.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    user = models.Utilisateur(
        nom=payload.nom_complet,
        email=payload.email,
        mot_de_passe=hash_password(payload.mot_de_passe),
        role=payload.role.value if payload.role else "technicien"
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    EmailService.send_welcome_email(user.email, user.nom)

    return schemas.UtilisateurRead.model_validate(user)