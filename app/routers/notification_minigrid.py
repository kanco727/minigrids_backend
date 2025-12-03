from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/notifications", tags=["notifications"])


#  Lister toutes les notifications

@router.get("/", response_model=List[schemas.NotificationMinigridRead])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    stmt = select(models.NotificationMinigrid).order_by(models.NotificationMinigrid.cree_le.desc())
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [schemas.NotificationMinigridRead.model_validate(r) for r in rows]



# Créer une notification

@router.post("/", response_model=schemas.NotificationMinigridRead)
async def create_notification(
    payload: schemas.NotificationMinigridCreate,
    db: AsyncSession = Depends(get_db),
):
    notif = models.NotificationMinigrid(**payload.model_dump(exclude_unset=True))
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return schemas.NotificationMinigridRead.model_validate(notif)


# Marquer UNE notification comme lue

@router.patch("/{notif_id}/read", response_model=schemas.NotificationMinigridRead)
async def mark_as_read(notif_id: int, db: AsyncSession = Depends(get_db)):
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    notif.est_lu = True
    await db.commit()
    await db.refresh(notif)
    return schemas.NotificationMinigridRead.model_validate(notif)



# arquer TOUTES les notifications comme lues

@router.patch("/mark_all_read")
async def mark_all_as_read(db: AsyncSession = Depends(get_db)):
    """Met à jour toutes les notifications non lues en 'lu'."""
    stmt = (
        update(models.NotificationMinigrid)
        .where(models.NotificationMinigrid.est_lu == False)
        .values(est_lu=True)
    )
    await db.execute(stmt)
    await db.commit()
    return {"message": "✅ Toutes les notifications ont été marquées comme lues."}



# Supprimer une notification

@router.delete("/{notif_id}")
async def delete_notification(notif_id: int, db: AsyncSession = Depends(get_db)):
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    await db.delete(notif)
    await db.commit()
    return {"deleted": notif_id}
