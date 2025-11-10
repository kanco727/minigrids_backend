# app/routers/maintenance_ticket.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


# ============================================================
# ✅ 1️⃣ Lister tous les tickets
# ============================================================
@router.get("/tickets", response_model=List[schemas.MaintenanceTicketRead])
async def list_tickets(
    minigrid_id: int | None = Query(None),
    statut: str | None = Query(None),
    priorite: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(models.MaintenanceTicket).order_by(models.MaintenanceTicket.id.desc())
    if minigrid_id is not None:
        stmt = stmt.where(models.MaintenanceTicket.minigrid_id == minigrid_id)
    if statut is not None:
        stmt = stmt.where(models.MaintenanceTicket.statut == statut)
    if priorite is not None:
        stmt = stmt.where(models.MaintenanceTicket.priorite == priorite)

    rows = (await db.execute(stmt)).scalars().all()
    return [schemas.MaintenanceTicketRead.from_orm(r) for r in rows]


# ============================================================
# ✅ 2️⃣ Créer un ticket
# ============================================================
@router.post("/tickets", response_model=schemas.MaintenanceTicketRead)
async def create_ticket(payload: schemas.MaintenanceTicketCreate, db: AsyncSession = Depends(get_db)):
    try:
        data = payload.dict(exclude_unset=True)
        data["date_creation"] = datetime.utcnow()
        data["statut"] = data.get("statut", "ouvert")
        data["description"] = (data.get("description") or "").strip()

        if not data.get("type"):
            raise HTTPException(400, "Le type de ticket est obligatoire.")
        if not data.get("description"):
            raise HTTPException(400, "La description du ticket est obligatoire.")
        if not data.get("minigrid_id"):
            raise HTTPException(400, "Une mini-grid doit être sélectionnée.")

        obj = models.MaintenanceTicket(**data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return schemas.MaintenanceTicketRead.from_orm(obj)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création ticket: {str(e)}")


# ============================================================
# ✅ 3️⃣ Mise à jour générique
# ============================================================
@router.patch("/tickets/{ticket_id}", response_model=schemas.MaintenanceTicketRead)
async def update_ticket(ticket_id: int, payload: dict = None, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")
    if not payload:
        raise HTTPException(400, "Aucune donnée fournie")

    for k, v in payload.items():
        if hasattr(obj, k):
            setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.from_orm(obj)


# ============================================================
# ✅ 4️⃣ Assigner un ticket
# ============================================================
@router.patch("/tickets/{ticket_id}/assigner", response_model=schemas.MaintenanceTicketRead)
async def assigner_ticket(ticket_id: int, assigne_a: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")
    if obj.statut in ["termine", "rapport_envoye"]:
        raise HTTPException(400, "Ticket déjà terminé, impossible de réassigner.")

    obj.assigne_a = assigne_a
    obj.statut = "en_cours"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.from_orm(obj)


# ============================================================
# ✅ 5️⃣ Clôturer un ticket
# ============================================================
@router.patch("/tickets/{ticket_id}/cloturer", response_model=schemas.MaintenanceTicketRead)
async def cloturer_ticket(ticket_id: int, rapport: str, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")
    if obj.statut != "en_cours":
        raise HTTPException(400, "Le ticket n'est pas en cours.")
    if not rapport or len(rapport.strip()) < 5:
        raise HTTPException(400, "Le rapport doit être fourni.")

    obj.rapport = rapport.strip()
    obj.statut = "rapport_envoye"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.from_orm(obj)


# ============================================================
# ✅ 6️⃣ Validation finale
# ============================================================
@router.patch("/tickets/{ticket_id}/valider", response_model=schemas.MaintenanceTicketRead)
async def valider_ticket(ticket_id: int, valide_par: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")
    if obj.statut != "rapport_envoye":
        raise HTTPException(400, "Ticket non prêt à être validé.")

    obj.valide_par = valide_par
    obj.statut = "termine"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.from_orm(obj)


# ============================================================
# ✅ 7️⃣ Supprimer un ticket
# ============================================================
@router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")

    await db.delete(obj)
    await db.commit()
    return {"deleted": ticket_id}


# ============================================================
# ✅ 8️⃣ Statistiques globales
# ============================================================
@router.get("/dashboard")
async def dashboard_maintenance(db: AsyncSession = Depends(get_db)):
    stmt = select(models.MaintenanceTicket)
    tickets = (await db.execute(stmt)).scalars().all()

    if not tickets:
        return {
            "total": 0, "ouverts": 0, "en_cours": 0, "rapport_envoye": 0,
            "termines": 0, "urgents": 0, "haute_priorite": 0, "par_minigrid": []
        }

    par_minigrid = {}
    for t in tickets:
        key = t.minigrid_id or "Inconnu"
        if key not in par_minigrid:
            par_minigrid[key] = {"minigrid_id": t.minigrid_id, "total": 0, "ouverts": 0, "en_cours": 0, "termines": 0}
        par_minigrid[key]["total"] += 1
        if t.statut == "ouvert":
            par_minigrid[key]["ouverts"] += 1
        elif t.statut == "en_cours":
            par_minigrid[key]["en_cours"] += 1
        elif t.statut in ["rapport_envoye", "termine"]:
            par_minigrid[key]["termines"] += 1

    return {
        "total": len(tickets),
        "ouverts": len([t for t in tickets if t.statut == "ouvert"]),
        "en_cours": len([t for t in tickets if t.statut == "en_cours"]),
        "rapport_envoye": len([t for t in tickets if t.statut == "rapport_envoye"]),
        "termines": len([t for t in tickets if t.statut == "termine"]),
        "urgents": len([t for t in tickets if t.priorite == "urgente"]),
        "haute_priorite": len([t for t in tickets if t.priorite == "haute"]),
        "par_minigrid": list(par_minigrid.values())
    }


# ============================================================
# ✅ 9️⃣ Récupérer un ticket précis (pour la page /statistiques)
# ============================================================
@router.get("/tickets/{ticket_id}", response_model=schemas.MaintenanceTicketRead)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """
    Récupère les informations détaillées d’un ticket spécifique.
    Utilisé par la page /statistiques pour afficher le rapport.
    """
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} introuvable.")

    return schemas.MaintenanceTicketRead.from_orm(obj)
