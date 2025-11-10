# app/schemas/minigrid.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# 🔹 Base commune
class MiniGridBase(BaseModel):
    site_id: int
    nom: str
    statut: Optional[str] = None

# 🔹 Création
class MiniGridCreate(MiniGridBase):
    pass

# 🔹 Mise à jour (patch)
class MiniGridUpdate(BaseModel):
    statut: Optional[str] = None
    nom: Optional[str] = None
    site_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# 🔹 Lecture
class MiniGridRead(MiniGridBase):
    id: int
    cree_le: Optional[datetime] = None
    maj_le: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
