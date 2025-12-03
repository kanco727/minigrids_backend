from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from .. import models, schemas
from app.models import MesureMinigrid

router = APIRouter(prefix="/alertes", tags=["alertes"])


# ---------- utilitaire: journaliser dans alerte_historique ----------
async def _log_history(
    db: AsyncSession,
    alerte_id: int,
    action: str,
    acteur_id: int | None = None,
    details: str | None = None,
):
    h = models.AlerteHistorique(
        alerte_id=alerte_id,
        action=action,
        acteur_id=acteur_id,
        details=details,
    )
    db.add(h)
    await db.commit()


# ---------- Liste avec jointure (nom du minigrid) ----------
@router.get("/full", response_model=List[schemas.AlerteMinigridListItem])
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
async def list_alertes(
    minigrid_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.AlerteMinigrid).order_by(
        models.AlerteMinigrid.time_stamp.desc()
    )
    if minigrid_id is not None:
        stmt = stmt.where(models.AlerteMinigrid.minigrid_id == minigrid_id)
    return (await db.execute(stmt)).scalars().all()


@router.post("/", response_model=schemas.AlerteMinigridRead)
async def create_alerte(
    payload: schemas.AlerteMinigridCreate, db: AsyncSession = Depends(get_db)
):
    obj = models.AlerteMinigrid(**payload.dict(exclude_unset=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    # 🔔 Création automatique d'une notification
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

    await _log_history(db, obj.id, "creation", None, notif_message)
    return obj


@router.get("/{alerte_id}", response_model=schemas.AlerteMinigridRead)
async def get_alerte(alerte_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.AlerteMinigrid, alerte_id)
    if not obj:
        raise HTTPException(404, "Alerte introuvable")
    return obj


@router.patch("/{alerte_id}", response_model=schemas.AlerteMinigridRead)
async def update_alerte(
    alerte_id: int,
    payload: schemas.AlerteMinigridUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.AlerteMinigrid, alerte_id)
    if not obj:
        raise HTTPException(404, "Alerte introuvable")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)

    await _log_history(db, obj.id, "statut_change", None, f"statut={obj.statut}")
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

    normal, reason = False, ""
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
        normal = True

    if normal:
        alerte.statut = "resolue"
        alerte.time_resolution = datetime.utcnow()
        await db.commit()
        await db.refresh(alerte)
        await _log_history(db, alerte.id, "resolution", None, "résolution automatique")
        return {
            "message": "✅ Alerte résolue automatiquement",
            "alerte_id": alerte.id,
            "type": alerte.type_alerte,
            "minigrid": alerte.minigrid_id,
        }
    else:
        raise HTTPException(status_code=400, detail=f"Impossible de résoudre : {reason}")


# ---------- Nouvelles routes avancées ----------

@router.get("/actives", response_model=List[schemas.AlerteMinigridRead])
async def list_actives(db: AsyncSession = Depends(get_db)):
    stmt = select(models.AlerteMinigrid).where(models.AlerteMinigrid.statut != "archivee")
    return (await db.execute(stmt)).scalars().all()


@router.get("/stats", response_model=schemas.AlerteStats)
async def alerte_stats(db: AsyncSession = Depends(get_db)):
    sql = text("""
        SELECT
          COUNT(*)::int AS total,
          SUM(CASE WHEN niveau = 'crit' THEN 1 ELSE 0 END)::int AS critiques,
          SUM(CASE WHEN statut = 'resolue' THEN 1 ELSE 0 END)::int AS resolues,
          AVG(EXTRACT(EPOCH FROM (time_resolution - time_stamp))/3600.0) AS temps_resolution_h
        FROM alerte_minigrid;
    """)
    row = (await db.execute(sql)).mappings().first()
    return schemas.AlerteStats(**row)


@router.get("/{alerte_id}/timeline", response_model=List[schemas.AlerteHistoriqueRead])
async def alerte_timeline(alerte_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.AlerteHistorique).where(
        models.AlerteHistorique.alerte_id == alerte_id
    ).order_by(models.AlerteHistorique.time_action.asc())
    return (await db.execute(stmt)).scalars().all()


@router.post("/{alerte_id}/comment", response_model=schemas.AlerteMinigridRead)
async def alerte_add_comment(
    alerte_id: int, payload: schemas.AlerteCommentPayload, db: AsyncSession = Depends(get_db)
):
    alerte = await db.get(models.AlerteMinigrid, alerte_id)
    if not alerte:
        raise HTTPException(404, "Alerte introuvable")

    sep = "\n---\n" if alerte.commentaire else ""
    alerte.commentaire = (alerte.commentaire or "") + f"{sep}{datetime.utcnow().isoformat()} : {payload.commentaire}"
    await db.commit()
    await db.refresh(alerte)

    await _log_history(db, alerte_id, "commentaire", None, payload.commentaire)
    return alerte


@router.patch("/{alerte_id}/assign", response_model=schemas.AlerteMinigridRead)
async def alerte_assign(
    alerte_id: int, payload: schemas.AlerteAssignPayload, db: AsyncSession = Depends(get_db)
):
    alerte = await db.get(models.AlerteMinigrid, alerte_id)
    if not alerte:
        raise HTTPException(404, "Alerte introuvable")

    alerte.responsable_id = payload.responsable_id
    if payload.commentaire:
        sep = "\n---\n" if alerte.commentaire else ""
        alerte.commentaire = (alerte.commentaire or "") + f"{sep}{datetime.utcnow().isoformat()} : {payload.commentaire}"

    if alerte.statut == "active":
        alerte.statut = "en_traitement"

    await db.commit()
    await db.refresh(alerte)
    await _log_history(db, alerte_id, "assignation", payload.responsable_id, f"assigné à {payload.responsable_id}")
    return alerte
