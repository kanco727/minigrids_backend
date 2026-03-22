# app/schemas/alerte_minigrid.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ---------- Modèle de base ----------
class AlerteMinigridBase(BaseModel):
    minigrid_id: Optional[int] = None
    type_alerte: Optional[str] = None
    niveau: Optional[str] = None
    message: Optional[str] = None
    statut: Optional[str] = None
    time_stamp: Optional[datetime] = None
    time_resolution: Optional[datetime] = None


# ---------- Création ----------
class AlerteMinigridCreate(AlerteMinigridBase):
    pass


# ---------- Mise à jour ----------
class AlerteMinigridUpdate(AlerteMinigridBase):
    pass


# ---------- Lecture ----------
class AlerteMinigridRead(AlerteMinigridBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ---------- Liste enrichie avec nom du minigrid ----------
class AlerteMinigridListItem(BaseModel):
    id: int
    minigrid_id: int
    minigrid_nom: Optional[str] = None
    type_alerte: Optional[str] = None
    niveau: Optional[str] = None
    message: Optional[str] = None
    statut: Optional[str] = None
    time_stamp: Optional[datetime] = None
    time_resolution: Optional[datetime] = None