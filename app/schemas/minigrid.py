# app/schemas/minigrid.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# 🔹 Base commune
class MiniGridBase(BaseModel):
    site_id: int
    nom: str
    statut: Optional[str] = None

# 🔹 Pour la création
class MiniGridCreate(MiniGridBase):
    pass

# 🔹 Pour la mise à jour
class MiniGridUpdate(MiniGridBase):
    pass

# 🔹 Pour la lecture (ce que FastAPI renvoie)
class MiniGridRead(MiniGridBase):
    id: int
    cree_le: Optional[datetime] = None
    maj_le: Optional[datetime] = None

    # ✅ Nouvelle configuration Pydantic v2
    model_config = ConfigDict(from_attributes=True)
