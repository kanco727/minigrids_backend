# app/routers/statistiques.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/statistiques", tags=["statistiques"])


# ============================================================
# ✅ 1️⃣ Lister toutes les statistiques enregistrées
# ============================================================
@router.get("/", response_model=List[schemas.StatistiqueRead])
async def list_statistiques(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(models.Statistique).order_by(models.Statistique.date_rapport.desc())
    )).scalars().all()
    return rows


# ============================================================
# ✅ 2️⃣ Créer une statistique manuelle
# ============================================================
@router.post("/", response_model=schemas.StatistiqueRead)
async def create_statistique(payload: schemas.StatistiqueCreate, db: AsyncSession = Depends(get_db)):
    obj = models.Statistique(**payload.model_dump(exclude_unset=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ============================================================
# ✅ 3️⃣ Mettre à jour une statistique existante
# ============================================================
@router.patch("/{statistique_id}", response_model=schemas.StatistiqueRead)
async def update_statistique(statistique_id: int, payload: schemas.StatistiqueUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Statistique, statistique_id)
    if not obj:
        raise HTTPException(404, "Statistique introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


# ============================================================
# ✅ 4️⃣ Supprimer une statistique
# ============================================================
@router.delete("/{statistique_id}")
async def delete_statistique(statistique_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Statistique, statistique_id)
    if not obj:
        raise HTTPException(404, "Statistique introuvable")
    await db.delete(obj)
    await db.commit()
    return {"deleted": statistique_id}


# ============================================================
# ✅ 5️⃣ Rapports de maintenance (tickets avec rapport ou terminés)
# ============================================================
@router.get("/maintenance_rapports")
async def get_maintenance_reports(db: AsyncSession = Depends(get_db)):
    """
    Retourne les tickets de maintenance terminés ou avec rapport joint.
    Sert à alimenter l’onglet “Rapports de Maintenance” du frontend.
    """
    stmt = select(models.MaintenanceTicket).where(
        models.MaintenanceTicket.statut.in_(["rapport_envoye", "termine"])
    )
    tickets = (await db.execute(stmt)).scalars().all()

    data = []
    for t in tickets:
        data.append({
            "id": t.id,
            "minigrid_id": t.minigrid_id,
            "type": t.type,
            "priorite": t.priorite,
            "statut": t.statut,
            "rapport": t.rapport,
            "rapport_fichier": t.rapport_fichier,
            "date_creation": t.date_creation.isoformat() if t.date_creation else None
        })

    return data


# ============================================================
# ✅ 6️⃣ Statistiques globales (pour tableau de bord principal)
# ============================================================
@router.get("/globales")
async def statistiques_globales(db: AsyncSession = Depends(get_db)):
    """
    Fournit un résumé global pour le tableau de bord :
    - nombre de mini-grids
    - nombre d’alertes
    - nombre de tickets de maintenance
    - tickets en cours / terminés
    - nombre de rapports envoyés
    """
    total_minigrids = (await db.execute(select(func.count(models.MiniGrid.id)))).scalar()
    total_alertes = (await db.execute(select(func.count(models.AlerteMinigrid.id)))).scalar()
    total_tickets = (await db.execute(select(func.count(models.MaintenanceTicket.id)))).scalar()
    tickets_en_cours = (await db.execute(
        select(func.count(models.MaintenanceTicket.id)).where(models.MaintenanceTicket.statut == "en_cours")
    )).scalar()
    tickets_termines = (await db.execute(
        select(func.count(models.MaintenanceTicket.id)).where(models.MaintenanceTicket.statut == "termine")
    )).scalar()
    tickets_rapport = (await db.execute(
        select(func.count(models.MaintenanceTicket.id)).where(models.MaintenanceTicket.statut == "rapport_envoye")
    )).scalar()

    return {
        "total_minigrids": total_minigrids or 0,
        "total_alertes": total_alertes or 0,
        "total_tickets": total_tickets or 0,
        "tickets_en_cours": tickets_en_cours or 0,
        "tickets_termines": tickets_termines or 0,
        "tickets_rapport_envoye": tickets_rapport or 0,
    }
