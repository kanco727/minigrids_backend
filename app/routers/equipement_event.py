# app/routers/equipement_event.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/equipements/events", tags=["Événements équipements"])


# ----------------------------------------------------------
# 1️⃣ Créer un événement (normalement interne)
# ----------------------------------------------------------
@router.post("/{equipement_id}", response_model=schemas.EquipementEventRead)
async def create_event(
    equipement_id: int,
    payload: schemas.EquipementEventCreate,
    db: AsyncSession = Depends(get_db),
):
    """Créer un événement pour un équipement (ON/OFF, REDÉMARRAGE...)."""

    equip = await db.get(models.EquipementMinigrid, equipement_id)
    if not equip:
        raise HTTPException(404, "Équipement introuvable")

    obj = models.EquipementEvent(
        equipement_id=equipement_id,
        **payload.model_dump(exclude_unset=True)
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    return obj


# ----------------------------------------------------------
# 2️⃣ Obtenir tous les événements d’un équipement
# ----------------------------------------------------------
@router.get("/{equipement_id}", response_model=List[schemas.EquipementEventRead])
async def list_events(
    equipement_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Récupérer l’historique complet des événements d’un équipement."""

    stmt = (
        select(models.EquipementEvent)
        .where(models.EquipementEvent.equipement_id == equipement_id)
        .order_by(desc(models.EquipementEvent.horodatage))
    )

    rows = (await db.execute(stmt)).scalars().all()
    return rows


# ----------------------------------------------------------
# 3️⃣ Lire un événement spécifique
# ----------------------------------------------------------
@router.get("/event/{event_id}", response_model=schemas.EquipementEventRead)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Lire un événement précis."""

    obj = await db.get(models.EquipementEvent, event_id)
    if not obj:
        raise HTTPException(404, "Événement introuvable")
    return obj


# ----------------------------------------------------------
# 4️⃣ Supprimer un événement
# ----------------------------------------------------------
@router.delete("/event/{event_id}")
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Supprimer un événement d’un équipement."""

    obj = await db.get(models.EquipementEvent, event_id)
    if not obj:
        raise HTTPException(404, "Événement introuvable")

    await db.delete(obj)
    await db.commit()

    return {"deleted": event_id}
