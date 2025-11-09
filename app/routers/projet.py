from typing import List
import json
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/projets", tags=["projets"])

@router.get("/", response_model=List[schemas.ProjetRead])
async def list_projets(db: AsyncSession = Depends(get_db)):
    stmt = select(models.Projet).order_by(models.Projet.id.desc())
    rows = (await db.execute(stmt)).scalars().all()
    # Convertir style_carte_json en dict si besoin
    for p in rows:
        if isinstance(p.style_carte_json, str):
            try:
                p.style_carte_json = json.loads(p.style_carte_json)
            except Exception:
                p.style_carte_json = None
    return rows

@router.post("/", response_model=schemas.ProjetRead)
async def create_projet(payload: schemas.ProjetCreate, db: AsyncSession = Depends(get_db)):
    data = payload.dict(exclude_unset=True)
    if "style_carte_json" in data and isinstance(data["style_carte_json"], dict):
        data["style_carte_json"] = json.dumps(data["style_carte_json"])
    obj = models.Projet(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    if isinstance(obj.style_carte_json, str):
        try:
            obj.style_carte_json = json.loads(obj.style_carte_json)
        except Exception:
            obj.style_carte_json = None
    return obj

@router.get("/{proj_id}", response_model=schemas.ProjetRead)
async def get_projet(proj_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Projet, proj_id)
    if not obj:
        raise HTTPException(404, "Projet introuvable")
    return obj

@router.patch("/{proj_id}", response_model=schemas.ProjetRead)
async def update_projet(proj_id: int, payload: schemas.ProjetUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Projet, proj_id)
    if not obj:
        raise HTTPException(404, "Projet introuvable")
    for k, v in payload.dict(exclude_unset=True).items():
        if k == "style_carte_json" and isinstance(v, dict):
            v = json.dumps(v)
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    if isinstance(obj.style_carte_json, str):
        try:
            obj.style_carte_json = json.loads(obj.style_carte_json)
        except Exception:
            obj.style_carte_json = None
    return obj

@router.delete("/{proj_id}")
async def delete_projet(proj_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Projet, proj_id)
    if not obj:
        raise HTTPException(404, "Projet introuvable")
    await db.delete(obj)
    await db.commit()
    return {"deleted": proj_id}
