from pydantic import BaseModel
from typing import Optional

class ParametreBase(BaseModel):
    nom_plateforme: str
    langue: str

class ParametreCreate(ParametreBase):
    pass

class ParametreUpdate(BaseModel):
    nom_plateforme: Optional[str] = None
    langue: Optional[str] = None

class ParametreRead(ParametreBase):
    id: int

    class Config:
        orm_mode = True
