from typing import List, Optional
from datetime import datetime, timezone, timedelta
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db, AsyncSessionLocal
from .. import models, schemas

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


# Helpers

STATUTS = {"ouvert", "en_cours", "rapport_envoye", "termine"}
ALLOWED_TRANSITIONS = {
    "ouvert": {"en_cours"},
    "en_cours": {"rapport_envoye"},
    "rapport_envoye": {"termine"},
    "termine": set(),
}


def _ensure_statut_transition(current: str, new: str):
    if new not in ALLOWED_TRANSITIONS.get(current, set()):
        raise HTTPException(
            400,
            f"Transition interdite: '{current}' → '{new}'. "
            f"Autorisé: {', '.join(ALLOWED_TRANSITIONS[current]) or 'aucune'}"
        )


async def _notify(db: AsyncSession, message: str, destinataire: str = "superviseur"):
    notif = models.NotificationMinigrid(
        message=message,
        type="alert",
        destinataire=destinataire,
        est_lu=False,
    )
    db.add(notif)
    await db.commit()



#  Payloads spécifiques

class AssignPayload(BaseModel):
    assigne_a: int
    commentaire: Optional[str] = None


class ReportPayload(BaseModel):
    rapport: str
    rapport_fichier: Optional[str] = None


class ValidatePayload(BaseModel):
    valide_par: int



#  Liste des tickets

@router.get("/tickets", response_model=List[schemas.MaintenanceTicketRead])
async def list_tickets(
    statut: Optional[str] = Query(None),
    priorite: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(models.MaintenanceTicket)
    if statut:
        stmt = stmt.where(models.MaintenanceTicket.statut == statut)
    if priorite:
        stmt = stmt.where(models.MaintenanceTicket.priorite == priorite)

    stmt = stmt.order_by(desc(models.MaintenanceTicket.date_creation))
    rows = (await db.execute(stmt)).scalars().all()
    return [schemas.MaintenanceTicketRead.model_validate(r) for r in rows]



#  Création d’un ticket

@router.post("/tickets", response_model=schemas.MaintenanceTicketRead)
async def create_ticket(payload: schemas.MaintenanceTicketCreate, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    data["date_creation"] = datetime.now(timezone.utc)
    data["statut"] = data.get("statut", "ouvert")
    data["priorite"] = data.get("priorite", "normale")

    if not data.get("description"):
        raise HTTPException(400, "Description requise.")

    obj = models.MaintenanceTicket(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    await _notify(db, f"🆕 Nouveau ticket '{obj.titre or obj.description[:30]}' créé.")
    return schemas.MaintenanceTicketRead.model_validate(obj)



#  Assignation

@router.patch("/tickets/{ticket_id}/assigner", response_model=schemas.MaintenanceTicketRead)
async def assigner_ticket(ticket_id: int, payload: AssignPayload, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")

    obj.assigne_a = payload.assigne_a
    if obj.statut == "ouvert":
        obj.statut = "en_cours"

    await db.commit()
    await db.refresh(obj)
    await _notify(db, f"👷 Ticket #{obj.id} assigné à {obj.assigne_a}")
    return schemas.MaintenanceTicketRead.model_validate(obj)



#  Envoi du rapport

@router.patch("/tickets/{ticket_id}/report", response_model=schemas.MaintenanceTicketRead)
async def envoyer_rapport(ticket_id: int, payload: ReportPayload, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")
    if not payload.rapport or len(payload.rapport.strip()) < 5:
        raise HTTPException(400, "Le rapport doit être fourni.")

    _ensure_statut_transition(obj.statut, "rapport_envoye")
    obj.rapport = payload.rapport.strip()
    obj.rapport_fichier = payload.rapport_fichier
    obj.statut = "rapport_envoye"

    await db.commit()
    await db.refresh(obj)
    await _notify(db, f"📄 Rapport envoyé pour ticket #{obj.id}")
    return schemas.MaintenanceTicketRead.model_validate(obj)



#  Validation (ADMIN SEULEMENT)

@router.patch("/tickets/{ticket_id}/valider", response_model=schemas.MaintenanceTicketRead)
async def valider_ticket(ticket_id: int, payload: ValidatePayload, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.MaintenanceTicket, ticket_id)
    if not obj:
        raise HTTPException(404, "Ticket introuvable")

    user = await db.get(models.Utilisateur, payload.valide_par)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable")
    if user.role != "admin":
        raise HTTPException(403, "Seul un administrateur peut valider ce ticket.")

    _ensure_statut_transition(obj.statut, "termine")
    obj.valide_par = payload.valide_par
    obj.statut = "termine"

    await db.commit()
    await db.refresh(obj)
    await _notify(db, f"✅ Ticket #{obj.id} validé par {user.nom}")
    return schemas.MaintenanceTicketRead.model_validate(obj)


#  Dashboard (résumé)

@router.get("/dashboard")
async def dashboard_maintenance(db: AsyncSession = Depends(get_db)):
    tickets = (await db.execute(select(models.MaintenanceTicket))).scalars().all()
    total = len(tickets)
    if total == 0:
        return {"total": 0, "ouverts": 0, "en_cours": 0, "rapport_envoye": 0, "termines": 0, "urgents": 0, "mttr_h": 0}

    ouverts = sum(1 for t in tickets if t.statut == "ouvert")
    en_cours = sum(1 for t in tickets if t.statut == "en_cours")
    rapport_envoye = sum(1 for t in tickets if t.statut == "rapport_envoye")
    termines = sum(1 for t in tickets if t.statut == "termine")
    urgents = sum(1 for t in tickets if t.priorite == "urgente")

    return {
        "total": total,
        "ouverts": ouverts,
        "en_cours": en_cours,
        "rapport_envoye": rapport_envoye,
        "termines": termines,
        "urgents": urgents,
    }



#  Vérification automatique des maintenances préventives

async def verifier_maintenances_periodiques():
    """Tâche planifiée qui vérifie chaque jour les maintenances préventives à exécuter."""
    while True:
        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            stmt = select(models.MaintenanceTicket).where(
                models.MaintenanceTicket.type == "préventive",
                models.MaintenanceTicket.frequence_jours.isnot(None),
                models.MaintenanceTicket.prochaine_execution.isnot(None),
                models.MaintenanceTicket.prochaine_execution <= now,
            )
            plans = (await db.execute(stmt)).scalars().all()

            for plan in plans:
                nouveau = models.MaintenanceTicket(
                    titre=f"Exécution planifiée : {plan.titre or plan.description[:40]}",
                    description=plan.description,
                    type="préventive",
                    priorite=plan.priorite or "normale",
                    minigrid_id=plan.minigrid_id,
                    assigne_a=plan.assigne_a,
                    cree_par=plan.cree_par,
                    date_creation=now,
                    statut="ouvert",
                )
                db.add(nouveau)
                plan.prochaine_execution = now + timedelta(days=plan.frequence_jours)
                await _notify(db, f"🛠 Nouvelle exécution automatique du plan '{plan.titre}'")

            if plans:
                await db.commit()

        await asyncio.sleep(86400)  # exécution toutes les 24h


# Lancer la tâche planifiée au démarrage
asyncio.create_task(verifier_maintenances_periodiques())
