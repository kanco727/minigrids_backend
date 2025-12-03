# app/routers/minigrid.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from random import randint, uniform

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/minigrids", tags=["minigrids"])


# Liste complète avec coordonnées et infos site

@router.get("/geo", summary="Liste des mini-grids avec coordonnées et données simulées")
async def list_minigrids_geo(db: AsyncSession = Depends(get_db)):
    """
    Retourne toutes les mini-grids avec :
    - coordonnées GPS (si disponibles)
    - indicateur de localisation (has_location)
    - données simulées (production, batterie, température, utilisateurs)
    """
    query = text("""
        SELECT 
            m.id,
            m.nom,
            m.statut,
            m.site_id,
            s.localite AS site_localite,
            ST_Y(s.point::geometry) AS latitude,
            ST_X(s.point::geometry) AS longitude,
            (s.point IS NOT NULL) AS has_location
        FROM mini_grid m
        JOIN site s ON s.id = m.site_id
        ORDER BY m.id DESC;
    """)

    rows = (await db.execute(query)).mappings().all()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "nom": r["nom"],
            "statut": r["statut"],
            "site_id": r["site_id"],
            "localite": r["site_localite"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "has_location": r["has_location"],
            # Données simulées
            "production_kw": round(uniform(10.0, 150.0), 2),
            "batterie_soc": randint(40, 100),
            "temperature": round(uniform(25.0, 40.0), 1),
            "utilisateurs_actifs": randint(10, 80),
            "statut_reseau": "normal" if randint(0, 4) else "alerte"
        })

    return results



#  Liste simple

@router.get("/", response_model=List[schemas.MiniGridRead])
async def list_minigrids(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MiniGrid).order_by(models.MiniGrid.id.desc()))
    rows = result.scalars().all()
    return [schemas.MiniGridRead.from_orm(r) for r in rows]



# Création d’un mini-grid

@router.post("/", response_model=schemas.MiniGridRead, summary="Créer un mini-grid")
async def create_minigrid(payload: schemas.MiniGridCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing = await db.execute(select(models.MiniGrid).where(models.MiniGrid.nom == payload.nom))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Une mini-grid avec ce nom existe déjà.")

        obj = models.MiniGrid(**payload.dict(exclude_unset=True))
        obj.cree_le = datetime.utcnow()
        obj.maj_le = datetime.utcnow()

        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        print(f"✅ Mini-grid créée : {obj.nom}")
        return obj

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Erreur d’intégrité : site_id invalide ou doublon.")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
