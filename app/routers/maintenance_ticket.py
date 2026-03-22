from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


# ============================================================
# 1) Lister les tickets
# ============================================================
@router.get("/tickets", response_model=List[schemas.MaintenanceTicketRead])
async def list_tickets(
    minigrid_id: int | None = Query(None),
    statut: str | None = Query(None),
    priorite: str | None = Query(None),
    type: str | None = Query(None),
    assigne_a: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.MaintenanceTicket).order_by(models.MaintenanceTicket.id.desc())

    if minigrid_id is not None:
        stmt = stmt.where(models.MaintenanceTicket.minigrid_id == minigrid_id)
    if statut:
        stmt = stmt.where(models.MaintenanceTicket.statut == statut)
    if priorite:
        stmt = stmt.where(models.MaintenanceTicket.priorite == priorite)
    if type:
        stmt = stmt.where(models.MaintenanceTicket.type == type)
    if assigne_a is not None:
        stmt = stmt.where(models.MaintenanceTicket.assigne_a == assigne_a)

    rows = (await db.execute(stmt)).scalars().all()
    return [schemas.MaintenanceTicketRead.model_validate(r) for r in rows]


# ============================================================
# 2) Créer un ticket
# ============================================================
@router.post("/tickets", response_model=schemas.MaintenanceTicketRead)
async def create_ticket(
    payload: schemas.MaintenanceTicketCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        data = payload.model_dump(exclude_unset=True)

        # valeurs de base réalistes
        data["date_creation"] = datetime.now(timezone.utc)
        data["statut"] = data.get("statut") or "ouvert"
        data["type"] = data.get("type") or "corrective"
        data["priorite"] = data.get("priorite") or "moyenne"
        data["source_ticket"] = data.get("source_ticket") or "manuel"

        # nettoyage
        if "titre" in data and data["titre"]:
            data["titre"] = data["titre"].strip()

        if "description" in data and data["description"]:
            data["description"] = data["description"].strip()

        # validations métier
        if not data.get("minigrid_id"):
            raise HTTPException(status_code=400, detail="Une mini-grid doit être sélectionnée.")

        if not data.get("titre"):
            raise HTTPException(status_code=400, detail="Le titre du ticket est obligatoire.")

        if not data.get("description"):
            raise HTTPException(status_code=400, detail="La description du ticket est obligatoire.")

        obj = models.MaintenanceTicket(**data)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)

        return schemas.MaintenanceTicketRead.model_validate(obj)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création ticket: {str(e)}")


# ============================================================
# 3) Mise à jour générique
# ============================================================
@router.patch("/tickets/{ticket_id}", response_model=schemas.MaintenanceTicketRead)
async def update_ticket(
    ticket_id: int,
    payload: schemas.MaintenanceTicketUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="Aucune donnée fournie")

    for k, v in data.items():
        if hasattr(obj, k):
            setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.model_validate(obj)


