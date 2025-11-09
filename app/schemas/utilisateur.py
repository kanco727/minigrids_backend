from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UtilisateurBase(BaseModel):
   # locataire_id: Optional[int] = None
    email: Optional[str] = None
    nom_complet: Optional[str] = None
    role: Optional[str] = None
    mfa_active: Optional[bool] = None
    dernier_login: Optional[datetime] = None

class UtilisateurCreate(UtilisateurBase): pass
class UtilisateurUpdate(UtilisateurBase): pass

class UtilisateurRead(UtilisateurBase):
    id: int
    cree_le: Optional[datetime] = None
    maj_le: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
