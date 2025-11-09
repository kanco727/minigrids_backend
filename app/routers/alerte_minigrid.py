from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from .. import models, schemas
from app.models import MesureMinigrid

router = APIRouter(prefix="/alertes", tags=["alertes"])

# ---------- Liste avec jointure (nom du minigrid) ----------
@router.get(
    "/full",
    response_model=List[schemas.AlerteMinigridListItem],
    summary="Liste des alertes avec le nom du minigrid",
)
async def list_alertes_full(
    minigrid_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    sql = """
        SELECT a.id,
               a.minigrid_id,
               m.nom AS minigrid_nom,
               a.type_alerte,
               a.niveau,
               a.message,
               a.statut,
               a.time_stamp
        FROM alerte_minigrid a
        JOIN mini_grid m ON m.id = a.minigrid_id
    """
    params = {}
    if minigrid_id is not None:
        sql += " WHERE a.minigrid_id = :mid"
        params["mid"] = minigrid_id
    sql += " ORDER BY a.time_stamp DESC"

    rows = (await db.execute(text(sql), params)).mappings().all()
    return [dict(r) for r in rows]


# ---------- CRUD de base ----------
@router.get("/", response_model=List[schemas.AlerteMinigridRead])
async def list_alertes(minigrid_id: Optional[int] = Query(None), db: AsyncSession = Depends(get_db)):
    stmt = select(models.AlerteMinigrid).order_by(models.AlerteMinigrid.time_stamp.desc())
    if minigrid_id is not None:
        stmt = stmt.where(models.AlerteMinigrid.minigrid_id == minigrid_id)
    return (await db.execute(stmt)).scalars().all()


@router.post("/", response_model=schemas.AlerteMinigridRead)
async def create_alerte(payload: schemas.AlerteMinigridCreate, db: AsyncSession = Depends(get_db)):
    obj = models.AlerteMinigrid(**payload.dict(exclude_unset=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    # Création automatique d'une notification
    notif_message = f"[{obj.niveau.upper()}] {obj.type_alerte} - {obj.message}"
    notif = models.NotificationMinigrid(
        alerte_id=obj.id,
        message=notif_message,
        type="app",
        destinataire="superviseur",
        est_lu=False,
    )
    db.add(notif)
    await db.commit()

    print(f"✅ Notification créée pour l’alerte {obj.id}")
    return obj


@router.get("/{alerte_id}", response_model=schemas.AlerteMinigridRead)
async def get_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.AlerteMinigrid, alerte_id)
    if not obj:
        raise HTTPException(404, "Alerte introuvable")
    return obj


@router.patch("/{alerte_id}", response_model=schemas.AlerteMinigridRead)
async def update_alerte(alerte_id: int, payload: schemas.AlerteMinigridUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.AlerteMinigrid, alerte_id)
    if not obj:
        raise HTTPException(404, "Alerte introuvable")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{alerte_id}")
async def delete_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.AlerteMinigrid, alerte_id)
    if not obj:
        raise HTTPException(404, "Alerte introuvable")
    await db.delete(obj)
    await db.commit()
    return {"deleted": alerte_id}


# ---------- Route intelligente de résolution ----------
@router.patch("/{alerte_id}/resolve", summary="Résoudre une alerte si les mesures sont normales")
async def resolve_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    """Analyse la dernière mesure du mini-grid associé et résout l’alerte si les valeurs sont normales."""

    alerte = await db.get(models.AlerteMinigrid, alerte_id)
    if not alerte:
        raise HTTPException(404, "Alerte introuvable")

    result = await db.execute(
        select(MesureMinigrid)
        .where(MesureMinigrid.minigrid_id == alerte.minigrid_id)
        .order_by(MesureMinigrid.time_stamp.desc())
        .limit(1)
    )
    mesure = result.scalar_one_or_none()
    if not mesure:
        raise HTTPException(404, "Aucune mesure trouvée pour ce mini-grid")

    normal = False
    reason = ""

    if "tension" in alerte.type_alerte.lower():
        normal = mesure.voltage and mesure.voltage > 210
        reason = f"Tension encore basse ({mesure.voltage} V)" if not normal else ""
    elif "température" in alerte.type_alerte.lower():
        normal = mesure.temperature and mesure.temperature < 45
        reason = f"Température toujours élevée ({mesure.temperature} °C)" if not normal else ""
    elif "surcharge" in alerte.type_alerte.lower():
        normal = mesure.courant and mesure.courant < 40
        reason = f"Courant encore élevé ({mesure.courant} A)" if not normal else ""
    else:
        normal = True  # alertes manuelles

    if normal:
        alerte.statut = "resolue"
        alerte.time_resolution = datetime.utcnow()
        await db.commit()
        await db.refresh(alerte)
        return {
            "message": "✅ Alerte résolue automatiquement",
            "alerte_id": alerte.id,
            "type": alerte.type_alerte,
            "minigrid": alerte.minigrid_id,
            "mesure_ok": {
                "voltage": mesure.voltage,
                "courant": mesure.courant,
                "temperature": mesure.temperature,
            },
        }
    else:
        raise HTTPException(status_code=400, detail=f"Impossible de résoudre : {reason}")