# ============================================================
# 4) Planifier un ticket
# ============================================================
@router.patch("/tickets/{ticket_id}/planifier", response_model=schemas.MaintenanceTicketRead)
async def planifier_ticket(
    ticket_id: int,
    date_planifiee: datetime,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    if obj.statut in ["termine", "rapport_envoye"]:
        raise HTTPException(status_code=400, detail="Impossible de planifier un ticket déjà clôturé.")

    obj.date_planifiee = date_planifiee
    obj.statut = "planifie"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.model_validate(obj)


# ============================================================
# 5) Assigner un ticket
# ============================================================
@router.patch("/tickets/{ticket_id}/assigner", response_model=schemas.MaintenanceTicketRead)
async def assigner_ticket(
    ticket_id: int,
    assigne_a: int,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    if obj.statut in ["termine", "rapport_envoye"]:
        raise HTTPException(status_code=400, detail="Ticket déjà terminé, impossible de réassigner.")

    obj.assigne_a = assigne_a

    # si déjà planifié, on garde planifié ; sinon ouvert → en_cours ou assigné selon ta logique
    if obj.statut == "ouvert":
        obj.statut = "en_cours"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.model_validate(obj)


# ============================================================
# 6) Démarrer une intervention
# ============================================================
@router.patch("/tickets/{ticket_id}/demarrer", response_model=schemas.MaintenanceTicketRead)
async def demarrer_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    if obj.statut in ["rapport_envoye", "termine"]:
        raise HTTPException(status_code=400, detail="Ce ticket ne peut plus être démarré.")

    obj.date_debut = datetime.now(timezone.utc)
    obj.statut = "en_cours"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.model_validate(obj)


# ============================================================
# 7) Clôturer un ticket
# ============================================================
@router.patch("/tickets/{ticket_id}/cloturer", response_model=schemas.MaintenanceTicketRead)
async def cloturer_ticket(
    ticket_id: int,
    rapport: str,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    if obj.statut != "en_cours":
        raise HTTPException(status_code=400, detail="Le ticket n'est pas en cours.")

    if not rapport or len(rapport.strip()) < 5:
        raise HTTPException(status_code=400, detail="Le rapport doit être fourni.")

    obj.rapport = rapport.strip()
    obj.date_fin = datetime.now(timezone.utc)
    obj.statut = "rapport_envoye"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.model_validate(obj)


# ============================================================
# 8) Validation finale
# ============================================================
@router.patch("/tickets/{ticket_id}/valider", response_model=schemas.MaintenanceTicketRead)
async def valider_ticket(
    ticket_id: int,
    valide_par: int,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    if obj.statut != "rapport_envoye":
        raise HTTPException(status_code=400, detail="Ticket non prêt à être validé.")

    obj.valide_par = valide_par
    obj.date_validation = datetime.now(timezone.utc)
    obj.statut = "termine"

    await db.commit()
    await db.refresh(obj)
    return schemas.MaintenanceTicketRead.model_validate(obj)


# ============================================================
# 9) Supprimer un ticket
# ============================================================
@router.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Ticket introuvable")

    await db.delete(obj)
    await db.commit()
    return {"deleted": ticket_id}


# ============================================================
# 10) Dashboard maintenance
# ============================================================
@router.get("/dashboard")
async def dashboard_maintenance(db: AsyncSession = Depends(get_db)):
    stmt = select(models.MaintenanceTicket)
    tickets = (await db.execute(stmt)).scalars().all()

    if not tickets:
        return {
            "total": 0,
            "ouverts": 0,
            "planifies": 0,
            "en_cours": 0,
            "rapport_envoye": 0,
            "termines": 0,
            "urgents": 0,
            "haute_priorite": 0,
            "preventives": 0,
            "correctives": 0,
            "par_minigrid": [],
        }

    par_minigrid = {}

    for t in tickets:
        key = t.minigrid_id or "Inconnu"
        if key not in par_minigrid:
            par_minigrid[key] = {
                "minigrid_id": t.minigrid_id,
                "total": 0,
                "ouverts": 0,
                "planifies": 0,
                "en_cours": 0,
                "termines": 0,
            }

        par_minigrid[key]["total"] += 1

        if t.statut == "ouvert":
            par_minigrid[key]["ouverts"] += 1
        elif t.statut == "planifie":
            par_minigrid[key]["planifies"] += 1
        elif t.statut == "en_cours":
            par_minigrid[key]["en_cours"] += 1
        elif t.statut in ["rapport_envoye", "termine"]:
            par_minigrid[key]["termines"] += 1

    return {
        "total": len(tickets),
        "ouverts": len([t for t in tickets if t.statut == "ouvert"]),
        "planifies": len([t for t in tickets if t.statut == "planifie"]),
        "en_cours": len([t for t in tickets if t.statut == "en_cours"]),
        "rapport_envoye": len([t for t in tickets if t.statut == "rapport_envoye"]),
        "termines": len([t for t in tickets if t.statut == "termine"]),
        "urgents": len([t for t in tickets if t.priorite == "urgente"]),
        "haute_priorite": len([t for t in tickets if t.priorite == "haute"]),
        "preventives": len([t for t in tickets if t.type == "preventive"]),
        "correctives": len([t for t in tickets if t.type == "corrective"]),
        "par_minigrid": list(par_minigrid.values()),
    }