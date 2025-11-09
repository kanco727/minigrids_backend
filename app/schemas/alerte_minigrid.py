# app/schemas/alerte_minigrid.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# ---------- Modèles CRUD standards ----------
class AlerteMinigridBase(BaseModel):
    minigrid_id: Optional[int] = None
    type_alerte: Optional[str] = None
    niveau: Optional[str] = None
    message: Optional[str] = None
    time_stamp: Optional[datetime] = None

class AlerteMinigridCreate(AlerteMinigridBase):
    pass

class AlerteMinigridUpdate(AlerteMinigridBase):
    pass

class AlerteMinigridRead(AlerteMinigridBase):
    id: int

    class Config:
        orm_mode = True  # nécessaire avec Pydantic v1 pour sérialiser des objets SQLAlchemy


# ---------- Modèle pour l’endpoint /alertes/full (avec nom de minigrid) ----------
class AlerteMinigridListItem(BaseModel):
    id: int
    minigrid_id: int
    minigrid_nom: Optional[str] = None
    type_alerte: Optional[str] = None
    niveau: Optional[str] = None
    message: Optional[str] = None
    time_stamp: Optional[datetime] = None
