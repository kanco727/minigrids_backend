from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


class MaintenanceAutoService:
    @staticmethod
    def should_create_ticket(alerte: models.AlerteMinigrid) -> bool:
        niveau = (alerte.niveau or "").lower()
        type_alerte = (alerte.type_alerte or "").lower()

        mots_cles = [
            "tension",
            "température",
            "temperature",
            "surcharge",
            "batterie",
            "onduleur",
            "hors ligne",
            "offline",
            "coupure",
            "defaut",
            "défaut",
            "erreur",
            "alarme",
        ]

        if niveau in ["critique", "haute", "urgent", "urgente"]:
            return True

        return any(mot in type_alerte for mot in mots_cles)

    @staticmethod
    def map_alert_to_ticket_type(type_alerte: str | None) -> str:
        text = (type_alerte or "").lower()

        if any(mot in text for mot in ["inspection", "controle", "contrôle", "nettoyage"]):
            return "preventive"

        if any(
            mot in text
            for mot in [
                "tension",
                "température",
                "temperature",
                "surcharge",
                "batterie",
                "onduleur",
                "hors ligne",
                "offline",
                "coupure",
                "defaut",
                "défaut",
                "erreur",
            ]
        ):
            return "corrective"

        return "corrective"

    @staticmethod
    def map_alert_to_priority(niveau: str | None) -> str:
        niveau = (niveau or "").lower()

        if niveau in ["critique", "critical"]:
            return "urgente"
        if niveau in ["haute", "high"]:
            return "haute"
        if niveau in ["moyenne", "medium", "moyen"]:
            return "moyenne"
        return "faible"

    @staticmethod
    async def existing_open_ticket(
        db: AsyncSession,
        alerte: models.AlerteMinigrid,
    ):
        stmt = (
            select(models.MaintenanceTicket)
            .where(models.MaintenanceTicket.minigrid_id == alerte.minigrid_id)
            .where(models.MaintenanceTicket.alerte_id == alerte.id)
            .where(
                models.MaintenanceTicket.statut.in_(
                    ["ouvert", "planifie", "en_cours", "rapport_envoye"]
                )
            )
            .order_by(models.MaintenanceTicket.id.desc())
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_ticket_from_alert(
        db: AsyncSession,
        alerte: models.AlerteMinigrid,
    ):
        if not MaintenanceAutoService.should_create_ticket(alerte):
            return None

        existing = await MaintenanceAutoService.existing_open_ticket(db, alerte)
        if existing:
            return existing

        ticket = models.MaintenanceTicket(
            minigrid_id=alerte.minigrid_id,
            alerte_id=alerte.id,
            titre=f"Intervention - {alerte.type_alerte}",
            type=MaintenanceAutoService.map_alert_to_ticket_type(alerte.type_alerte),
            source_ticket="alerte",
            description=alerte.message or f"Alerte détectée : {alerte.type_alerte}",
            priorite=MaintenanceAutoService.map_alert_to_priority(alerte.niveau),
            statut="ouvert",
        )

        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket