from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/equipement-types", tags=["equipement-types"])

@router.get("/", response_model=List[schemas.EquipementTypeRead])
async def list_types(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(models.EquipementType).order_by(models.EquipementType.id.desc()))).scalars().all()
    return rows

@router.post("/", response_model=schemas.EquipementTypeRead)
async def create_type(payload: schemas.EquipementTypeCreate, db: AsyncSession = Depends(get_db)):
    obj = models.EquipementType(**payload.dict(exclude_unset=True))
    db.add(obj); await db.commit(); await db.refresh(obj)
    return obj

@router.patch("/{type_id}", response_model=schemas.EquipementTypeRead)
async def update_type(type_id: int, payload: schemas.EquipementTypeUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.EquipementType, type_id)
    if not obj: raise HTTPException(404, "Type introuvable")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit(); await db.refresh(obj)
    return obj

@router.delete("/{type_id}")
async def delete_type(type_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.EquipementType, type_id)
    if not obj: raise HTTPException(404, "Type introuvable")
    await db.delete(obj); await db.commit()
    return {"deleted": type_id}
