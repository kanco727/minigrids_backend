from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MaintenanceTicketBase(BaseModel):
    minigrid_id: Optional[int] = None
    equipement_id: Optional[int] = None
    alerte_id: Optional[int] = None

    titre: Optional[str] = None
    type: Optional[str] = None
    source_ticket: Optional[str] = None

    description: Optional[str] = None
    priorite: Optional[str] = None
    statut: Optional[str] = None

    date_creation: Optional[datetime] = None
    date_planifiee: Optional[datetime] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    date_validation: Optional[datetime] = None

    rapport: Optional[str] = None
    observation_technicien: Optional[str] = None

    cree_par: Optional[int] = None
    assigne_a: Optional[int] = None
    valide_par: Optional[int] = None

    cout_estime: Optional[Decimal] = None
    cout_reel: Optional[Decimal] = None
    duree_estimee_h: Optional[Decimal] = None
    duree_reelle_h: Optional[Decimal] = None


class MaintenanceTicketCreate(BaseModel):
    minigrid_id: int
    equipement_id: Optional[int] = None
    alerte_id: Optional[int] = None

    titre: str = Field(..., min_length=3, max_length=255)
    type: str = Field(default="corrective")
    source_ticket: Optional[str] = Field(default="manuel")

    description: str = Field(..., min_length=5)
    priorite: str = Field(default="moyenne")
    statut: str = Field(default="ouvert")

    date_planifiee: Optional[datetime] = None

    cree_par: Optional[int] = None
    assigne_a: Optional[int] = None

    cout_estime: Optional[Decimal] = None
    duree_estimee_h: Optional[Decimal] = None


class MaintenanceTicketUpdate(BaseModel):
    minigrid_id: Optional[int] = None
    equipement_id: Optional[int] = None
    alerte_id: Optional[int] = None

    titre: Optional[str] = Field(default=None, min_length=3, max_length=255)
    type: Optional[str] = None
    source_ticket: Optional[str] = None

    description: Optional[str] = Field(default=None, min_length=5)
    priorite: Optional[str] = None
    statut: Optional[str] = None

    date_planifiee: Optional[datetime] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    date_validation: Optional[datetime] = None

    rapport: Optional[str] = None
    observation_technicien: Optional[str] = None

    cree_par: Optional[int] = None
    assigne_a: Optional[int] = None
    valide_par: Optional[int] = None

    cout_estime: Optional[Decimal] = None
    cout_reel: Optional[Decimal] = None
    duree_estimee_h: Optional[Decimal] = None
    duree_reelle_h: Optional[Decimal] = None


class MaintenanceTicketRead(MaintenanceTicketBase):
    id: int
    cree_le: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)