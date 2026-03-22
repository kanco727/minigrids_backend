from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from .. import models, schemas
from ..dependencies import get_current_user, get_admin_user, require_permission
from ..enums import PermissionEnum
from ..security import hash_password

router = APIRouter(prefix="/utilisateurs", tags=["utilisateurs"])

@router.get("/", response_model=List[schemas.UtilisateurRead])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_permission(PermissionEnum.VIEW_USERS))
):
    """Lister tous les utilisateurs"""
    rows = (await db.execute(select(models.Utilisateur).order_by(models.Utilisateur.id.desc()))).scalars().all()
    return [schemas.UtilisateurRead.model_validate(r) for r in rows]

@router.post("/", response_model=schemas.UtilisateurRead)
async def create_user(
    payload: schemas.UtilisateurCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_permission(PermissionEnum.MANAGE_USERS))
):
    """Créer un nouvel utilisateur (admin seulement)"""
    
    # Vérifier si l'email existe déjà
    stmt = select(models.Utilisateur).where(models.Utilisateur.email == payload.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Créer l'utilisateur avec mot de passe hashé
    obj = models.Utilisateur(
        nom=payload.nom_complet,
        email=payload.email,
        mot_de_passe=hash_password(payload.mot_de_passe),
        role=payload.role.value if payload.role else "technicien"
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return schemas.UtilisateurRead.model_validate(obj)

@router.get("/me", response_model=schemas.UtilisateurRead)
async def get_current_user_info(
    current_user: models.Utilisateur = Depends(get_current_user)
):
    """Récupérer les infos de l'utilisateur actuel"""
    return schemas.UtilisateurRead.model_validate(current_user)

@router.patch("/{user_id}", response_model=schemas.UtilisateurRead)
async def update_user(
    user_id: int, 
    payload: schemas.UtilisateurUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user)
):
    """Mettre à jour un utilisateur"""
    
    # Vérifier les permissions: admin ou l'utilisateur se modifie lui-même
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    obj = await db.get(models.Utilisateur, user_id)
    if not obj:
        raise HTTPException(404, "Utilisateur introuvable")
    
    for k, v in payload.model_dump(exclude_unset=True).items():
        if k == "mot_de_passe" and v:
            setattr(obj, k, hash_password(v))
        elif v is not None:
            setattr(obj, k, v)
    
    await db.commit()
    await db.refresh(obj)
    return schemas.UtilisateurRead.model_validate(obj)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_permission(PermissionEnum.MANAGE_USERS))
):
    """Supprimer un utilisateur (admin seulement)"""
    obj = await db.get(models.Utilisateur, user_id)
    if not obj:
        raise HTTPException(404, "Utilisateur introuvable")
    
    if obj.id == current_user.id:
        raise HTTPException(400, "Impossible de supprimer votre propre compte")
    
    await db.delete(obj)
    await db.commit()
    return {"deleted": user_id}
