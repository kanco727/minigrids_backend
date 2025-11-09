from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# --- Schéma de base ---
class EquipementMinigridBase(BaseModel):
    minigrid_id: Optional[int] = None
    type_id: Optional[int] = None
    numero_serie: Optional[str] = None
    modele: Optional[str] = None
    date_installation: Optional[datetime] = None
    statut: Optional[str] = None


# --- Schéma de création et mise à jour ---
class EquipementMinigridCreate(EquipementMinigridBase):
    pass

class EquipementMinigridUpdate(EquipementMinigridBase):
    pass


# --- Schéma de lecture / sortie ---
class EquipementMinigridOut(EquipementMinigridBase):
    id: int
    cree_le: Optional[datetime] = None
    maj_le: Optional[datetime] = None

    class Config:
        orm_mode = True  # important : permet à FastAPI de convertir les objets SQLAlchemy
