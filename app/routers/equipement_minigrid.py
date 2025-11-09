from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/equipements", tags=["Équipements"])

# --- Lister tous les équipements ou ceux d’un minigrid spécifique ---
@router.get("/", response_model=List[schemas.EquipementMinigridOut])
async def list_equipements(minigrid_id: int | None = Query(None), db: AsyncSession = Depends(get_db)):
    stmt = select(models.EquipementMinigrid).order_by(models.EquipementMinigrid.id.desc())
    if minigrid_id is not None:
        stmt = stmt.where(models.EquipementMinigrid.minigrid_id == minigrid_id)
    rows = (await db.execute(stmt)).scalars().all()
    return rows


# --- Créer un équipement ---
@router.post("/", response_model=schemas.EquipementMinigridOut)
async def create_equipement(payload: schemas.EquipementMinigridCreate, db: AsyncSession = Depends(get_db)):
    obj = models.EquipementMinigrid(**payload.dict(exclude_unset=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# --- Lire un équipement spécifique ---
@router.get("/{equip_id}", response_model=schemas.EquipementMinigridOut)
async def get_equipement(equip_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.EquipementMinigrid, equip_id)
    if not obj:
        raise HTTPException(404, "Équipement introuvable")
    return obj


# --- Mettre à jour un équipement ---
@router.patch("/{equip_id}", response_model=schemas.EquipementMinigridOut)
async def update_equipement(equip_id: int, payload: schemas.EquipementMinigridUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.EquipementMinigrid, equip_id)
    if not obj:
        raise HTTPException(404, "Équipement introuvable")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


# --- Supprimer un équipement ---
@router.delete("/{equip_id}")
async def delete_equipement(equip_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.EquipementMinigrid, equip_id)
    if not obj:
        raise HTTPException(404, "Équipement introuvable")
    await db.delete(obj)
    await db.commit()
    return {"deleted": equip_id}


# --- Simulation commande ON/OFF ---
@router.post("/{equip_id}/command")
async def simulate_command(equip_id: int, action: str, db: AsyncSession = Depends(get_db)):
    """
    Simulation d'une commande envoyée à un équipement :
    - action = 'turn_on' → passe l'équipement à actif
    - action = 'turn_off' → passe l'équipement à inactif
    """
    equip = await db.get(models.EquipementMinigrid, equip_id)
    if not equip:
        raise HTTPException(404, "Équipement introuvable")

    if action == "turn_on":
        equip.statut = "actif"
    elif action == "turn_off":
        equip.statut = "inactif"
    else:
        raise HTTPException(400, "Action invalide")

    await db.commit()
    await db.refresh(equip)

    return {
        "id": equip.id,
        "statut": equip.statut,
        "message": f"Équipement {equip.id} mis à jour en {equip.statut}"
    }
