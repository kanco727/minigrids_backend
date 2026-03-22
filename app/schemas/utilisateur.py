from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from ..enums import RoleEnum

class UtilisateurBase(BaseModel):
    email: EmailStr
    nom_complet: str
    role: Optional[RoleEnum] = RoleEnum.TECHNICIEN

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class UtilisateurUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nom_complet: Optional[str] = None
    role: Optional[RoleEnum] = None
    actif: Optional[bool] = None

class UtilisateurRead(BaseModel):
    id: int
    email: str
    nom_complet: str
    role: str
    actif: bool
    date_creation: Optional[datetime] = None
    date_modification: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class UtilisateurLogin(BaseModel):
    email: EmailStr
    role: str
    id: int
    actif: bool
