from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from .. import models, schemas
from ..dependencies import get_current_user, require_permission
from ..enums import PermissionEnum
from ..services.email_service import EmailService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[schemas.NotificationMinigridRead])
async def list_notifications(
    db: AsyncSession = Depends(get_db)
):
    """Lister les notifications (accès libre)"""
    stmt = select(models.NotificationMinigrid).order_by(models.NotificationMinigrid.cree_le.desc())
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [schemas.NotificationMinigridRead.model_validate(r) for r in rows]


@router.post("/", response_model=schemas.NotificationMinigridRead)
async def create_notification(
    payload: schemas.NotificationMinigridCreate,
    db: AsyncSession = Depends(get_db)
):
    """Créer une notification (accès libre)"""
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
    """Envoyer une notification par email (accès libre)"""
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")
    # Récupérer les destinataires
    stmt = select(models.Utilisateur).where(models.Utilisateur.actif == True)
    result = await db.execute(stmt)
    users = result.scalars().all()
    # Envoyer les emails
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
    """Marquer une notification comme lue (accès libre)"""
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")
    notif.est_lu = True
    await db.commit()
    await db.refresh(notif)
    return schemas.NotificationMinigridRead.model_validate(notif)


@router.delete("/{notif_id}")
async def delete_notification(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_permission(PermissionEnum.SEND_NOTIFICATIONS))
):
    """Supprimer une notification"""
    notif = await db.get(models.NotificationMinigrid, notif_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    await db.delete(notif)
    await db.commit()
    return {"deleted": notif_id}
