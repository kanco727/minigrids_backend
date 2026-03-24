from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from .. import models, schemas
from ..services.email_service import EmailService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[schemas.NotificationMinigridRead])
async def list_notifications(
    db: AsyncSession = Depends(get_db)
):
    """Lister les notifications non archivées"""
    stmt = (
        select(models.NotificationMinigrid)
        .where(models.NotificationMinigrid.est_archivee == False)
        .order_by(models.NotificationMinigrid.cree_le.desc())
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [schemas.NotificationMinigridRead.model_validate(r) for r in rows]


@router.post("/", response_model=schemas.NotificationMinigridRead)
async def create_notification(
    payload: schemas.NotificationMinigridCreate,
    db: AsyncSession = Depends(get_db)
):
    notif = models.NotificationMinigrid(**payload.model_dump(exclude_unset=True))
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return schemas.NotificationMinigridRead.model_validate(notif)


@router.post("/{notif_id}/send-email")
async def send_notification_email(
    notif_id: int,
    db: AsyncSession = Depends(get_db)
):
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    stmt = select(models.Utilisateur).where(models.Utilisateur.actif == True)
    result = await db.execute(stmt)
    users = result.scalars().all()

    sent_count = 0
    for user in users:
        success = EmailService.send_notification_email(
            recipient=user.email,
            notification_type=notif.type or "info",
            message=notif.message,
            metadata={"ID": str(notif.id), "Type": notif.type}
        )
        if success:
            sent_count += 1

    return {
        "notification_id": notif_id,
        "emails_sent": sent_count,
        "total_recipients": len(users)
    }


@router.patch("/{notif_id}/read", response_model=schemas.NotificationMinigridRead)
async def mark_as_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db)
):
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    notif.est_lu = True
    await db.commit()
    await db.refresh(notif)
    return schemas.NotificationMinigridRead.model_validate(notif)


@router.patch("/mark-all-read", response_model=List[schemas.NotificationMinigridRead])
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(models.NotificationMinigrid).where(
        models.NotificationMinigrid.est_archivee == False,
        models.NotificationMinigrid.est_lu == False
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    for notif in notifications:
        notif.est_lu = True

    await db.commit()

    for notif in notifications:
        await db.refresh(notif)

    return [schemas.NotificationMinigridRead.model_validate(n) for n in notifications]


@router.patch("/{notif_id}/archive", response_model=schemas.NotificationMinigridRead)
async def archive_notification(
    notif_id: int,
    db: AsyncSession = Depends(get_db)
):
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    notif.est_archivee = True
    notif.archivee_le = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(notif)
    return schemas.NotificationMinigridRead.model_validate(notif)