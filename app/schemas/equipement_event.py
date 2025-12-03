# app/schemas/equipement_event.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class EquipementEventBase(BaseModel):
    type_event: str
    message: Optional[str] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    source: Optional[str] = "system"

class EquipementEventCreate(EquipementEventBase):
    pass

class EquipementEventRead(EquipementEventBase):
    id: int
    equipement_id: int
    horodatage: datetime

    model_config = ConfigDict(from_attributes=True)
