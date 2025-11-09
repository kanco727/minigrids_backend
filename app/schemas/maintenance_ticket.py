# app/schemas/maintenance_ticket.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# 🔹 Modèle de base
class MaintenanceTicketBase(BaseModel):
    minigrid_id: Optional[int] = None
    alerte_id: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None
    date_creation: Optional[datetime] = None
    rapport: Optional[str] = None
    cree_par: Optional[int] = None
    assigne_a: Optional[int] = None
    valide_par: Optional[int] = None


# 🔹 Création
class MaintenanceTicketCreate(MaintenanceTicketBase):
    pass


# 🔹 Mise à jour
class MaintenanceTicketUpdate(MaintenanceTicketBase):
    pass


# 🔹 Lecture (réponse API)
class MaintenanceTicketRead(MaintenanceTicketBase):
    id: int
    cree_le: Optional[datetime] = None

    # ✅ Compatible Pydantic v2
    model_config = ConfigDict(from_attributes=True)
