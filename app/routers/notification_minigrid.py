from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/notifications", tags=["notifications"])


# 🔹 1️⃣ Lister toutes les notifications
@router.get("/", response_model=List[schemas.NotificationMinigridRead])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    stmt = select(models.NotificationMinigrid).order_by(models.NotificationMinigrid.cree_le.desc())
    result = await db.execute(stmt)
    rows = result.scalars().all()

    # ✅ Conversion ORM → Pydantic (Pydantic v2)
    return [schemas.NotificationMinigridRead.model_validate(r) for r in rows]


# 🔹 2️⃣ Créer une notification
@router.post("/", response_model=schemas.NotificationMinigridRead)
async def create_notification(
    payload: schemas.NotificationMinigridCreate,
    db: AsyncSession = Depends(get_db),
):
    notif = models.NotificationMinigrid(**payload.model_dump(exclude_unset=True))
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    # ✅ Retourne un modèle Pydantic valide
    return schemas.NotificationMinigridRead.model_validate(notif)


# 🔹 3️⃣ Marquer une notification comme lue
@router.patch("/{notif_id}/read", response_model=schemas.NotificationMinigridRead)
async def mark_as_read(notif_id: int, db: AsyncSession = Depends(get_db)):
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    notif.est_lu = True
    await db.commit()
    await db.refresh(notif)
    return schemas.NotificationMinigridRead.model_validate(notif)


# 🔹 4️⃣ Supprimer une notification
@router.delete("/{notif_id}")
async def delete_notification(notif_id: int, db: AsyncSession = Depends(get_db)):
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    await db.delete(notif)
    await db.commit()
    return {"deleted": notif_id}
