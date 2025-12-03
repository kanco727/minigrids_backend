from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------- Base ----------
class AlerteMinigridBase(BaseModel):
    minigrid_id: Optional[int] = None
    type_alerte: Optional[str] = None
    niveau: Optional[str] = None
    message: Optional[str] = None
    statut: Optional[str] = None
    time_stamp: Optional[datetime] = None


# ---------- CRUD ----------
class AlerteMinigridCreate(AlerteMinigridBase):
    categorie: Optional[str] = None
    valeur_mesuree: Optional[float] = None
    seuil_declenchement: Optional[float] = None
    origine: Optional[str] = "automatique"


class AlerteMinigridUpdate(AlerteMinigridBase):
    commentaire: Optional[str] = None
    responsable_id: Optional[int] = None


class AlerteMinigridRead(AlerteMinigridBase):
    id: int
    categorie: Optional[str] = None
    valeur_mesuree: Optional[float] = None
    seuil_declenchement: Optional[float] = None
    origine: Optional[str] = None
    responsable_id: Optional[int] = None
    commentaire: Optional[str] = None
    time_resolution: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Liste complète avec nom de mini-grid ----------
class AlerteMinigridListItem(BaseModel):
    id: int
    minigrid_id: int
    minigrid_nom: Optional[str] = None
    type_alerte: Optional[str] = None
    niveau: Optional[str] = None
    message: Optional[str] = None
    statut: Optional[str] = None
    time_stamp: Optional[datetime] = None


# ---------- Historique / timeline ----------
class AlerteHistoriqueRead(BaseModel):
    id: int
    alerte_id: int
    action: str
    acteur_id: Optional[int]
    details: Optional[str]
    time_action: datetime

    class Config:
        from_attributes = True


class AlerteHistoriqueCreate(BaseModel):
    action: str
    acteur_id: Optional[int] = None
    details: Optional[str] = None


# ---------- Actions complémentaires ----------
class AlerteAssignPayload(BaseModel):
    responsable_id: int
    commentaire: Optional[str] = None


class AlerteCommentPayload(BaseModel):
    commentaire: str


# ---------- Statistiques ----------
class AlerteStats(BaseModel):
    total: int
    critiques: int
    resolues: int
    temps_resolution_h: Optional[float] = None
