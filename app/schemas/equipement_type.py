from pydantic import BaseModel, ConfigDict
from typing import Optional

class EquipementTypeBase(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None

class EquipementTypeCreate(EquipementTypeBase): pass
class EquipementTypeUpdate(EquipementTypeBase): pass

class EquipementTypeRead(EquipementTypeBase):
    id: int

    class Config:
        orm_mode = True
