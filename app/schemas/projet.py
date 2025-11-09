from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ProjetBase(BaseModel):
    locataire_id: Optional[int] = None
    nom: Optional[str] = None
    pays: Optional[str] = None
    niveau_admin: Optional[int] = None
    visibilite_sur_carte: Optional[bool] = True
    style_carte_json: Optional[dict] = None  # JSONB -> dict côté API

class ProjetCreate(ProjetBase):
    pass

class ProjetUpdate(ProjetBase):
    pass

from typing import Any
import json

class ProjetRead(ProjetBase):
    id: int
    cree_le: Optional[datetime] = None
    maj_le: Optional[datetime] = None

    @classmethod
    def from_orm(cls, obj):
        data = super().from_orm(obj)
        # Convertir style_carte_json (str) en dict si besoin
        if isinstance(data.style_carte_json, str):
            try:
                data.style_carte_json = json.loads(data.style_carte_json)
            except Exception:
                data.style_carte_json = None
        return data

    class Config:
        orm_mode = True
