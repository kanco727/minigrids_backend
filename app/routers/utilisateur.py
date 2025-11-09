from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/utilisateurs", tags=["utilisateurs"])

@router.get("/", response_model=List[schemas.UtilisateurRead])
async def list_users(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(models.Utilisateur).order_by(models.Utilisateur.id.desc()))).scalars().all()
    return rows

@router.post("/", response_model=schemas.UtilisateurRead)
async def create_user(payload: schemas.UtilisateurCreate, db: AsyncSession = Depends(get_db)):
    obj = models.Utilisateur(**payload.model_dump(exclude_unset=True))
    db.add(obj); await db.commit(); await db.refresh(obj)
    return obj

@router.patch("/{user_id}", response_model=schemas.UtilisateurRead)
async def update_user(user_id: int, payload: schemas.UtilisateurUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Utilisateur, user_id)
    if not obj: raise HTTPException(404, "Utilisateur introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit(); await db.refresh(obj)
    return obj

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Utilisateur, user_id)
    if not obj: raise HTTPException(404, "Utilisateur introuvable")
    await db.delete(obj); await db.commit()
    return {"deleted": user_id}
