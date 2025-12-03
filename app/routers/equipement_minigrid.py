# app/routers/equipements.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/equipements", tags=["Équipements"])


# -------------------------------------------------------
# 1) Lister équipements (option minigrid_id)
# -------------------------------------------------------
@router.get("/", response_model=List[schemas.EquipementMinigridOut])
async def list_equipements(
    minigrid_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.EquipementMinigrid).order_by(models.EquipementMinigrid.id.desc())
    if minigrid_id is not None:
        stmt = stmt.where(models.EquipementMinigrid.minigrid_id == minigrid_id)

    rows = (await db.execute(stmt)).scalars().all()
    return rows


# -------------------------------------------------------
# 2) Créer équipement
# -------------------------------------------------------
@router.post("/", response_model=schemas.EquipementMinigridOut)
async def create_equipement(
    payload: schemas.EquipementMinigridCreate,
    db: AsyncSession = Depends(get_db),
):
    obj = models.EquipementMinigrid(**payload.model_dump(exclude_unset=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    # ✅ log event création
    ev = models.EquipementEvent(
        equipement_id=obj.id,
        type_event="created",
        message=f"Équipement créé ({obj.modele})",
        source="system",
        new_status=obj.statut
    )
    db.add(ev)
    await db.commit()

    return obj


# -------------------------------------------------------
# 3) Lire un équipement
# -------------------------------------------------------
@router.get("/{equip_id}", response_model=schemas.EquipementMinigridOut)
async def get_equipement(equip_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.EquipementMinigrid, equip_id)
    if not obj:
        raise HTTPException(404, "Équipement introuvable")
    return obj


# -------------------------------------------------------
# 4) Update équipement
# -------------------------------------------------------
@router.patch("/{equip_id}", response_model=schemas.EquipementMinigridOut)
async def update_equipement(
    equip_id: int,
    payload: schemas.EquipementMinigridUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.EquipementMinigrid, equip_id)
    if not obj:
        raise HTTPException(404, "Équipement introuvable")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj


# -------------------------------------------------------
# 5) Delete équipement
# -------------------------------------------------------
@router.delete("/{equip_id}")
async def delete_equipement(equip_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.EquipementMinigrid, equip_id)
    if not obj:
        raise HTTPException(404, "Équipement introuvable")
    await db.delete(obj)
    await db.commit()
    return {"deleted": equip_id}


# -------------------------------------------------------
# 6) Commande ON/OFF (historique auto)
# -------------------------------------------------------
@router.post("/{equip_id}/command")
async def simulate_command(
    equip_id: int,
    action: str,
    db: AsyncSession = Depends(get_db)
):
    equip = await db.get(models.EquipementMinigrid, equip_id)
    if not equip:
        raise HTTPException(404, "Équipement introuvable")

    old_status = equip.statut

    if action == "turn_on":
        equip.statut = "actif"
        type_event = "on"
        msg = "Mis en service"
    elif action == "turn_off":
        equip.statut = "inactif"
        type_event = "off"
        msg = "Mis hors service"
    else:
        raise HTTPException(400, "Action invalide")

    await db.commit()
    await db.refresh(equip)

    # ✅ log event
    ev = models.EquipementEvent(
        equipement_id=equip.id,
        type_event=type_event,
        message=msg,
        old_status=old_status,
        new_status=equip.statut,
        source="user"
    )
    db.add(ev)
    await db.commit()

    return {
        "id": equip.id,
        "statut": equip.statut,
        "message": f"Équipement {equip.id} mis à jour en {equip.statut}"
    }


# -------------------------------------------------------
# 7) Historique des événements d’un équipement
# -------------------------------------------------------
@router.get("/{equip_id}/events", response_model=List[schemas.EquipementEventRead])
async def list_events(equip_id: int, db: AsyncSession = Depends(get_db)):
    equip = await db.get(models.EquipementMinigrid, equip_id)
    if not equip:
        raise HTTPException(404, "Équipement introuvable")

    stmt = (
        select(models.EquipementEvent)
        .where(models.EquipementEvent.equipement_id == equip_id)
        .order_by(models.EquipementEvent.horodatage.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    return rows


@router.post("/{equip_id}/events", response_model=schemas.EquipementEventRead)
async def add_event(
    equip_id: int,
    payload: schemas.EquipementEventCreate,
    db: AsyncSession = Depends(get_db)
):
    equip = await db.get(models.EquipementMinigrid, equip_id)
    if not equip:
        raise HTTPException(404, "Équipement introuvable")

    ev = models.EquipementEvent(
        equipement_id=equip_id,
        **payload.model_dump(exclude_unset=True)
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return ev


# -------------------------------------------------------
# 8) Actions avancées (simulation + historique)
# -------------------------------------------------------
@router.post("/{equip_id}/actions")
async def advanced_action(
    equip_id: int,
    action: str,
    db: AsyncSession = Depends(get_db)
):
    equip = await db.get(models.EquipementMinigrid, equip_id)
    if not equip:
        raise HTTPException(404, "Équipement introuvable")

    allowed = {"restart", "reset", "force_measure", "check_comm"}
    if action not in allowed:
        raise HTTPException(400, "Action avancée invalide")

    labels = {
        "restart": "Redémarrage",
        "reset": "Réinitialisation",
        "force_measure": "Mesure forcée",
        "check_comm": "Vérification communication",
    }

    ev = models.EquipementEvent(
        equipement_id=equip_id,
        type_event=action,
        message=labels[action],
        source="user"
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)

    return {"ok": True, "message": labels[action]}
